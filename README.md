# flight-punctuality-analytics
A data pipeline and dashboard for analyzing flight delays at Swedish airports.

## Known data limitations

About 3–8% of flights have an airline or airport that is not in the Wikipedia reference lists, so they show as `Unknown` in the marts. Swedavia often gives only an ICAO code for airlines (e.g. JON, FRO), while the Wikipedia list is matched on IATA. Some small airports and placeholder codes (e.g. RNB, KRN, ZZZ) are also missing.

## Dashboard metrics

- **Delay**: actual time minus scheduled time, in minutes. A flight that is 5 minutes early has a delay of -5.
- **Delayed flight**: a flight that is 15 minutes or more late.
- **Share delayed**: delayed flights divided by flights that have an actual time. Flights that have not landed or departed yet, and cancelled flights, are left out of the share but still count in the flight total.
- **Avg delay**: the average delay of those flights. It can be negative or close to zero because early flights pull the average down, so use share delayed to judge punctuality.
