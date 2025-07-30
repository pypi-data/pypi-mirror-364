import os
from pathlib import Path
import boto3
import numpy as np
import pytest
import rasterio
from moto import mock_aws

from digitalarzengine.io.managers.s3_manager import S3Manager


@pytest.fixture
def s3_manager():
    return S3Manager("fake", "fake", "us-east-1")


def create_test_geotiff(path: Path, crs="EPSG:4326"):
    data = np.ones((1, 10, 10), dtype=rasterio.uint8)
    transform = rasterio.transform.from_origin(0, 10, 1, 1)

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=10,
        width=10,
        count=1,
        dtype=data.dtype,
        crs=crs,
        transform=transform,
    ) as dst:
        dst.write(data)

    return path


@mock_aws
def test_upload_and_existence(tmp_path: Path, s3_manager: S3Manager):
    os.environ.update({
        "AWS_ACCESS_KEY_ID": "fake",
        "AWS_SECRET_ACCESS_KEY": "fake"
    })

    s3 = boto3.client("s3", region_name="us-east-1")
    bucket_name = "my-test-bucket"
    s3.create_bucket(Bucket=bucket_name)

    local_file = tmp_path / "test.txt"
    content = "Hello, Moto"
    local_file.write_text(content)

    s3_uri = f"s3://{bucket_name}/test-folder/test.txt"
    assert s3_manager.upload_file(str(local_file), s3_uri)
    assert s3_manager.is_file_exists(s3_uri)

    obj = s3.get_object(Bucket=bucket_name, Key="test-folder/test.txt")
    assert obj["Body"].read().decode("utf-8") == content


# @mock_aws
# def test_raster_upload_and_open(tmp_path: Path, s3_manager: S3Manager):
#     s3 = boto3.client("s3", region_name="us-east-1")
#     bucket = "test-bucket"
#     s3.create_bucket(Bucket=bucket)
#
#     local_tif = create_test_geotiff(tmp_path / "dummy.tif")
#     s3_uri = f"s3://{bucket}/rasters/dummy.tif"
#     assert s3_manager.upload_file(str(local_tif), s3_uri)
#
#     dataset = s3_manager.get_rio_dataset(s3_uri)
#     assert dataset.count == 1
#     assert dataset.crs is not None
#     assert dataset.read(1).shape == (10, 10)
#     dataset.close()
