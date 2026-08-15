import folium
from streamlit_folium import st_folium

# --------------------------------------------------
# Configuration
# --------------------------------------------------

DEFAULT_MAP_HEIGHT = 650
DEFAULT_TILES = "OpenStreetMap"

# --------------------------------------------------
# Map Creation
# --------------------------------------------------


def create_map(aoi):
    """
    Create the base Folium map centered on the AOI.
    """

    centroid = aoi["spatial"]["centroid"]

    m = folium.Map(
        location=[
            centroid["latitude"],
            centroid["longitude"],
        ],
        zoom_start=10,
        tiles=None,
        control_scale=True,
    )

    return m


def add_basemaps(m):
    """
    Add selectable basemaps.
    """

    # OpenStreetMap
    folium.TileLayer(
        "OpenStreetMap",
        name="OpenStreetMap",
    ).add_to(m)

    # Carto Light
    folium.TileLayer(
        "CartoDB positron",
        name="Light",
    ).add_to(m)

    # Carto Dark
    folium.TileLayer(
        "CartoDB dark_matter",
        name="Dark",
    ).add_to(m)

    # OpenTopoMap
    folium.TileLayer(
        "OpenTopoMap",
        name="Terrain",
    ).add_to(m)

    # Esri Satellite
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite",
        overlay=False,
        control=True,
    ).add_to(m)


# --------------------------------------------------
# AOI Boundary
# --------------------------------------------------


def add_aoi(m, aoi):
    """
    Add AOI polygon.
    """

    geometry = aoi["geometry"]["geometry"]

    folium.GeoJson(
        geometry,
        name="Area of Interest",
        style_function=lambda feature: {
            "fillColor": "#2E86DE",
            "color": "#1B4F72",
            "weight": 3,
            "fillOpacity": 0.2,
        },
    ).add_to(m)


# --------------------------------------------------
# Centroid
# --------------------------------------------------


def add_centroid(m, aoi):
    """
    Add centroid marker.
    """

    centroid = aoi["spatial"]["centroid"]

    folium.Marker(
        location=[
            centroid["latitude"],
            centroid["longitude"],
        ],
        tooltip=aoi["identity"]["name"],
        popup=aoi["identity"]["name"],
        icon=folium.Icon(color="red"),
    ).add_to(m)


# --------------------------------------------------
# Zoom to AOI
# --------------------------------------------------


def fit_to_aoi(m, aoi):
    """
    Automatically fit map to AOI bounds.
    """

    bounds = aoi["geometry"]["geometry"].bounds

    m.fit_bounds(
        [
            [bounds[1], bounds[0]],
            [bounds[3], bounds[2]],
        ]
    )


# --------------------------------------------------
# Display
# --------------------------------------------------


def display_map(aoi):

    m = create_map(aoi)

    add_basemaps(m)

    add_aoi(m, aoi)

    add_centroid(m, aoi)

    fit_to_aoi(m, aoi)

    folium.LayerControl(collapsed=False).add_to(m)

    st_folium(
        m,
        width="stretch",
        height=DEFAULT_MAP_HEIGHT,
    )
