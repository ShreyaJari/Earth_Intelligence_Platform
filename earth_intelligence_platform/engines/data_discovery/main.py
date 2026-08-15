from .build_catalog import build_catalog
from .discovery_assessment import discovery_assessment


def run_data_discovery_engine(aoi):
    """
    Run the Data Discovery Engine.
    """

    catalog = build_catalog()

    catalog = discovery_assessment(
        catalog,
        aoi,
    )

    return catalog
