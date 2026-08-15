"""
main.py

Entry point for the Risk Engine.
"""

from .risk_engine import run_risk_engine


def main(
    terrain_product,
    landcover_product,
    weather_product,
    satellite_product,
):

    return run_risk_engine(
        terrain_product,
        landcover_product,
        weather_product,
        satellite_product,
    )


if __name__ == "__main__":

    print("Risk Engine is a library and should be imported.")
