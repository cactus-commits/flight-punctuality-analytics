import dlt
import pandas as pd

HEADERS = {"User-Agent": "eda-script/0.1"}


def _read_tables_with_iata(url: str) -> pd.DataFrame:
    # match= keeps only tables whose text contains "IATA"
    tables = pd.read_html(url, match="IATA", storage_options=HEADERS)

    cleaned = []
    for t in tables:
        # flatten MultiIndex headers if present
        if isinstance(t.columns, pd.MultiIndex):
            t.columns = [" ".join(map(str, c)).strip() for c in t.columns]
        # strip footnote markers like "IATA[1]" -> "IATA"
        t.columns = t.columns.astype(str).str.replace(r"\[.*?\]", "", regex=True).str.strip()
        cleaned.append(t)

    if not cleaned:
        raise ValueError(f"No tables with an IATA column found at {url}")
    return pd.concat(cleaned, ignore_index=True)


@dlt.resource(name="raw_wikipedia_airlines", write_disposition="replace")
def airline_codes_resource():
    yield _read_tables_with_iata("https://en.wikipedia.org/wiki/List_of_airline_codes")


@dlt.resource(name="raw_wikipedia_airports", write_disposition="replace")
def airport_codes_resource():
    yield _read_tables_with_iata("https://en.wikipedia.org/wiki/List_of_international_airports_by_country")

# Group the two resources into one dlt source.
# The function name becomes the source name, which is part of the asset keys (for dagster).
@dlt.source
def wikipedia_source():
    # Return both resources so they are loaded together
    return airline_codes_resource(), airport_codes_resource()