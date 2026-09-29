"""Source: uk_census.

ONS ODWP01EW (2021) + WU01EW (2011) MSOA OD; MSOA BGC boundaries; TTWA 2011; LAD. Clean: drop home / no-fixed-place (2021 cat. 1,3; 2011 OD0000001/3) and offshore/abroad codes identically in both years.

Contract: `fetch()` → files in data/raw/<source>/ + manifest entry (url, version, sha256, accessed);
`load()` → tidy GeoDataFrame/DataFrame saved to data/interim/<source>*.parquet.
Every numeric check against tests/golden_values.yaml. See docs/02_DATA_SOURCES.md.
"""


def fetch(cfg: dict) -> None:
    raise NotImplementedError


def load(cfg: dict):
    raise NotImplementedError
