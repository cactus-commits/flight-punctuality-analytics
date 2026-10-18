"""Flight punctuality dashboard: delayed arrivals and departures at Swedish airports.

Run from the repo root: uv run streamlit run streamlit_app/app.py
Reads mart_arrivals_info and mart_departures_info in Snowflake (swedavia_db.mart).
"""

import altair as alt
import pandas as pd
import snowflake.connector
import streamlit as st

DELAY_THRESHOLD_MIN = 15  # same threshold as the marts (is_delayed)
MIN_FLIGHTS_IN_RANKING = 5  # hide airlines/airports with too few flights from rankings

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

st.set_page_config(page_title="Flight punctuality", page_icon="✈️", layout="wide")


@st.cache_resource
def get_connection():
    return snowflake.connector.connect(**st.secrets["snowflake"])


@st.cache_data(ttl=600)
def load_flights() -> pd.DataFrame:
    cur = get_connection().cursor()
    try:
        cur.execute(QUERY)
        df = pd.DataFrame(cur.fetchall(), columns=[c[0].lower() for c in cur.description])
    finally:
        cur.close()
    df["date"] = pd.to_datetime(df["date"])
    df["delay_minutes"] = pd.to_numeric(df["delay_minutes"])
    df["is_delayed"] = df["is_delayed"].astype("boolean")  # null = not landed/departed yet
    df["cancelled"] = df["flight_status"] == "Cancelled"
    return df


def summarize(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    """Flights, measured flights (have an actual time) and delay share per group."""
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
    out["pct_delayed"] = (out["delayed"] / out["measured"]).where(out["measured"] > 0) * 100
    return out


AXIS_TITLES = {"pct_delayed": "Share delayed (% of flights)", "delayed": "Delayed flights (number)"}

HELP_DELAYED = f"Number of flights that were {DELAY_THRESHOLD_MIN} minutes or more later than scheduled."
HELP_SHARE = (
    "Delayed flights divided by flights that have an actual time. "
    "Cancelled flights and flights that have not landed or departed yet are left out of the share."
)


def ranking_chart(data: pd.DataFrame, category: str, metric: str, title: str):
    return (
        alt.Chart(data, title=title)
        .mark_bar()
        .encode(
            x=alt.X(metric, title=AXIS_TITLES[metric]),
            y=alt.Y(category, sort="-x", title=None),
            color=alt.Color("direction", title="Direction"),
            yOffset="direction",
            tooltip=[category, "direction", "flights", "delayed", alt.Tooltip("pct_delayed", format=".1f")],
        )
    )


try:
    flights = load_flights()
except Exception as e:  # missing secrets, wrong credentials, no network
    st.error(f"Could not load data from Snowflake: {e}")
    st.info("Copy .streamlit/secrets.toml.example to .streamlit/secrets.toml and fill in your credentials.")
    st.stop()

st.title("✈️ Flight punctuality at Swedish airports")
st.caption(
    f"A flight counts as delayed when it is {DELAY_THRESHOLD_MIN}+ min later than scheduled. "
    "Flights without an actual time yet, and cancelled flights, are counted as flights but left out of the delay share."
)

# ---- Filters
with st.sidebar:
    st.header("Filters")
    min_d, max_d = flights["date"].min().date(), flights["date"].max().date()
    date_range = st.date_input("Date", (min_d, max_d), min_value=min_d, max_value=max_d)
    directions = st.multiselect("Direction", ["Arrival", "Departure"], default=["Arrival", "Departure"])
    airports = st.multiselect("Airport", sorted(flights["airport"].dropna().unique()))
    airlines = st.multiselect("Airline", sorted(flights["airline_name"].dropna().unique()))
    if st.button("Refresh data"):
        st.cache_data.clear()
        st.rerun()

start, end = (date_range if len(date_range) == 2 else (date_range[0], date_range[0]))
df = flights[flights["date"].between(pd.Timestamp(start), pd.Timestamp(end)) & flights["direction"].isin(directions)]
if airports:
    df = df[df["airport"].isin(airports)]
if airlines:
    df = df[df["airline_name"].isin(airlines)]

if df.empty:  # also covers no direction selected
    st.warning("No flights match the filters.")
    st.stop()

# ---- KPIs: arrivals vs departures
st.subheader("Arrivals vs departures")
kpi_cols = st.columns(len(directions))
for col, direction in zip(kpi_cols, directions):
    icon = "🛬" if direction == "Arrival" else "🛫"
    d = df[df["direction"] == direction]
    with col.container(border=True):
        st.markdown(f"### {icon} {direction}s")
        if d.empty:
            st.write("No flights match the filters.")
            continue
        t = summarize(d.assign(all="all"), ["all"]).iloc[0]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Flights", f"{int(t.flights):,}")
        m2.metric("Delayed", f"{int(t.delayed):,}", help=HELP_DELAYED)
        m3.metric("Share delayed", "–" if pd.isna(t.pct_delayed) else f"{t.pct_delayed:.1f}%", help=HELP_SHARE)
        m4.metric("Cancelled", f"{int(t.cancelled):,}", help="Flights with status Cancelled.")

# ---- By date
st.subheader("Delays by date")
by_date = summarize(df, ["date", "direction"])
st.altair_chart(
    alt.Chart(by_date)
    .mark_bar()
    .encode(
        x=alt.X("date:T", title=None, timeUnit="yearmonthdate"),
        y=alt.Y("delayed:Q", title=AXIS_TITLES["delayed"]),
        color=alt.Color("direction", title="Direction"),
        xOffset="direction",
        tooltip=["date", "direction", "flights", "delayed", alt.Tooltip("pct_delayed", format=".1f")],
    ),
    width="stretch",
)

# ---- By airline / airport
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
    st.caption("Counts favour the airlines and airports with the most flights. Use share delayed to compare punctuality.")
else:
    st.caption(f"Only airlines and airports with at least {MIN_FLIGHTS_IN_RANKING} measured flights per direction are shown.")

left, right = st.columns(2)
for col, field, label in ((left, "airline_name", "airline"), (right, "airport", "airport")):
    s = summarize(df, [field, "direction"])
    if metric == "pct_delayed":  # shares from tiny samples are misleading
        s = s[s["measured"] >= MIN_FLIGHTS_IN_RANKING]
    # order by the combined value of both directions, so one airline/airport stays together
    total = s.groupby(field)[["delayed", "measured"]].sum()
    total["pct_delayed"] = total["delayed"] / total["measured"] * 100
    order = total[metric].nlargest(top_n).index
    s = s[s[field].isin(order)]
    col.altair_chart(ranking_chart(s, field, metric, f"By {label}"), width="stretch")

with st.expander("Data"):
    st.dataframe(summarize(df, ["airline_name", "airport", "direction"]).sort_values("delayed", ascending=False), width="stretch")
    st.caption("avg_delay_min is the average of actual minus scheduled time, so early flights make it lower or negative.")
