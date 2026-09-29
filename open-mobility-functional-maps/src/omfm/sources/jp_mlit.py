"""Source: jp_mlit.

MLIT 全国の人流オープンデータ (G空間情報センター mlit-1km-fromto), Hiroshima prefecture; provider Agoop (verify in データ定義書 p.6); JIS X 0410 1 km mesh; suppression <10; normalised volumes.

Contract: `fetch()` → files in data/raw/<source>/ + manifest entry (url, version, sha256, accessed);
`load()` → tidy GeoDataFrame/DataFrame saved to data/interim/<source>*.parquet.
Every numeric check against tests/golden_values.yaml. See docs/02_DATA_SOURCES.md.
"""


def fetch(cfg: dict) -> None:
    raise NotImplementedError


def load(cfg: dict):
    raise NotImplementedError
