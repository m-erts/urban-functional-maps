"""Pipeline entry point.

python scripts/run.py analysis [--only uk,uk_sweep,rs,nl,jp,osm]
python scripts/run.py figures
python scripts/run.py register [--freeze]
python scripts/run.py all
"""

import argparse

from omfm import pipeline

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["analysis", "figures", "register", "all"])
    ap.add_argument("--only", default=None, help="comma-separated cases: " + ",".join(pipeline.CASES))
    ap.add_argument("--freeze", action="store_true", help="rewrite the regression snapshot tests/golden_values.yaml")
    a = ap.parse_args()
    if a.stage in ("analysis", "all"):
        pipeline.run(a.only.split(",") if a.only else None)
    if a.stage in ("figures", "all"):
        from omfm.viz import figures

        figures.all_figures()
    if a.stage in ("register", "all"):
        from omfm import register

        register.write(freeze=a.freeze)
