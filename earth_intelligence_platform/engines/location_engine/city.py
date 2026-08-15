"""
city.py

Defines the City object used throughout the Earth Intelligence Platform.

Author: Shreya Jariwala
Project: Earth Intelligence Platform
"""

from dataclasses import dataclass

from shapely.geometry import MultiPolygon, Polygon
from shapely.geometry.base import BaseGeometry


@dataclass(slots=True)
class City:
    """
    Represents a resolved urban centre.
    """

    name: str
    country: str
    geometry: BaseGeometry

    @property
    def centroid(self):
        """Returns the centroid of the city."""
        return self.geometry.centroid

    @property
    def bounds(self):
        """
        Returns the bounding box.

        (minx, miny, maxx, maxy)
        """
        return self.geometry.bounds

    @property
    def area(self):
        """
        Returns area in square degrees.

        NOTE:
        This should not be used for calculations.
        Reproject before calculating metric areas.
        """
        return self.geometry.area

    def __repr__(self):

        return f"City(" f"name='{self.name}', " f"country='{self.country}')"
