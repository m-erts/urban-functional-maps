# The talk

**Eurostat vs OSM vs Census: Choosing Open Mobility Data for Urban Function Maps**
Accepted for the general track of FOSS4G 2026, Hiroshima; scheduled for 2026-09-03, 14:00 to 14:30 JST.
The author was unable to present it. The slides, the paper and the code prepared for it are published in this repository.
Speaker: Marija Ercegovac · Licence of the contribution: CC BY 4.0
Programme: https://talks.osgeo.org/foss4g-2026 · Conference: https://2026.foss4g.org/en/program-schedule/

## Abstract (as submitted, verbatim)

Which open mobility dataset should you trust for urban function analysis? Using Copernicus Urban Atlas polygons, we compare Eurostat experimental MNO statistics, OpenStreetMap GPS traces, and census commuting flows. You will learn their biases, and get a fully reproducible Python/PostGIS workflow.

Open mobility data is everywhere, but different sources answer different questions -- and the differences are easy to miss until results conflict. This talk presents a reproducible, open-source workflow to compare three widely accessible mobility proxies on a common spatial reference.

Using Copernicus Urban Atlas polygons and the DEGURBA classification (derived from 1 km2 population grid cells), we convert each source into comparable density-normalised temporal indicators (day/night ratios, intraday profiles, weekday/weekend patterns). The three sources:
- Eurostat experimental MNO statistics (aggregated, anonymised mobile network operator statistics published by national statistical offices)
- OpenStreetMap public GPS traces (community-contributed trace archive; participation bias applies)
- Census commuting flows from Eurostat (static origin-destination baseline)

We apply a simple clustering step (HDBSCAN) to group similar temporal profiles into functional signatures (residential, office, late-evening activity, mixed-use), and use UMAP only as a visual explanation aid. Instead of selling one "best" dataset, we provide a practical decision guide: which source is best for presence vs flows, what biases to expect, and how to combine sources when a single source falls short.

Early findings: MNO statistics capture temporal presence well but availability and comparability vary by country; OSM GPS traces reflect contributor behaviour more than population-level patterns; census flows miss intraday dynamics but anchor the OD baseline. Where sources agree, classification is robust; where they diverge, the divergence reveals structural data limitations worth knowing.

What you take away:
- A decision matrix with concrete rules of thumb (e.g., intraday presence -- start with MNO; commuting structure -- census OD; fine-grain routes/activities -- OSM, with known participation bias)
- Typical biases and coverage gaps of each source across different European urban contexts
- A reproducible pipeline: Python + PostGIS + OSRM + QGIS-ready layers and scripts

We will publish the full pipeline as an open repository (Docker/conda, pinned environments, end-to-end scripts to regenerate figures and maps).

This talk is for anyone choosing open mobility data for urban analysis who wants to stop guessing and start comparing.

Level of technical complexity: 2 – intermediate.

**Essential open-source projects (declared):** PostgreSQL + PostGIS; QGIS; Python; GeoPandas; OSRM; OpenStreetMap; Docker; scikit-learn; hdbscan; umap-learn.

**Advance reading (declared):**
1. Eurostat/ESS position paper on MNO data for official statistics — https://ec.europa.eu/eurostat/documents/7870049/17468840/KS-FT-23-001-EN-N.pdf
2. DEGURBA methodology — https://ec.europa.eu/eurostat/web/degree-of-urbanisation/methodology
3. Copernicus Urban Atlas — https://land.copernicus.eu/en/products/urban-atlas
4. CLMS data policy — https://land.copernicus.eu/en/data-policy
5. OSM copyright & licence (ODbL) — https://www.openstreetmap.org/copyright
6. OSRM backend — https://github.com/Project-OSRM/osrm-backend

## Speaker bio (as submitted)
Senior Geospatial Analyst at Rockup, building neighborhood analytics tools. Previously Geospatial Researcher (R&D) at Habidatum, developing cross-country urban mobility pipelines for European policy institutions — OD matrices, temporal land-use profiling, service accessibility mapping across 16 countries. Former geospatial data scientist at Yandex (GeoAI prediction models, spatial feature engineering). Invited lecturer on geospatial data science (MIPT Deep Learning School) and QGIS (RheinMain University). Jury member at IAAC Barcelona. Daily tools: Python, GeoPandas, PostGIS, QGIS. Admitted to MSc Geomatics at TU Delft. Runs URBAN_MASH (2,200+ subscribers).

## What the abstract announced and what is in this repository

| Announced in the abstract | In this repository |
|---|---|
| Eurostat experimental MNO statistics | No cross-country dataset exists. The Spanish national product, trips between districts from operator data with purpose and hour, is the nearest open equivalent and is analysed. The Japanese people-flow panel is used for time of day, under its right name: a panel of smartphone applications, not operator data |
| OpenStreetMap public GPS traces | Three windows: Hiroshima, Belgrade, London. Sample statistics only; the comparison with presence and places had eleven shared cells and is not reported |
| Census commuting flows from Eurostat | National sources: England and Wales (census pairs), the Netherlands (register pairs between municipalities, 2023; between 40 regions, 2014), Serbia (bands). Functional areas by the Coombes-Bond algorithm (R package LabourMarketAreas) and by a heuristic |
| Copernicus Urban Atlas polygons as common reference | Not used. Each source is analysed on its own units |
| DEGURBA classification | Degree of urbanisation from GHS-SMOD, weighted by GHS-POP population, for Serbian municipalities |
| Day/night ratios, intraday profiles, weekday and weekend patterns | Japan: day/night and weekday/holiday; the data have no hourly profile. Spain: trips by hour of departure and purpose |
| HDBSCAN functional signatures | Run and reported: no partition into classes. Classes are declared thresholds |
| UMAP as a visual aid | Not used |
| Python and PostGIS workflow, QGIS-ready layers | Python pipeline; `omfm.io.to_gpkg` and `to_postgis` write any layer |
| OSRM | Not used |
| Docker and conda, pinned environments, end-to-end scripts | `environment.yml`, `requirements.lock`, `Dockerfile`, `make all` |
| Decision matrix | In the README, the paper (Section 5) and the slides |

The text of deck v1 with speaker notes is in `talk/deck_v1_text.md`. Version 2 of the slides is in `docs/slides/`. Corrections: `docs/ERRATA.md`.
