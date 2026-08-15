"""
resolve_city.py

Resolves ambiguous city search results.

Project: Earth Intelligence Platform
"""

import geopandas as gpd


def resolve_city(matches: gpd.GeoDataFrame):
    """
    Resolve multiple matching cities by asking the user to select one.

    Parameters
    ----------
    matches : GeoDataFrame
        Search results returned by GHSCityDatabase.search().

    Returns
    -------
    pandas.Series
        The selected city record.
    """

    if len(matches) == 0:
        raise ValueError("No matching cities found.")

    if len(matches) == 1:
        return matches.iloc[0]

    print("\nMultiple cities found:\n")

    for i, (_, row) in enumerate(matches.iterrows(), start=1):

        print(f"{i}. " f"{row['GC_UCN_MAI_2025']} " f"({row['GC_CNT_UNN_2025']})")

    while True:

        choice = input("\nSelect a city by number: ")

        try:

            choice = int(choice)

            if 1 <= choice <= len(matches):
                return matches.iloc[choice - 1]

            print("Invalid selection.")

        except ValueError:

            print("Please enter a valid number.")
