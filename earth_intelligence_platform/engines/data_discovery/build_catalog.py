from datetime import datetime

from .dataset_registry import dataset_registry


def build_catalog():
    """
    Build the Earth Intelligence Catalog.
    """

    catalog = {
        "metadata": {
            "engine": "Data Discovery Engine",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
        },
        "datasets": [],
    }

    catalog["datasets"].extend(dataset_registry)

    return catalog
