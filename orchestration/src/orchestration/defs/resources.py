# ---------------------------------------------------------------
# Resources
# Registers the resources that the assets depend on. Dagster uses
# the key (e.g. "dlt") to match the parameter name in the asset
# functions and injects the right resource at run time.
# ---------------------------------------------------------------

# orchestration/src/orchestration/defs/resources.py
import dagster as dg
# Reuse the resource instance we created in dlt_assets.py
from orchestration.defs.assets.dlt_assets import dlt_resource


# @dg.definitions tells Dagster's auto-discovery to pick up this function.
# Resources are NOT found automatically from module-level variables,
# so we register them explicitly here.
@dg.definitions
def resources() -> dg.Definitions:
    return dg.Definitions(
        # The key "dlt" must match the parameter name `dlt` in the
        # asset functions (dependency injection by name).
        resources={"dlt": dlt_resource},
    )