import dlt # dlt library, used to define the pipeline
import dagster as dg # Dagster core (assets, execution context)
from dagster_dlt import DagsterDltResource, dlt_assets # Dagster <-> dlt integration

# Import our own dlt sources from the data_load_extract package.
# SWE_AIRPORTS and DATES are the airport dict and date list in get_swedavia_data.py
from data_load_extract.get_swedavia_data import flights_source, SWE_AIRPORTS, DATES
from data_load_extract.get_wikipedia_data import wikipedia_source


# ---------------------------------------------------------------
# dlt resource
# ---------------------------------------------------------------
# Lets Dagster run dlt pipelines. It must be registered in Definitions
# under the key "dlt" so Dagster can inject it into the functions below.
dlt_resource = DagsterDltResource()

# ---------------------------------------------------------------
# Swedavia assets (arrivals + departures)
# ---------------------------------------------------------------

@dlt_assets(
    # The dlt source that contains the arrivals and departures resources
    # flights_source needs two arguments: the airport codes and the dates.
    dlt_source=flights_source(list(SWE_AIRPORTS.keys()), DATES),
    # The pipeline that loads the data into Snowflake, schema "staging"
    dlt_pipeline=dlt.pipeline(
        pipeline_name="swedavia",
        destination="snowflake",
        dataset_name="staging"
    ),
    # Unique name, needed because we have more than one @dlt_assets in the project
    name="swedavia",
    # Groups the assets together in the Dagster UI
    group_name="extract_load",    
)
def swedavia_dlt_assets(context: dg.AssetExecutionContext, dlt: DagsterDltResource):
    # `context` and `dlt` are injected by Dagster at run time.
    # dlt.run() executes the pipeline and reports each loaded table
    # to Dagster as a materialized asset.
    yield from dlt.run(context=context)


# ---------------------------------------------------------------
# Wikipedia assets (airlines + airports)
# ---------------------------------------------------------------
@dlt_assets(
    dlt_source=wikipedia_source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="wikipedia",
        destination="snowflake",
        dataset_name="staging",
    ),
    name="wikipedia",
    group_name="extract_load",
)
def wikipedia_dlt_assets(context: dg.AssetExecutionContext, dlt: DagsterDltResource):
    # Same pattern as above, but for the Wikipedia source
    yield from dlt.run(context=context)