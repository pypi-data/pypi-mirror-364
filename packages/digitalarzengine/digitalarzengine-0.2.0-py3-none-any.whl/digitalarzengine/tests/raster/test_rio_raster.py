import numpy as np
import pytest

from affine import Affine

from digitalarzengine.io.rio_raster import RioRaster
from digitalarzengine.tests.raster.conftest import spatial_resolution, extent


# Test reading data array
def test_get_data_array(dummy_raster_path):
    raster = RioRaster(dummy_raster_path)
    data = raster.get_data_array()
    assert isinstance(data, np.ndarray)
    assert data.ndim == 3


def test_raster_core_checks(dummy_raster_path):
    raster = RioRaster(dummy_raster_path)
    assert not raster.empty, "Raster should not be empty"

    # ✅ CRS check
    assert raster.get_crs().to_string() == "EPSG:32643"

    # ✅ Spatial resolution
    xres, yres = raster.get_spatial_resolution()
    assert pytest.approx(xres, 0.01) == spatial_resolution
    assert pytest.approx(yres, 0.01) == spatial_resolution

    # ✅ Image resolution from extent
    xmin, ymin, xmax, ymax = extent
    expected_width = int((xmax - xmin) / spatial_resolution)
    expected_height = int((ymax - ymin) / spatial_resolution)
    width, height = raster.get_image_resolution()
    assert width == expected_width
    assert height == expected_height

    # ✅ Bands / Spectral
    assert raster.get_spectral_resolution() == 1

    # ✅ Radiometric
    assert raster.get_radiometric_resolution() in ["float32", "float16"]

    # ✅ GeoTransform
    transform = raster.get_geo_transform()
    assert isinstance(transform, Affine)
    assert transform.a == spatial_resolution
    assert transform.e == -spatial_resolution

    # ✅ Metadata keys
    meta = raster.get_meta()
    expected_keys = {"driver", "dtype", "count", "crs", "transform", "width", "height"}
    assert expected_keys.issubset(meta.keys())

    # ✅ Nodata check
    nodata = raster.get_nodata_value()
    assert nodata is None or isinstance(nodata, (int, float))

    print("✅ Resolution + Metadata checks passed.")


# Test clipping with same CRS (simple box)
def test_clip_raster(dummy_raster_path):
    import geopandas as gpd
    from shapely.geometry import box
    raster = RioRaster(dummy_raster_path)
    bounds = raster.get_bounds()
    aoi_geom = box(*bounds)
    aoi_gdf = gpd.GeoDataFrame(geometry=[aoi_geom], crs=raster.get_crs())
    clipped = raster.clip_raster(aoi_gdf, in_place=False)
    assert isinstance(clipped, RioRaster)
    assert not clipped.empty


# Test reprojection
def test_reproject_to(dummy_raster_path):
    raster = RioRaster(dummy_raster_path)
    reprojected = raster.reproject_to("EPSG:3857", in_place=False)
    assert isinstance(reprojected, RioRaster)
    assert reprojected.get_crs().to_string() == "EPSG:3857"
