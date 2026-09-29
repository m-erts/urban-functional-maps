# CLAUDE.md — open-mobility-functional-maps

Project memory for Claude Code. Read this first, then `docs/internal/00_HANDOFF.md`.

## What this project is
Reproducible open-source pipeline behind the FOSS4G 2026 Hiroshima talk
**"Eurostat vs OSM vs Census: Choosing Open Mobility Data for Urban Function Maps"**
(Marija Ercegovac, 3 Sep 2026, 14:00, Room 2; talk 2 of the author's FOSS4G slots).
Core claim: every open mobility source silently sacrifices one of three dimensions —
**origin→destination pairs, trip purpose, time of day/week** — and three cheap checks
(**shuffle / read the code list / draw it**) catch the resulting errors.

The talk promised: "full pipeline as an open repository (Docker/conda, pinned environments,
end-to-end scripts to regenerate figures and maps)" under CC BY 4.0. **That promise is not yet
fulfilled — delivering it is the goal of this repo.**

## Current state (as of 2026-09-29)
- The original analysis code was written in an earlier Claude Cowork session
  (figure paths in the deck: `/sessions/practical-upbeat-brown/mnt/outputs/deck2_assets/*.png`).
  That session's scratch folder is ephemeral → **the original scripts are probably lost**
  unless Marija saved them locally. First task: ask her / search her disk (see HANDOFF §2).
- Everything needed to REBUILD is specified: parameters (`config/params.yaml`),
  methods (`docs/03_METHODOLOGY.md`), every number shown on stage
  (`tests/golden_values.yaml` = regression targets), data sources (`docs/02_DATA_SOURCES.md`).
- A critical review of the deck exists (`docs/internal/05_REVIEW_FINDINGS.md`) with verified
  factual errors that MUST be fixed in the published version (see "Known factual errors").

## Known factual errors in the v1 deck (do not propagate into code, README or figures)
1. MLIT 全国の人流オープンデータ is **not NTT docomo / not MNO network data**. Provider per
   G空間情報センター + Urban Data Challenge: **株式会社Agoop** (SoftBank group), smartphone
   app-GPS panel expanded to population. Verify against the データ定義書 before writing labels.
2. "Only Japan publishes the clock" / "Eurostat MNO: a standard without data" is contradicted by
   **Spain MITMA open hourly MNO OD (2020–2021, 2022–present)**. Treat Spain as a first-class source.
3. Japanese **census** DOES publish municipal OD pairs (常住地×従業地, e-Stat); "bands only" applies
   to the MLIT From-To file, not the census.
4. NL: 81252NED ended 2014 but successors exist (83628NED 2014–2020, 85481NED current) — still
   regional (the "40-region cage" argument survives, "discontinued" does not).
5. UK census 2021 = 21 March 2021, mid-lockdown; ONS itself recommends continuing to use 2011 TTWAs.

## Conventions
- Language: code, docs, README, commit messages in **English** (public repo, international
  audience). Chat with Marija in **Russian**.
- Python ≥3.11, GeoPandas, DuckDB (+spatial), h3, scikit-learn, hdbscan; PostGIS optional
  ("PostGIS-ready": every output also writable to PostGIS via `omfm.io.to_postgis`).
- Layout: `src/omfm/sources/<source>.py` = fetch + clean one source → tidy parquet in
  `data/interim/`; `src/omfm/analysis/*.py` = pure functions (no I/O), unit-testable;
  `scripts/` = thin CLI entry points; `src/omfm/viz/` = figures, one function per deck figure.
- All parameters live in `config/params.yaml`. No magic numbers in code.
- CRS: store in EPSG:4326 in interim; analyse in the local projected CRS listed per source.
- **Raw data is never committed.** `data/manifest.yaml` records URL, version/date, licence,
  sha256. Fetch scripts must be idempotent and verify checksums.
- Figures: matplotlib, shared style `src/omfm/viz/style.py` (deck palette, colour-blind-safe
  diverging maps — NOT red/green), fonts matching the deck; every map carries attribution.
- Every number that appears on a slide must be produced by code and asserted in
  `tests/golden_values.yaml` (tolerance per value). If a reproduced number differs from the deck,
  do NOT tweak parameters to match — report the difference to Marija.
- Licences: code MIT (`LICENSE`), text/figures/slides CC BY 4.0 (`LICENSE-CONTENT`).
  Data licences in `docs/02_DATA_SOURCES.md` — OSM ODbL attribution, Overture attribution,
  ONS OGL v3, CBS CC BY 4.0, MLIT 政府標準利用規約, GHSL CC BY 4.0, SORS terms.
- Sensitive wording: Serbia census does not cover Kosovo → write "Kosovo*" with the
  UNSCR 1244 footnote; describe the join bug technically ("unmatched polygon inherited
  another unit's values").

## Commands (target — implement them)
```
make env          # conda env from environment.yml (pinned)
make fetch        # all sources → data/raw (checksummed)
make interim      # clean → data/interim/*.parquet
make analysis     # all metrics → outputs/tables
make figures      # all deck figures → outputs/figures
make test         # pytest incl. golden values
make all          # end-to-end
docker build -t omfm . && docker run --rm -v $PWD/data:/app/data omfm make all
```

## Working rules for Claude
- Before any factual claim in docs/README about a dataset (provider, years, licence, granularity),
  check the primary source; cite the URL in `docs/02_DATA_SOURCES.md`.
- Implement source by source, each with a test, in the order of `docs/06_BACKLOG.md`.
- Keep `docs/04_RESULTS_REGISTER.md` and `tests/golden_values.yaml` in sync.
- Use `/repro-check`, `/fact-check`, `/slide-sync` commands in `.claude/commands/`.
