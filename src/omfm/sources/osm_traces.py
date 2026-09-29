"""OSM public GPS trackpoints for a bounding box, through the OSM API.

The API returns 5,000 points per page. Forty pages give 200,000 points: that number is the
size of the request, not a property of the city. The API serves the archive as it is on the
day of the request, so a later download of the same window returns other points; the files
used for the published numbers are identified by checksum in ``data/manifest.yaml``.
"""

from __future__ import annotations

import csv
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

from ..config import params, path

NS = {"gpx": "http://www.topografix.com/GPX/1/0"}
UA = {"User-Agent": "omfm/1.0 (+https://github.com/m-erts/urban-functional-maps)"}


def fetch_window(name: str, bbox: list[float], out: Path | None = None, pause: float = 1.0) -> Path:
    """Download up to ``pages_per_box`` pages for one window (lon_min, lat_min, lon_max, lat_max)."""
    cfg = params()["osm_traces"]
    out = out or path("raw", f"OSM/osm_traces_{name}.csv", mkdir=True)
    if out.exists():
        return out
    rows = []
    for page in range(cfg["pages_per_box"]):
        r = requests.get(cfg["api"], params={"bbox": ",".join(map(str, bbox)), "page": page}, headers=UA, timeout=60)
        if r.status_code != 200:
            break
        pts = ET.fromstring(r.content).findall(".//gpx:trkpt", NS)
        if not pts:
            break
        for p in pts:
            t = p.find("gpx:time", NS)
            rows.append((p.get("lat"), p.get("lon"), t.text if t is not None else ""))
        time.sleep(pause)  # the API usage policy asks for restraint
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["lat", "lon", "time"])
        w.writerows(rows)
    return out
