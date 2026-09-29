"""Output helpers: GeoPackage for QGIS, PostGIS."""

from __future__ import annotations

import os

from .config import path

__all__ = ["to_gpkg", "to_postgis"]


def to_gpkg(gdf, layer: str, name: str = "omfm.gpkg"):
    """Write a layer to ``outputs/maps/<name>``."""
    out = path("maps", name, mkdir=True)
    gdf.to_file(out, layer=layer, driver="GPKG")
    return out


def to_postgis(gdf, table: str, url: str | None = None, schema: str = "public") -> None:
    """Write a layer to PostGIS. Needs the ``postgis`` extra; URL from ``OMFM_PG`` by default."""
    from sqlalchemy import create_engine

    url = url or os.environ.get("OMFM_PG", "postgresql://omfm:omfm@localhost:5432/omfm")
    gdf.to_postgis(table, create_engine(url), schema=schema, if_exists="replace", index=False)
