"""
select_dataset.py

Select the best available weather dataset.
"""


def select_dataset(
    catalog,
    weather_product,
):
    """
    Select the highest-priority applicable weather dataset.

    Parameters
    ----------
    catalog : dict
        Earth Intelligence Catalog, containing a "datasets" list.

    weather_product : dict

    Returns
    -------
    tuple
        (selected_dataset, weather_product)
    """

    candidates = [
        dataset
        for dataset in catalog["datasets"]
        if (dataset["category"] == "Weather" and dataset["applicable"])
    ]

    if not candidates:

        raise ValueError("No applicable weather datasets found.")

    selected_dataset = min(
        candidates,
        key=lambda dataset: dataset["priority"],
    )

    weather_product["dataset"] = selected_dataset

    return (
        selected_dataset,
        weather_product,
    )
