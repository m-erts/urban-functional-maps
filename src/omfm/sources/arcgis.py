"""Paged download from an ArcGIS feature service (ONS Open Geography Portal)."""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests

UA = {"User-Agent": "omfm/1.0 (+https://github.com/m-erts/urban-functional-maps)"}


def fetch_layer(
    service_url: str,
    out: Path,
    geometry: bool = True,
    page: int = 2000,
    out_sr: int = 4326,
    where: str = "1=1",
    pause: float = 0.3,
) -> Path:
    """Download every feature of ``<service_url>/0`` into one GeoJSON (or JSON records) file.

    Idempotent: an existing non-empty ``out`` is kept. Pagination uses resultOffset, which the
    service honours for layers that advertise ``supportsPagination``.
    """
    out = Path(out)
    if out.exists() and out.stat().st_size > 0:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    url = f"{service_url.rstrip('/')}/0/query"
    feats, offset = [], 0
    while True:
        q = {
            "where": where,
            "outFields": "*",
            "resultOffset": offset,
            "resultRecordCount": page,
            "returnGeometry": str(geometry).lower(),
            "f": "geojson" if geometry else "json",
        }
        if geometry:
            q["outSR"] = out_sr
        for attempt in range(5):
            r = requests.get(url, params=q, headers=UA, timeout=180)
            if r.status_code == 200 and "error" not in r.text[:200].lower():
                break
            time.sleep(2 + 3 * attempt)
        else:
            raise RuntimeError(f"{url}: HTTP {r.status_code} after retries: {r.text[:200]}")
        d = r.json()
        batch = d.get("features", [])
        feats.extend(batch if geometry else [f["attributes"] for f in batch])
        more = d.get("exceededTransferLimit") or d.get("properties", {}).get("exceededTransferLimit")
        if not batch or not more:
            break
        offset += len(batch)
        time.sleep(pause)
    payload = {"type": "FeatureCollection", "features": feats} if geometry else feats
    out.write_text(json.dumps(payload), encoding="utf-8")
    return out
