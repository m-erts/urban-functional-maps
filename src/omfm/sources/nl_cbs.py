"""Netherlands: CBS register-based jobs by residence region x workplace region.

81252NED (2006-2014) publishes pairs only between 40 COROP regions, regions that were drawn
in 1970 as commuter basins. Its successors 83628NED (2014-2020) and 85481NED (2021-) exist;
85481NED publishes municipality pairs.

OData quirks: ``$skip`` is ignored by the service, so the request is split by residence region;
region codes are space-padded; values are thousands of jobs.
"""

from __future__ import annotations

import time

import pandas as pd
import requests

from ..config import params, path

__all__ = ["fetch", "load", "corop_matrix"]

UA = {"User-Agent": "omfm/1.0 (+https://github.com/m-erts/urban-functional-maps)"}


def _get(url: str, **q) -> list[dict]:
    q["$format"] = "json"
    for attempt in range(5):
        r = requests.get(url, params=q, headers=UA, timeout=120)
        if r.status_code == 200:
            return r.json()["value"]
        time.sleep(2 + 2 * attempt)
    raise RuntimeError(f"{url}: HTTP {r.status_code}")


def fetch(force: bool = False) -> pd.DataFrame:
    """Download the December slice for all region pairs; cache under ``paths.interim``."""
    cfg = params()["netherlands"]
    out = path("interim", cfg["cache"], mkdir=True)
    if out.exists() and not force:
        return pd.read_csv(out)
    base = f"{cfg['odata']}/{cfg['table_2014']}"
    regions = [r["Key"] for r in _get(f"{base}/WoonregioS")]
    rows = []
    for key in regions:
        flt = (
            f"Geslacht eq '{cfg['sex']}' and Leeftijd eq '{cfg['age']}' and "
            f"Perioden eq '{cfg['period']}' and WoonregioS eq '{key}'"
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
    """Cached table, or fetch it."""
    return fetch()


def corop_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """COROP x COROP pairs (codes ``CRxx``) as ``origin, dest, flow`` in jobs."""
    m = df[df.origin.str.startswith("CR") & df.dest.str.startswith("CR")]
    return pd.DataFrame({"origin": m.origin, "dest": m.dest, "flow": m.jobs_thousands * 1000.0}).reset_index(drop=True)
