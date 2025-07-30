import pytest
import geopandas as gpd
from shapely.geometry import Point
from sqlalchemy import MetaData, Table, Column, Integer, String
from geoalchemy2 import Geometry
from digitalarzengine.adapters.db_manager import GeoDBManager, DBParams

POSTGIS_DB_PARAMS = DBParams(
    engine_name="postgresql+psycopg2",  # Make sure you use the correct driver
    con_str={
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": "55432",  # Must match your PostGIS test instance
        "name": "postgres",
    }
)

@pytest.fixture(scope="module")
def postgis_manager():
    """Fixture to setup and teardown a test spatial table"""
    manager = GeoDBManager(POSTGIS_DB_PARAMS)
    engine = manager.get_engine()
    metadata = MetaData()

    test_geom_table = Table(
        "places_test", metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("geom", Geometry(geometry_type="POINT", srid=4326)),
    )

    metadata.drop_all(engine, checkfirst=True)
    metadata.create_all(engine)

    with manager.managed_session() as session:
        session.execute(test_geom_table.insert().values([
            {"id": 1, "name": "Alpha", "geom": "SRID=4326;POINT(30 10)"},
            {"id": 2, "name": "Beta", "geom": "SRID=4326;POINT(40 20)"}
        ]))
        session.commit()

    yield manager

    metadata.drop_all(engine)


def test_gdf_from_postgis(postgis_manager: GeoDBManager):
    gdf = postgis_manager.execute_stmt_as_gdf("SELECT id, name, geom FROM places_test", srid=4326)
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert gdf.shape[0] == 2
    assert gdf.iloc[0]["name"] == "Alpha"
    assert gdf.geometry.iloc[0].equals(Point(30, 10))


def test_dict_query_postgis(postgis_manager: GeoDBManager):
    result = postgis_manager.execute_query_as_dict("SELECT * FROM places_test WHERE name = 'Beta'")
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == 2
    assert result[0]["name"] == "Beta"


def test_get_spatial_table_names(postgis_manager: GeoDBManager):
    spatial_tables = postgis_manager.get_spatial_table_names()
    assert isinstance(spatial_tables, list)
    assert "places_test" in spatial_tables


def test_table_to_gdf(postgis_manager: GeoDBManager):
    gdf = postgis_manager.table_to_gdf("places_test", geom_col_name="geom")
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert gdf.crs.to_epsg() == 4326
    assert len(gdf) == 2
    assert "name" in gdf.columns


def test_data_to_gdf_from_raw_query(postgis_manager: GeoDBManager):
    # Mimic lower-level call to data_to_gdf()
    data = postgis_manager.get_query_data("SELECT id, name, geom FROM places_test")
    gdf = postgis_manager.data_to_gdf(data, geom_col="geom", srid=4326, is_wkb=True)
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert gdf.shape[0] == 2
    assert gdf.crs.to_epsg() == 4326
