from earth_intelligence_platform.engines.location_engine.main import run_location_engine

aoi = run_location_engine(
    location={
        "input_type": "city",
        "city": "Mumbai",
        "country": "India",
    }
)

print(aoi["identity"]["name"])
