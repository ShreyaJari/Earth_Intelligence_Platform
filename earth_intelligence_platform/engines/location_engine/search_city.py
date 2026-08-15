"""
search_city.py

Searches the GHS Urban Centre Database for matching cities.

Project: Earth Intelligence Platform
"""

from pathlib import Path

import geopandas as gpd


class GHSCityDatabase:
    """
    Loads and searches the GHS Urban Centre Database.
    """

    # ------------------------------------------------------------------
    # Dataset configuration
    # ------------------------------------------------------------------

    LAYER_NAME = "GHSL_UCDB_THEME_GENERAL_CHARACTERISTICS_GLOBE_R2024A"

    CITY_COLUMN = "GC_UCN_MAI_2025"
    COUNTRY_COLUMN = "GC_CNT_UNN_2025"

    def __init__(self, gpkg_path):

        self.gpkg_path = Path(gpkg_path)

        if not self.gpkg_path.exists():
            raise FileNotFoundError(f"GHS dataset not found:\n{self.gpkg_path}")

        print("Loading GHS Urban Centre Database...")

        self.gdf = gpd.read_file(self.gpkg_path, layer=self.LAYER_NAME)

        # Convert to WGS84
        self.gdf = self.gdf.to_crs(epsg=4326)

        print(f"Loaded {len(self.gdf):,} urban centres.")

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, city, country=None):
        """
        Search for a city.

        Parameters
        ----------
        city : str
            Name of the city.

        country : str, optional
            Country filter.

        Returns
        -------
        GeoDataFrame
            Matching city polygons.
        """

        city = city.strip()

        # Exact city match
        matches = self.gdf[self.gdf[self.CITY_COLUMN].str.casefold() == city.casefold()]

        # Optional country filter
        if country is not None:

            matches = matches[
                matches[self.COUNTRY_COLUMN].str.casefold() == country.casefold()
            ]

        return matches.reset_index(drop=True)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self, matches):

        if matches.empty:
            print("No matching city found.")
            return

        print("\nSearch Results")
        print("-" * 60)

        for _, row in matches.iterrows():

            print(f"City      : {row[self.CITY_COLUMN]}")
            print(f"Country   : {row[self.COUNTRY_COLUMN]}")
            print(f"Area      : {row['GC_UCA_KM2_2025']:.0f} km²")
            print(f"Geometry  : {row.geometry.geom_type}")
            print("-" * 60)

    # ------------------------------------------------------------------
    # Plot
    # ------------------------------------------------------------------

    def plot(self, matches):

        if matches.empty:
            print("Nothing to plot.")
            return

        ax = matches.plot(
            figsize=(8, 8),
            edgecolor="red",
            facecolor="none",
            linewidth=2,
        )

        ax.set_title(matches.iloc[0][self.CITY_COLUMN])

        return ax
