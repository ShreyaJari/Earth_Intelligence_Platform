"""
Earth Intelligence Platform
Terrain Engine

Terrain Dataset Selection
"""


def select_dataset(catalog, terrain_product):
    """
    Select the preferred terrain dataset from the Earth Intelligence Catalog.

    Selection Criteria
    ------------------
    - Category = Terrain
    - Applicable = True
    - Highest Priority

    Parameters
    ----------
    catalog : dict
        Earth Intelligence Catalog.

    terrain_product : dict
        Terrain Product.

    Returns
    -------
    tuple
        Selected terrain dataset and updated Terrain Product.
    """

    terrain_datasets = [
        dataset
        for dataset in catalog["datasets"]
        if dataset["category"] == "Terrain" and dataset["applicable"]
    ]

    if len(terrain_datasets) == 0:

        raise ValueError("No applicable terrain datasets found.")

    priority_order = {"Primary": 1, "Secondary": 2}

    terrain_datasets = sorted(
        terrain_datasets,
        key=lambda dataset: priority_order.get(dataset["priority"], 99),
    )

    selected_dataset = terrain_datasets[0]

    terrain_product["dataset"] = {
        "id": selected_dataset["id"],
        "name": selected_dataset["name"],
        "provider": selected_dataset["provider"],
        "category": selected_dataset["category"],
        "stac_collection": selected_dataset["stac_collection"],
    }

    return selected_dataset, terrain_product
