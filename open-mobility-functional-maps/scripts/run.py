"""Pipeline entry point: python scripts/run.py {fetch|interim|analysis|figures} [--only uk,rs,nl,jp,osm,es]."""
import argparse
import importlib

from omfm.io import params

SOURCES = {"uk": "uk_census", "rs": "serbia_census", "nl": "nl_cbs", "jp": "jp_mlit", "osm": "osm_traces",
           "overture": "overture", "ghsl": "ghsl", "es": "spain_mitma"}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["fetch", "interim", "analysis", "figures"])
    ap.add_argument("--only", default=",".join(SOURCES))
    a = ap.parse_args()
    cfg = params()
    for key in a.only.split(","):
        mod = importlib.import_module(f"omfm.sources.{SOURCES[key]}")
        if a.stage == "fetch":
            mod.fetch(cfg)
        elif a.stage == "interim":
            mod.load(cfg)
        else:
            raise NotImplementedError(f"{a.stage} for {key}: implement in omfm.analysis / omfm.viz")
