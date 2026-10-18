# flight-punctuality-analytics
A data pipeline and dashboard for analyzing flight delays at Swedish airports.

## Known data limitations

About 3–8% of flights have an airline or airport that is not in the Wikipedia reference lists, so they show as `Unknown` in the marts. Swedavia often gives only an ICAO code for airlines (e.g. JON, FRO), while the Wikipedia list is matched on IATA. Some small airports and placeholder codes (e.g. RNB, KRN, ZZZ) are also missing.
