# CLAUDE.md

Project memory for Claude Code.

## What this is

Pipeline, paper and slides on open mobility data for functional-area maps, prepared for FOSS4G 2026, Hiroshima.
The documents say "prepared for" and claim nothing about the session; do not write that the talk was given unless the author says so.
Repository: https://github.com/m-erts/urban-functional-maps. Author: Marija Ercegovac.

## Rules

- Public text is in English. Talk to the author in Russian.
- No number is typed into a document. `README.md`, `docs/paper/paper.md`, `docs/slides/index.html` and
  `docs/outreach/linkedin.md` are rendered from `templates/` by `scripts/render_docs.py`; edit the template.
- If a recomputed number differs from an earlier one, report the difference. Never change a parameter to
  make a number agree.
- All parameters are in `config/params.yaml`.
- Raw data are never committed. Every input is in `data/manifest.yaml` with address, licence and SHA-256.
- Figures follow `DESIGN.md`: census amber, OpenStreetMap green, Eurostat-type grid and presence blue.
  No shadows, no gradients. Every map carries the attribution of its source.
- The 2022 census of Serbia does not cover Kosovo*; keep the footnote (UNSCR 1244/1999) wherever Serbia is mapped.
- Before stating a fact about a dataset, find the primary source. Known traps: `docs/ERRATA.md`.

## Commands

```
python scripts/fetch_data.py            inputs
python scripts/run.py analysis          all cases; --only uk,uk_sweep,uk_cases,rs,nl,jp,osm
python scripts/run.py figures
python scripts/run.py register          docs/RESULTS.md; --freeze rewrites tests/golden_values.yaml
python scripts/render_docs.py           documents from templates; --check in CI
bash scripts/build_pdf.sh               paper and slides as PDF
pytest -q ; ruff check src tests scripts
```

## Layout

`src/omfm/sources` read and reconcile one source each. `src/omfm/analysis` are pure functions.
`src/omfm/pipeline.py` writes `outputs/tables` and `golden_actual.yaml`. `src/omfm/viz/figures.py` draws
from the tables into `docs/figures`.
