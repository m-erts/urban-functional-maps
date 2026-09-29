"""Source: overture.

Overture Places via DuckDB httpfs/spatial on the release GeoParquet; filter by bbox; H3 r8 counts.

Contract: `fetch()` → files in data/raw/<source>/ + manifest entry (url, version, sha256, accessed);
`load()` → tidy GeoDataFrame/DataFrame saved to data/interim/<source>*.parquet.
Every numeric check against tests/golden_values.yaml. See docs/02_DATA_SOURCES.md.
"""


def fetch(cfg: dict) -> None:
    raise NotImplementedError


def load(cfg: dict):
    raise NotImplementedError
