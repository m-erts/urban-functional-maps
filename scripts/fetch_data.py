"""Fetch the inputs that have a stable public address and check every file against the manifest.

    python scripts/fetch_data.py            download what is missing, then verify checksums
    python scripts/fetch_data.py --verify   verify only

Files that need a manual step (a portal with a form or a login) are listed with their address.
Nothing is overwritten. Raw data are never committed.
"""

import argparse
import hashlib
import sys
from pathlib import Path

import requests
import yaml

from omfm.config import ROOT, params, path
from omfm.sources import nl_cbs, osm_traces
from omfm.sources.arcgis import fetch_layer

MANIFEST = ROOT / "data" / "manifest.yaml"
UA = {"User-Agent": "omfm/1.0 (+https://github.com/m-erts/urban-functional-maps)"}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, headers=UA, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(out, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)


def main(verify_only: bool) -> int:
    entries = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["files"]
    manual, bad = [], []
    for e in entries:
        out = path("raw", e["path"]) if e.get("root", "raw") == "raw" else ROOT / e["path"]
        if not out.exists() and not verify_only:
            how = e.get("fetch", "manual")
            try:
                if how == "http":
                    print(f"download  {e['path']}")
                    download(e["url"], out)
                elif how == "arcgis":
                    print(f"download  {e['path']}")
                    fetch_layer(e["url"], out, geometry=out.suffix == ".geojson", page=e.get("page", 2000))
                elif how == "osm_api":
                    name = out.stem.replace("osm_traces_", "")
                    print(f"download  {e['path']} (about one minute)")
                    osm_traces.fetch_window(name, params()["osm_traces"]["windows"][name], out)
            except Exception as err:  # keep going, report at the end
                print(f"  failed: {err}")
        if not out.exists():
            manual.append(e)
            continue
        if e.get("sha256") and e.get("stable", True):
            if sha256(out) != e["sha256"]:
                bad.append(e["path"])
    if not verify_only:
        nl_cbs.fetch()
    for e in manual:
        print(f"MISSING   {e['path']}\n          get it from {e['url']}\n          {e.get('note', '')}")
    for p in bad:
        print(f"CHECKSUM  {p} differs from the manifest: the publisher changed the file, or the download is broken")
    print(f"{len(entries) - len(manual)} of {len(entries)} files present, {len(bad)} checksum mismatches")
    return 1 if (manual or bad) else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true")
    sys.exit(main(ap.parse_args().verify))
