"""Source: serbia_census.

SORS Popis 2022 daily migrants by municipality and destination band (work, education merged pupils+students); GeoSrbija boundaries (UTF-8!); Kosovo* not covered — UNSCR 1244 footnote.

Contract: `fetch()` → files in data/raw/<source>/ + manifest entry (url, version, sha256, accessed);
`load()` → tidy GeoDataFrame/DataFrame saved to data/interim/<source>*.parquet.
Every numeric check against tests/golden_values.yaml. See docs/02_DATA_SOURCES.md.
"""


def fetch(cfg: dict) -> None:
    raise NotImplementedError


def load(cfg: dict):
    raise NotImplementedError
