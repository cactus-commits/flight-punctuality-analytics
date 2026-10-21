"""Flight punctuality dashboard: delayed arrivals and departures at Swedish airports.

Run from the repo root: uv run streamlit run streamlit_app/app.py
Reads mart_arrivals_info and mart_departures_info in Snowflake (swedavia_db.mart).
"""

import os
import altair as alt
import pandas as pd
import snowflake.connector
import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # reads .env when run locally; in Docker the variables already come from env_file

DELAY_THRESHOLD_MIN = 15  # same threshold as the marts (is_delayed)
MIN_FLIGHTS_IN_RANKING = 5  # hide airlines/airports with too few flights from rankings

# Combines arrivals and departures into one table so the dashboard can filter and compare both.
# "airport" is always the Swedish side: arrival airport for arrivals, departure airport for departures.
QUERY = """
select 'Arrival' as direction, airline_name, arrival_airport_name as airport,
       date, flight_status, delay_minutes, is_delayed
from mart_arrivals_info
union all
select 'Departure', airline_name, departure_airport_name,
       date, flight_status, delay_minutes, is_delayed
from mart_departures_info
"""

st.set_page_config(page_title="Flight punctuality",
                   page_icon="✈️", layout="wide")


def _connection_is_alive(conn) -> bool:
    # Snowflake session tokens expire after a while, so a cached connection can go stale.
    # A cheap query tells us; if it fails, Streamlit drops the connection and reconnects.
    try:
        conn.cursor().execute("select 1").close()
        return True
    except snowflake.connector.Error:
        return False


@st.cache_resource(validate=_connection_is_alive)
def get_connection():
    # Creates one Snowflake connection and reuses it across app reruns.
    # secrets from environment variables, the rest is not secret (same setup as profiles.yml)
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("DESTINATION__SNOWFLAKE__CREDENTIALS__USERNAME"),
        password=os.getenv("SNOWFLAKE_USER_TRANSFORMER_PASSWORD"),
        role=os.getenv("DESTINATION__SNOWFLAKE__CREDENTIALS__ROLE"),
        warehouse=os.getenv("DESTINATION__SNOWFLAKE__CREDENTIALS__WAREHOUSE"),
        database=os.getenv("DESTINATION__SNOWFLAKE__CREDENTIALS__DATABASE"),
        schema=os.getenv("DASHBOARD_SCHEMA"),
        client_session_keep_alive=True,  # keeps the session token fresh while the app is open
    )


@st.cache_data(ttl=600)
def load_flights() -> pd.DataFrame:
    # Runs the query, loads the result into a DataFrame and cleans up data types.
    # The result is cached for 10 minutes to avoid hitting Snowflake on every interaction.
    cur = get_connection().cursor()
    try:
        cur.execute(QUERY)
        df = pd.DataFrame(cur.fetchall(), columns=[
                          c[0].lower() for c in cur.description])
    finally:
        cur.close()
    df["date"] = pd.to_datetime(df["date"])
    df["delay_minutes"] = pd.to_numeric(df["delay_minutes"])
    df["is_delayed"] = df["is_delayed"].astype(
        "boolean")  # null = not landed/departed yet
    df["airport"] = df["airport"].str.replace(
        r"\s+Airport$", "", regex=True)  # shorter chart labels
    df["cancelled"] = df["flight_status"] == "Cancelled"
    return df


def summarize(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    """Flights, measured flights (have an actual time) and delay share per group."""
    # Core aggregation used by the KPIs, charts and tables: groups the flights
    # and counts total, measured, delayed and cancelled flights, plus average delay and share delayed.
    out = (
        df.groupby(by, dropna=False)
        .agg(
            flights=("is_delayed", "size"),
            measured=("is_delayed", "count"),
            delayed=("is_delayed", "sum"),
            cancelled=("cancelled", "sum"),
            avg_delay_min=("delay_minutes", "mean"),
        )
        .reset_index()
    )
    out[["delayed", "cancelled"]] = out[["delayed", "cancelled"]].astype(int)
    out["pct_delayed"] = (out["delayed"] / out["measured"]
                          ).where(out["measured"] > 0) * 100
    return out


# ---- Chart settings: colours, axis format and help texts shared by the charts

# neutral blues so neither direction draws attention like red/orange would
DIRECTION_COLORS = alt.Scale(
    domain=["Arrival", "Departure"], range=["#2f6f8f", "#9db8c8"])

# delayed vs on time (date chart only); direction colours are used by the ranking charts
STATUS_COLORS = alt.Scale(domain=["Delayed", "On time"], range=[
                          "#E4572E", "#BFC5CC"])
# a day is partial if more than 5% of its non-cancelled flights have no actual time yet
PARTIAL_DAY_SHARE = 0.05
# whole numbers for flight counts
COUNT_AXIS = alt.Axis(tickMinStep=1, format="d")

AXIS_TITLES = {
    "pct_delayed": "Share delayed (%)", "delayed": "Delayed flights"}

HELP_DELAYED = f"Number of flights that were {DELAY_THRESHOLD_MIN} minutes or more later than scheduled."
HELP_SHARE = (
    "Delayed flights divided by flights that have an actual time. "
    "Cancelled flights and flights that have not landed or departed yet are left out of the share."
)


def date_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Per direction and date: delayed / on-time counts and whether the day is still incomplete."""
    # Builds the data behind the date charts: summarizes per direction and day,
    # flags days that are not finished yet, and creates readable x-axis labels.
    stats = summarize(df, ["direction", "date"])
    non_cancelled = stats["flights"] - stats["cancelled"]
    no_actual = non_cancelled - stats["measured"]
    stats["partial"] = (
        no_actual / non_cancelled).where(non_cancelled > 0, 0) > PARTIAL_DAY_SHARE
    stats["on_time"] = stats["measured"] - stats["delayed"]
    stats["label"] = [
        f"{d:%a} {d.day} {d:%b}" + (" (partial)" if p else "") for d, p in zip(stats["date"], stats["partial"])
    ]
    return stats.sort_values("date")


def date_chart(stats: pd.DataFrame, y_max: float):
    """Stacked bars for one direction: delayed at the bottom, on time on top, share delayed above each bar."""
    # Reshapes the data to long format, draws the stacked bars (faded for partial days)
    # and adds a text label with the share delayed on top of each bar.
    long = stats.melt(
        id_vars=["label", "date", "measured", "pct_delayed", "partial"],
        value_vars=["delayed", "on_time"],
        var_name="status",
        value_name="count",
    )
    long["status"] = long["status"].map(
        {"delayed": "Delayed", "on_time": "On time"})
    long["stack_order"] = long["status"].map(
        {"Delayed": 0, "On time": 1})  # lowest is stacked first (bottom)
    x = alt.X("label:O", sort=stats["label"].tolist(
    ), title=None, axis=alt.Axis(labelAngle=0))
    y_scale = alt.Scale(domain=[0, y_max])
    bars = (
        alt.Chart(long)
        .mark_bar()
        .encode(
            x=x,
            y=alt.Y("count:Q", title="Flights",
                    scale=y_scale, axis=COUNT_AXIS),
            color=alt.Color("status:N", scale=STATUS_COLORS, legend=None),
            order=alt.Order("stack_order:Q"),
            opacity=alt.condition(
                alt.datum.partial, alt.value(0.45), alt.value(1)),
            tooltip=[
                alt.Tooltip("label:O", title="Date"),
                alt.Tooltip("status:N", title="Status"),
                alt.Tooltip("count:Q", title="Flights"),
                alt.Tooltip("measured:Q", title="Flights measured"),
                alt.Tooltip("pct_delayed:Q",
                            title="Share delayed (%)", format=".1f"),
            ],
        )
    )
    labels = (
        alt.Chart(stats[stats["measured"] > 0].assign(
            text=lambda d: d["pct_delayed"].round().astype(int).astype(str) + "%"))
        .mark_text(baseline="bottom", dy=-3, color="#374151")
        .encode(x=x, y=alt.Y("measured:Q", scale=y_scale), text="text:N")
    )
    return bars + labels


def ranking_chart(data: pd.DataFrame, category: str, metric: str, title: str, average: float | None = None):
    # Draws horizontal bars per airport or airline, with one bar per direction.
    # When an average is given, a dashed line with a label is added for comparison.
    bars = (
        alt.Chart(data, title=title)
        .mark_bar()
        .encode(
            x=alt.X(metric, title=AXIS_TITLES[metric],
                    axis=COUNT_AXIS if metric == "delayed" else alt.Axis()),
            y=alt.Y(category, sort="-x", title=None,
                    axis=alt.Axis(labelLimit=250)),
            color=alt.Color("direction", scale=DIRECTION_COLORS, legend=None),
            yOffset="direction",
            tooltip=[category, "direction", "flights", "delayed",
                     alt.Tooltip("pct_delayed", format=".1f")],
        )
    )
    if average is None:
        return bars
    ref = pd.DataFrame({"average": [average], "label": [
                       f"Average {average:.1f}%"]})
    rule = alt.Chart(ref).mark_rule(color="#374151", strokeDash=[
        5, 4], size=2).encode(x="average:Q")
    text = (
        alt.Chart(ref)
        .mark_text(align="left", dx=4, dy=-4, baseline="bottom", color="#374151", fontWeight="bold")
        .encode(x="average:Q", y=alt.value(0), text="label")
    )
    return bars + rule + text


# ---- Load data: show an error and stop the app if Snowflake can't be reached
try:
    flights = load_flights()
except Exception as e:  # missing secrets, wrong credentials, no network
    st.error(f"Could not load data from Snowflake: {e}")
    st.info("Set SNOWFLAKE_ACCOUNT and SNOWFLAKE_USER_TRANSFORMER_PASSWORD in .env (see .env.example).")
    st.stop()

st.title("✈️ Flight punctuality at Swedish airports")
st.caption(
    f"A flight counts as delayed when it is {DELAY_THRESHOLD_MIN}+ min later than scheduled. "
    "Flights without an actual time yet, and cancelled flights, are counted as flights but left out of the delay share."
)

# ---- Filters: sidebar controls, then the filters are applied to the data.
# Empty airport/airline selections mean "all".
with st.sidebar:
    st.header("Filters")
    min_d, max_d = flights["date"].min().date(), flights["date"].max().date()
    date_range = st.date_input(
        "Date", (min_d, max_d), min_value=min_d, max_value=max_d)
    directions = st.multiselect("Direction", ["Arrival", "Departure"], default=[
                                "Arrival", "Departure"])
    airports = st.multiselect("Airport", sorted(
        flights["airport"].dropna().unique()))
    airlines = st.multiselect("Airline", sorted(
        flights["airline_name"].dropna().unique()))
    if st.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()

start, end = (date_range if len(date_range) ==
              2 else (date_range[0], date_range[0]))
df = flights[flights["date"].between(pd.Timestamp(
    start), pd.Timestamp(end)) & flights["direction"].isin(directions)]
if airports:
    df = df[df["airport"].isin(airports)]
if airlines:
    df = df[df["airline_name"].isin(airlines)]

if df.empty:  # also covers no direction selected
    st.warning("No flights match the filters.")
    st.stop()

# ---- KPIs: arrivals vs departures
# One box per selected direction showing the number of delays and the share of flights delayed.
st.subheader("Arrivals vs departures")
kpi_cols = st.columns(len(directions))
for col, direction in zip(kpi_cols, directions):
    icon = "🛬" if direction == "Arrival" else "🛫"
    d = df[df["direction"] == direction]
    with col.container(border=True):
        if d.empty:
            st.write(f"{icon} {direction}s: no flights match the filters.")
            continue
        t = summarize(d.assign(all="all"), ["all"]).iloc[0]
        share = "–" if pd.isna(t.pct_delayed) else f"{t.pct_delayed:.1f}%"
        st.metric(
            f"{icon} {direction}s",
            f"{int(t.delayed):,} {'delay' if t.delayed == 1 else 'delays'}",
            help=f"{HELP_DELAYED}\n\nShare delayed: {HELP_SHARE}",
        )
        st.write(
            f"{share} of {int(t.flights):,} flights · {int(t.cancelled):,} cancelled (not included in share)")

# ---- By date: one chart per direction, delayed vs on time
# Includes a manual colour legend and draws the charts side by side.
st.subheader("Delays by date")
st.markdown(
    '<small><span style="color:#E4572E;font-size:1.2em">●</span> Delayed (15+ min late) &nbsp;&nbsp;'
    '<span style="color:#BFC5CC;font-size:1.2em">●</span> On time (less than 15 min late) &nbsp;&nbsp;'
    "Labels show the share delayed. Faded bars are days that are not finished yet.</small>",
    unsafe_allow_html=True,
)
stats = date_stats(df)
# same scale in both charts, headroom for the share label
y_max = stats["measured"].max() * 1.12
for col, direction in zip(st.columns(len(directions)), directions):
    with col:
        st.markdown(f"**{direction}s**")
        st.altair_chart(date_chart(
            stats[stats["direction"] == direction], y_max), width="stretch")

# ---- By airline / airport
# The user picks how to rank (share or count) and how many to show.
# Then one ranking chart is drawn for airports and one for airlines.
st.subheader("Delays by airline and airport")
metric_label = st.radio(
    "Rank by",
    ["Share delayed (%)", "Delayed flights"],
    horizontal=True,
    help=f"Share delayed: {HELP_SHARE}\n\nDelayed flights: {HELP_DELAYED}",
)
metric = "pct_delayed" if metric_label.startswith("Share") else "delayed"
top_n = st.slider("Show top", 5, 30, 10)
if metric == "delayed":
    st.caption(
        "Counts favour the airlines and airports with the most flights. Use share delayed to compare punctuality.")
else:
    st.caption(
        f"Only airlines and airports with at least {MIN_FLIGHTS_IN_RANKING} measured flights per direction are shown. "
        "The dashed line is the average share delayed for all flights in the current filter: bars to its right are worse than normal."
    )

legend_html = "".join(
    f'<span style="color:{color};font-size:1.2em">●</span> {name} &nbsp;&nbsp;'
    for name, color in zip(DIRECTION_COLORS.domain, DIRECTION_COLORS.range)
)
st.markdown(
    f"<small>Chart colours: {legend_html}</small>", unsafe_allow_html=True)

overall_pct = summarize(df.assign(all="all"), ["all"]).iloc[0].pct_delayed
# airports first and wider: the airport authority's main interest
left, right = st.columns([3, 2])
for col, field, label in ((left, "airport", "airport"), (right, "airline_name", "airline")):
    s = summarize(df, [field, "direction"])
    if metric == "pct_delayed":  # shares from tiny samples are misleading
        s = s[s["measured"] >= MIN_FLIGHTS_IN_RANKING]
    # order by the combined value of both directions, so one airline/airport stays together
    total = s.groupby(field)[["delayed", "measured"]].sum()
    total["pct_delayed"] = total["delayed"] / total["measured"] * 100
    order = total[metric].nlargest(top_n).index
    s = s[s[field].isin(order)]
    average = overall_pct if metric == "pct_delayed" and pd.notna(
        overall_pct) else None
    col.altair_chart(ranking_chart(s, field, metric,
                     f"By {label}", average), width="stretch")

# ---- Raw numbers: collapsible table with the underlying data
with st.expander("Data"):
    st.dataframe(summarize(df, ["airline_name", "airport", "direction"]).sort_values(
        "delayed", ascending=False), width="stretch")
    st.caption(
        "avg_delay_min is the average of actual minus scheduled time, so early flights make it lower or negative.")
