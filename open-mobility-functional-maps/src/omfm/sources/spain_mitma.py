"""Source: spain_mitma.

MITMA big-data mobility v2 (2022→, hourly). Download from movilidad-opendata.mitma.es or via spanishoddata (R).

Contract: `fetch()` → files in data/raw/<source>/ + manifest entry (url, version, sha256, accessed);
`load()` → tidy GeoDataFrame/DataFrame saved to data/interim/<source>*.parquet.
Every numeric check against tests/golden_values.yaml. See docs/02_DATA_SOURCES.md.
"""


def fetch(cfg: dict) -> None:
    raise NotImplementedError


def load(cfg: dict):
    raise NotImplementedError
