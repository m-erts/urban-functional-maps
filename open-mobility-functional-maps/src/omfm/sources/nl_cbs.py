"""Source: nl_cbs.

CBS 81252NED (2006-2014, COROP 40x40) via OData; successors 83628NED, 85481NED; COROP boundaries from PDOK.

Contract: `fetch()` → files in data/raw/<source>/ + manifest entry (url, version, sha256, accessed);
`load()` → tidy GeoDataFrame/DataFrame saved to data/interim/<source>*.parquet.
Every numeric check against tests/golden_values.yaml. See docs/02_DATA_SOURCES.md.
"""


def fetch(cfg: dict) -> None:
    raise NotImplementedError


def load(cfg: dict):
    raise NotImplementedError
