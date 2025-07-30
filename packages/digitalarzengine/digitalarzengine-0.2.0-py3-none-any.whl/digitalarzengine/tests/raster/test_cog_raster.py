import os
import tempfile
import numpy as np
import geopandas as gpd
from pyproj import Transformer
from shapely.geometry import box
from io import BytesIO

import pytest
from digitalarzengine.io.cog_raster import COGRaster
from digitalarzengine.tests.raster.conftest import raster_crs

# Constants
SAMPLE_COG = "data/test_dummy_utm43_cog.tif"

@pytest.fixture(scope="module")
def cog_raster(dummy_raster_path):
    # Ensure COG is created from dummy raster
    if not os.path.exists(SAMPLE_COG):
        COGRaster.create_cog(dummy_raster_path, des_path=SAMPLE_COG)
    return COGRaster.open_from_local(SAMPLE_COG)


def test_01_create_cog_from_geotiff(dummy_raster_path):
    if os.path.exists(SAMPLE_COG):
        os.remove(SAMPLE_COG)
    cog_path = COGRaster.create_cog(dummy_raster_path, des_path=SAMPLE_COG)
    assert os.path.exists(cog_path)


def test_02_open_from_local(cog_raster):
    assert isinstance(cog_raster, COGRaster)
    assert cog_raster.get_file_path() == SAMPLE_COG


def test_03_get_pixel_value_at_coords(cog_raster):
    west, south, east, north = cog_raster.bounds
    mid_x = (west + east) / 2
    mid_y = (south + north) / 2

    # Transform from UTM (EPSG:32643) to WGS84 (EPSG:4326)
    transformer = Transformer.from_crs(raster_crs, "EPSG:4326", always_xy=True)
    mid_lon, mid_lat = transformer.transform(mid_x, mid_y)

    val = cog_raster.get_pixel_value_at_long_lat(mid_lon, mid_lat)
    assert val is not None


def test_04_read_tile_png(cog_raster):
    colormap = COGRaster.create_stretch_colormap(0, 255)
    tile = cog_raster.read_tile_as_png(0, 0, 0, colormap)
    assert isinstance(tile, BytesIO)
    assert tile.getbuffer().nbytes > 0


def test_05_create_empty_image(cog_raster):
    empty = cog_raster.create_empty_image(256, 256, format="JPEG")
    assert isinstance(empty, BytesIO)
    assert empty.getbuffer().nbytes > 0


def test_06_create_stretch_colormap():
    cmap = COGRaster.create_stretch_colormap(0, 100, steps=10)
    assert isinstance(cmap, dict)
    assert len(cmap) == 10
    for k, v in cmap.items():
        assert isinstance(v, tuple) and len(v) == 3


def test_07_create_color_map_with_style():
    style = {
        'min': 0,
        'max': 100,
        'palette': ['#000000', '#888888', '#FFFFFF']
    }
    cmap = COGRaster.create_color_map(style)
    assert isinstance(cmap, list)
    for rng, color in cmap:
        assert isinstance(rng, tuple) and isinstance(color, tuple)


def test_08_raster_from_array_and_multiband(cog_raster):
    data = np.random.randint(0, 255, (3, 256, 256), dtype=np.uint8)
    mask = np.ones((256, 256), dtype=bool)
    extent = [0, 0, 10, 10]
    raster = cog_raster.raster_from_array(data, mask, extent)
    assert raster.get_dataset() is not None


def test_09_save_tile_as_geotiff(cog_raster):
    with tempfile.NamedTemporaryFile(suffix=".tif") as tmp:
        cog_raster.save_tile_as_geotiff(0, 0, 0, tmp.name)
        assert os.path.exists(tmp.name)


def test_10_read_data_under_aoi(cog_raster):
    aoi = gpd.GeoDataFrame(geometry=[box(*cog_raster.bounds)], crs="EPSG:4326")
    result = cog_raster.read_data_under_aoi(aoi)
    assert isinstance(result, type(cog_raster.get_rio_raster()))
