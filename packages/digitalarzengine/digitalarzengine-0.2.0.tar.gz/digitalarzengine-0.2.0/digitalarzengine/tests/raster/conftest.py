# conftest.py

import os
import numpy as np
import pytest

from digitalarzengine.io.rio_raster import RioRaster

# Test file paths
TEST_DIR = "data"
SAMPLE_COG = os.path.join(TEST_DIR, "test_dummy_utm43_cog.tif")
COLOR_TILE_JPG = os.path.join(TEST_DIR, "test_tile_colored.jpg")
COLOR_TILE_PNG = os.path.join(TEST_DIR, "test_tile_colored.png")

spatial_resolution = 300
extent = (420000, 3520000, 423000, 3523000)
raster_crs = "EPSG:32643"


@pytest.fixture(scope="module")
def dummy_raster_path():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    raster_path = os.path.join(data_dir, "test_dummy_utm43.tif")

    # Delete old file if it exists
    if os.path.exists(raster_path):
        os.remove(raster_path)

    # Create raster
    RioRaster.create_dummy_geotiff(
        output_path=raster_path,
        spatial_resolution=spatial_resolution,
        extent=extent,
        count=1,
        crs=raster_crs,
        dtype=np.float32,
        value_range=(0.0, 1.0)
    )

    return raster_path

