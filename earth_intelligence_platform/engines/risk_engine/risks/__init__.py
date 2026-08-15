"""
Risk modules.
"""

from .flood import compute_flood_risk
from .landslide import compute_landslide_risk
from .urban_heat import compute_urban_heat_risk
from .wildfire import compute_wildfire_risk
from .wind import compute_wind_risk

__all__ = [
    "compute_flood_risk",
    "compute_landslide_risk",
    "compute_wildfire_risk",
    "compute_urban_heat_risk",
    "compute_wind_risk",
]
