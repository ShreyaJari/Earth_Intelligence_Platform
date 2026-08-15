import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import xarray as xr

DEFAULT_CMAPS = [
    "viridis",
    "terrain",
    "gray",
    "plasma",
    "inferno",
    "magma",
    "cividis",
]


def get_layers(dataset):
    return [layer for layer in dataset.data_vars if layer != "spatial_ref"]


# Generic Raster Viewer


def display_raster(
    dataset: xr.Dataset,
    title="Raster",
    aoi_geometry=None,
    categorical_legend=None,
):

    layers = get_layers(dataset)

    if not layers:
        st.warning("No raster layers available.")
        return

    col1, col2 = st.columns([3, 1])

    with col2:

        layer = st.selectbox(
            "Layer",
            layers,
            key=f"{title}_layer",
        )

        if categorical_legend is None:

            cmap = st.selectbox(
                "Color Map",
                DEFAULT_CMAPS,
                key=f"{title}_cmap",
            )

        else:

            st.caption("Using class colors from the legend.")

    data = dataset[layer]

    if "time" in data.dims:
        data = data.isel(time=0)

    x_name = "x" if "x" in data.dims else "longitude"
    y_name = "y" if "y" in data.dims else "latitude"

    x_coords = data[x_name].values
    y_coords = data[y_name].values

    extent = [
        x_coords.min(),
        x_coords.max(),
        y_coords.min(),
        y_coords.max(),
    ]

    fig, ax = plt.subplots(figsize=(8, 6))

    if categorical_legend is not None:

        # ---------------------------------------------------------
        # Discrete, legend-matched colormap — remap raw class IDs
        # to a contiguous 0..N-1 index so each index maps to
        # exactly one legend color, guaranteeing the map matches
        # the Legend swatches shown elsewhere on the page.
        # ---------------------------------------------------------

        class_ids = sorted(categorical_legend.keys())

        colors = [categorical_legend[class_id]["color"] for class_id in class_ids]

        names = [categorical_legend[class_id]["name"] for class_id in class_ids]

        id_to_index = {class_id: index for index, class_id in enumerate(class_ids)}

        raw_values = data.values

        remapped = np.full_like(
            raw_values,
            fill_value=np.nan,
            dtype=np.float32,
        )

        for class_id, index in id_to_index.items():

            remapped[raw_values == class_id] = index

        discrete_cmap = mcolors.ListedColormap(colors)

        image = ax.imshow(
            remapped,
            cmap=discrete_cmap,
            vmin=-0.5,
            vmax=len(class_ids) - 0.5,
            origin="upper",
            extent=extent,
        )

        legend_patches = [
            plt.matplotlib.patches.Patch(
                facecolor=colors[i],
                edgecolor="black",
                linewidth=0.3,
                label=names[i],
            )
            for i in range(len(class_ids))
        ]

        ax.legend(
            handles=legend_patches,
            loc="upper left",
            bbox_to_anchor=(1.02, 1),
            fontsize=8,
            frameon=False,
        )

    else:

        image = ax.imshow(
            data,
            cmap=cmap,
            origin="upper",
            extent=extent,
        )

        plt.colorbar(
            image,
            ax=ax,
            shrink=0.8,
        )

    if aoi_geometry is not None:

        geometry_to_plot = aoi_geometry

        if data.rio.crs is not None:

            import geopandas as gpd

            aoi_gdf = gpd.GeoDataFrame(
                geometry=[aoi_geometry],
                crs="EPSG:4326",
            ).to_crs(data.rio.crs)

            geometry_to_plot = aoi_gdf.geometry.iloc[0]

        if geometry_to_plot.geom_type == "Polygon":

            boundary_polygons = [geometry_to_plot]

        elif geometry_to_plot.geom_type == "MultiPolygon":

            boundary_polygons = list(geometry_to_plot.geoms)

        else:

            boundary_polygons = []

        for polygon in boundary_polygons:

            bx, by = polygon.exterior.xy

            ax.plot(bx, by, color="red", linewidth=1.5)

    ax.set_title(layer.replace("_", " ").title())
    ax.set_xlabel("")
    ax.set_ylabel("")

    with col1:
        st.pyplot(fig)

    plt.close(fig)


# Satellite RGB Viewer


def display_rgb(dataset: xr.Dataset):

    required = {"B02", "B03", "B04", "B08"}

    if not required.issubset(dataset.data_vars):
        st.info("RGB Composite Viewer is only available for Sentinel-2 imagery.")
        return

    st.subheader("RGB Composite Viewer")

    composite = st.selectbox(
        "Composite",
        [
            "True Color",
            "Color Infrared",
        ],
        key="satellite_composite",
    )

    if composite == "True Color":
        red = dataset["B04"]
        green = dataset["B03"]
        blue = dataset["B02"]

    else:
        red = dataset["B08"]
        green = dataset["B04"]
        blue = dataset["B03"]

    if "time" in red.dims:
        red = red.isel(time=0)
        green = green.isel(time=0)
        blue = blue.isel(time=0)

    rgb = np.dstack(
        [
            red.values,
            green.values,
            blue.values,
        ]
    ).astype(float)

    low = np.nanpercentile(rgb, 2)
    high = np.nanpercentile(rgb, 98)

    rgb = (rgb - low) / (high - low)
    rgb = np.clip(rgb, 0, 1)

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.imshow(rgb)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(composite)

    st.pyplot(fig)

    plt.close(fig)


# Metadata


def display_metadata(dataset):

    st.subheader("Raster Information")

    st.write(f"**Dimensions:** {dict(dataset.sizes)}")

    st.write(f"**Layers:** {', '.join(get_layers(dataset))}")

    st.write(f"**Coordinates:** {', '.join(dataset.coords)}")
