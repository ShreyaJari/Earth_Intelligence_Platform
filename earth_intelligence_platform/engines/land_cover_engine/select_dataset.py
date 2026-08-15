"""
select_dataset.py

Dataset selection for the Land Cover Engine.
"""


def select_dataset(catalog, landcover_product):
    """
    Select the highest-priority applicable land cover dataset.

    Parameters
    ----------
    catalog : dict
        Earth Intelligence Catalog, containing a "datasets" list.

    landcover_product : dict
        Land cover product dictionary.

    Returns
    -------
    tuple
        (selected_dataset, landcover_product)

    Raises
    ------
    ValueError
        If no suitable dataset is found.
    """

    candidates = [
        dataset
        for dataset in catalog["datasets"]
        if (
            dataset.get("category") == "Land Cover" and dataset.get("applicable", False)
        )
    ]

    if not candidates:

        raise ValueError("No applicable land cover datasets found.")

    selected_dataset = min(
        candidates, key=lambda dataset: dataset.get("priority", float("inf"))
    )

    landcover_product["dataset"] = selected_dataset

    return selected_dataset, landcover_product
