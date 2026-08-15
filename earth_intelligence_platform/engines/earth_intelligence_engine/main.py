"""
main.py

Entry point for the Earth Intelligence Engine.
"""

from .earth_intelligence_engine import run_earth_intelligence_engine


def main(
    location_product,
    discovery_product,
    satellite_product,
    terrain_product,
    landcover_product,
    weather_product,
    risk_product,
):

    return run_earth_intelligence_engine(
        location_product,
        discovery_product,
        satellite_product,
        terrain_product,
        landcover_product,
        weather_product,
        risk_product,
    )


if __name__ == "__main__":

    print("Earth Intelligence Engine is a library and should be imported.")
