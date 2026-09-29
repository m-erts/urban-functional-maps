"""Source: osm_traces.

OSM API 0.6 trackpoints: GET /api/0.6/trackpoints?bbox=..&page=0..39 (5000 pts/page). Cache GPX per page, respect usage policy, keep untimed (private) points separately.

Contract: `fetch()` → files in data/raw/<source>/ + manifest entry (url, version, sha256, accessed);
`load()` → tidy GeoDataFrame/DataFrame saved to data/interim/<source>*.parquet.
Every numeric check against tests/golden_values.yaml. See docs/02_DATA_SOURCES.md.
"""


def fetch(cfg: dict) -> None:
    raise NotImplementedError


def load(cfg: dict):
    raise NotImplementedError
