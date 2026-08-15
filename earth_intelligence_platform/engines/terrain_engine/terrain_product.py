"""
Earth Intelligence Platform
Terrain Engine

Standard Terrain Product
"""


def create_terrain_product():
    """
    Create an empty standardized Terrain Product.

    Returns
    -------
    dict
        Empty Terrain Product.
    """

    return {
        "success": False,
        "errors": [],
        "warnings": [],
        "dataset": None,
        "dem": None,
        "metadata": {},
        "products": {},
        "statistics": {},
        "processing": {},
    }
