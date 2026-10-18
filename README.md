# flight-punctuality-analytics
A data pipeline and dashboard for analyzing flight delays at Swedish airports.

## Known data limitations

About 3–8% of flights have an airline or airport that is not in the Wikipedia reference lists, so they show as `Unknown` in the marts. Swedavia often gives only an ICAO code for airlines (e.g. JON, FRO), while the Wikipedia list is matched on IATA. Some small airports and placeholder codes (e.g. RNB, KRN, ZZZ) are also missing.

## Dashboard

A Streamlit app that reads the two marts (`mart_arrivals_info`, `mart_departures_info`) in Snowflake.

Run it from the repo root:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then fill in your Snowflake credentials
uv run streamlit run streamlit_app/app.py
```

What it shows:

- **Arrivals vs departures**: one box per direction. The number of delays comes first, with share delayed, number of flights and number of cancelled flights underneath.
- **Delays by date**: one chart per direction. Orange bars are delayed flights (at the bottom), grey bars are flights that were not delayed. The percentage above each bar is the share delayed that day. Both charts use the same y-axis. Days that are not finished yet (more than 5% of their non-cancelled flights have no actual time) are faded and marked "(partial)".
- **Delays by airport and airline**: rankings, airports first. The default is share delayed, because counts mainly show which airports and airlines have the most flights. The dashed line is the average share delayed for all flights in the current filter, so bars to its right are worse than normal. Airports and airlines with fewer than 5 measured flights per direction are left out of the share ranking.
- **Filters** in the sidebar: date, direction, airport and airline.
- **Data**: an expandable table with the numbers behind the charts.

The airport charts show the Swedish side of each flight: the arrival airport for arrivals and the departure airport for departures.

### Metrics

- **Delay**: actual time minus scheduled time, in minutes. A flight that is 5 minutes early has a delay of -5.
- **Delayed flight**: a flight that is 15 minutes or more late. Everything else that has an actual time counts as on time.
- **Share delayed**: delayed flights divided by flights that have an actual time. Flights that have not landed or departed yet, and cancelled flights, are left out of the share but still count in the flight total.
- **Cancelled**: flights with status Cancelled. They are shown as a number and never counted as delayed or on time.
- **Avg delay** (in the data table): the average delay of measured flights. It can be negative or close to zero because early flights pull the average down, so use share delayed to judge punctuality.
