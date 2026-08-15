def discovery_assessment(catalog, aoi):
    """
    Evaluate dataset applicability for the AOI.
    """

    for dataset in catalog["datasets"]:

        if dataset["coverage"] == "Global":
            dataset["applicable"] = True

        else:
            dataset["applicable"] = False

    return catalog
