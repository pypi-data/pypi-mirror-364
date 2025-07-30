import pytest
import geopandas as gpd
from shapely.geometry import Point
from sqlalchemy import Table, Column, Integer, String, MetaData
from geoalchemy2 import Geometry

from digitalarzengine.adapters.db_manager import GeoDBManager, DBParams


@pytest.fixture(scope="module")
def geo_db_manager():
    db_params = DBParams(
        engine_name="sqlite",
        con_str={"file_path": ":memory:"}
    )
    manager = GeoDBManager(db_params)

    # Create spatial metadata
    engine = manager.get_engine()
    metadata = MetaData()

    # Define spatial table
    test_geom_table = Table(
        "places", metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("geom", Geometry(geometry_type="POINT", srid=4326))
    )

    metadata.create_all(engine)

    # Insert test geometries
    with manager.managed_session() as session:
        session.execute(test_geom_table.insert().values([
            {"id": 1, "name": "A", "geom": "SRID=4326;POINT(10 10)"},
            {"id": 2, "name": "B", "geom": "SRID=4326;POINT(20 20)"}
        ]))
        session.commit()

    return manager


def test_execute_stmt_as_gdf(geo_db_manager: GeoDBManager):
    gdf = geo_db_manager.execute_stmt_as_gdf("SELECT id, name, geom FROM places")
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert gdf.shape[0] == 2
    assert gdf.geometry.iloc[0].equals(Point(10, 10))


def test_execute_query_as_dict_spatial(geo_db_manager: GeoDBManager):
    result = geo_db_manager.execute_query_as_dict(
        "SELECT id, name FROM places WHERE ST_X(geom) = 20"
    )
    assert isinstance(result, list)
    assert result[0]["name"] == "B"
