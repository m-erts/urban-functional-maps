"""I/O helpers: params, parquet, PostGIS export, GeoPackage for QGIS."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def params() -> dict:
    return yaml.safe_load((ROOT / "config" / "params.yaml").read_text())


def to_postgis(gdf, table: str, url: str = "postgresql://omfm:omfm@localhost:5432/omfm", schema="public"):
    from sqlalchemy import create_engine

    gdf.to_postgis(table, create_engine(url), schema=schema, if_exists="replace", index=False)


def to_gpkg(gdf, layer: str, path: Path = ROOT / "outputs" / "maps" / "omfm.gpkg"):
    path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(path, layer=layer, driver="GPKG")
