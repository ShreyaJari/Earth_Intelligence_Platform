"""
Earth Intelligence Platform
Satellite Engine

Select Acquisition

Selects the best acquisition from the ranked list, subject
to a minimum AOI coverage gate.
"""

from earth_intelligence_platform.engines.satellite_engine.satellite_product import Scene

MIN_COVERAGE_PERCENT = 95.0


def select_acquisition(
    ranked_acquisitions,
    min_coverage_percent=MIN_COVERAGE_PERCENT,
):
    """
    Select the highest-ranked acquisition.

    Parameters
    ----------
    ranked_acquisitions : list[Acquisition]

    min_coverage_percent : float
        Minimum acceptable AOI coverage. Raises if the
        best acquisition falls short.

    Returns
    -------
    Scene
    """

    if not ranked_acquisitions:

        raise ValueError("No acquisitions available for selection.")

    best = ranked_acquisitions[0]

    if best.coverage_percent < min_coverage_percent:

        raise RuntimeError(
            f"Best available acquisition ({best.date}) covers "
            f"only {best.coverage_percent}% of the AOI "
            f"(minimum required: {min_coverage_percent}%). "
            f"Tiles found: {best.tile_ids}. "
            "Consider widening the date range or lowering "
            "the coverage threshold."
        )

    scene = Scene(
        scene_id=f"acquisition_{best.date}",
        acquisition_date=best.date,
        collection="sentinel-2-l2a",
        provider="Microsoft Planetary Computer",
        cloud_cover=best.cloud_cover,
        stac_items=best.items,
        tile_ids=best.tile_ids,
        coverage_percent=best.coverage_percent,
    )

    print("\n========== SELECTED ACQUISITION ==========")

    print(f"Date           : {scene.acquisition_date}")

    print(f"Tiles          : {scene.tile_ids}")

    print(f"Coverage       : {scene.coverage_percent}%")

    print(f"Cloud Cover    : {scene.cloud_cover:.2f}%")

    print(f"Provider       : {scene.provider}")

    print("============================================\n")

    return scene
