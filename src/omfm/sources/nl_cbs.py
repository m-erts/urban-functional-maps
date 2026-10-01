"""Netherlands: CBS register-based jobs by region of residence and region of work.

81252NED (2006-2014) publishes pairs only between 40 COROP regions, which CBS describes as
designed in 1970, each a central city with its surrounding area. Its successor 85481NED (2021-)
publishes pairs between municipalities for December of each year. Values are thousands of jobs
with one decimal, so a pair is known to the nearest 100 jobs and pairs under 50 jobs appear as 0.

OData quirks: ``$skip`` is ignored by the service, so every request filters on one region of
residence; region codes are padded with spaces.
"""

from __future__ import annotations

import json
import time

import pandas as pd
import requests

from ..config import params, path

__all__ = [
    "fetch",
    "load",
    "corop_matrix",
    "fetch_municipal",
    "municipal_matrix",
    "fetch_boundaries",
    "load_boundaries",
]

UA = {"User-Agent": "omfm/1.0 (+https://github.com/m-erts/urban-functional-maps)"}
UNKNOWN = "GM0000"  # municipality not known: not a territory, dropped from the pairs


def _get(url: str, **q) -> list[dict]:
    q["$format"] = "json"
    for attempt in range(5):
        r = requests.get(url, params=q, headers=UA, timeout=120)
        if r.status_code == 200:
            return r.json()["value"]
        time.sleep(2 + 2 * attempt)
    raise RuntimeError(f"{url}: HTTP {r.status_code}")


# ------------------------------------------------------------------------------ 81252NED, COROP
def fetch(force: bool = False) -> pd.DataFrame:
    """December 2014, all region pairs of 81252NED; cached under ``paths.interim``."""
    cfg = params()["netherlands"]
    out = path("interim", cfg["cache"], mkdir=True)
    if out.exists() and not force:
        return pd.read_csv(out)
    base = f"{cfg['odata']}/{cfg['table_2014']}"
    rows = []
    for r in _get(f"{base}/WoonregioS"):
        flt = (
            f"Geslacht eq '{cfg['sex']}' and Leeftijd eq '{cfg['age']}' and "
            f"Perioden eq '{cfg['period']}' and WoonregioS eq '{r['Key']}'"
        )
        rows += _get(f"{base}/TypedDataSet", **{"$filter": flt})
        time.sleep(0.2)
    df = pd.DataFrame(rows)
    df = pd.DataFrame(
        {
            "origin": df.WoonregioS.str.strip(),
            "dest": df.WerkregioS.str.strip(),
            "jobs_thousands": df.BanenVanWerknemers_1,
        }
    )
    df.dropna(subset=["jobs_thousands"]).to_csv(out, index=False)
    return pd.read_csv(out)


def load() -> pd.DataFrame:
    return fetch()


def corop_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """COROP x COROP pairs (codes ``CRxx``) as ``origin, dest, flow`` in jobs."""
    m = df[df.origin.str.startswith("CR") & df.dest.str.startswith("CR")]
    return pd.DataFrame({"origin": m.origin, "dest": m.dest, "flow": m.jobs_thousands * 1000.0}).reset_index(drop=True)


# -------------------------------------------------------------------- 85481NED, municipalities
def fetch_municipal(force: bool = False) -> pd.DataFrame:
    """All pairs of 85481NED for the configured December; cached under ``paths.interim``."""
    cfg = params()["netherlands"]["municipal"]
    out = path("interim", cfg["cache"], mkdir=True)
    if out.exists() and not force:
        return pd.read_csv(out)
    base = f"{params()['netherlands']['odata']}/{cfg['table']}"
    regions = [r["Key"] for r in _get(f"{base}/WoonregioS") if r["Key"].startswith("GM")]
    rows = []
    for key in regions:
        rows += _get(f"{base}/TypedDataSet", **{"$filter": f"Perioden eq '{cfg['period']}' and WoonregioS eq '{key}'"})
        time.sleep(0.1)
    df = pd.DataFrame(rows)
    df = pd.DataFrame(
        {
            "origin": df.WoonregioS.str.strip(),
            "dest": df.WerkregioS.str.strip(),
            "jobs_thousands": df.BanenVanWerknemers_1,
        }
    )
    df.dropna(subset=["jobs_thousands"]).to_csv(out, index=False)
    return pd.read_csv(out)


def municipal_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Municipality pairs as ``origin, dest, flow`` in jobs, and the share of each municipality's
    jobs (row ``NL01``) that the rounded pairs retain. Pairs with the unknown municipality are dropped."""
    gm_o, gm_d = df.origin.str.startswith("GM"), df.dest.str.startswith("GM")
    real = gm_o & gm_d & (df.origin != UNKNOWN) & (df.dest != UNKNOWN)
    gm = df[real & (df.jobs_thousands > 0)]
    od = pd.DataFrame({"origin": gm.origin, "dest": gm.dest, "flow": gm.jobs_thousands * 1000.0}).reset_index(drop=True)
    nl = df[df.dest == "NL01"].set_index("origin").jobs_thousands * 1000.0
    retained = (od.groupby("origin").flow.sum() / nl.reindex(od.origin.unique())).rename("retained")
    return od, retained


# --------------------------------------------------------------------------------- boundaries
def fetch_boundaries(collection: str, year: int, force: bool = False):
    """Generalised CBS boundaries from the PDOK OGC API, as GeoJSON under ``data/raw/NL``."""
    cfg = params()["netherlands"]["municipal"]
    out = path("raw", "NL", f"{collection}_{year}.geojson", mkdir=True)
    if out.exists() and not force:
        return out
    url = f"{cfg['pdok']}/collections/{collection}/items"
    q = {"f": "json", "limit": 1000, "jaarcode": year}
    feats = []
    while url:
        r = requests.get(url, params=q, headers=UA, timeout=180)
        r.raise_for_status()
        d = r.json()
        feats += d["features"]
        url = next((lk["href"] for lk in d.get("links", []) if lk.get("rel") == "next"), None)
        q = None
    out.write_text(json.dumps({"type": "FeatureCollection", "features": feats}), encoding="utf-8")
    return out


def load_boundaries(collection: str, year: int):
    import geopandas as gpd

    g = gpd.read_file(fetch_boundaries(collection, year))
    return g.rename(columns={"statcode": "unit"})[["unit", "statnaam", "geometry"]].to_crs(
        params()["netherlands"]["crs"]
    )
