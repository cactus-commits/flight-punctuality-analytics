# flight-punctuality-analytics
A data pipeline and dashboard for analyzing flight delays at Swedish airports.

## Known data limitations

About 3–8% of flights have an airline or airport that is not in the Wikipedia reference lists, so they show as `Unknown` in the marts. Swedavia often gives only an ICAO code for airlines (e.g. JON, FRO), while the Wikipedia list is matched on IATA. Some foreign airports and placeholder codes (e.g. AGH, SFT, ZZZ) are also missing, and show as `Unknown` on the other end of the flight. Swedavia airports that are missing from the Wikipedia list (Ronneby and Kiruna) are added in `data_transformation/dbt_flights/seeds/missing_airports.csv`.
