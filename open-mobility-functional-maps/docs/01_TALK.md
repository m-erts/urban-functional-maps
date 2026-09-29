# The talk

**Eurostat vs OSM vs Census: Choosing Open Mobility Data for Urban Function Maps**
FOSS4G 2026 Hiroshima · 2026-09-03 14:00–14:30 JST (07:00–07:30 Europe/Belgrade) · Room 2
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

## Promise ledger — abstract vs. v1 deck vs. this repo

| Promised in abstract | v1 deck (3 Sep) | Repo target |
|---|---|---|
| Eurostat experimental MNO statistics | replaced: no EU-wide dataset; Japan MLIT used (mislabelled as docomo/MNO — it is Agoop app-GPS) | MLIT (correct label) **+ Spain MITMA** as the real open MNO; Eurostat `multimno` code referenced |
| OSM public GPS traces | ✅ Belgrade, Hiroshima (a third window was mentioned but not shown) | + third window or text fix; + MLIT ground-truth test |
| Census commuting flows "from Eurostat" | UK (pairs), Serbia (bands), NL register OD (40 regions) | + FR MOBPRO / DE BA / JP census pairs in decision matrix |
| Copernicus Urban Atlas polygons | ❌ not used (GHS-SMOD instead) | implement or explicitly drop in README |
| DEGURBA classification | partial: GHS-SMOD population-weighted DEGURBA logic (Serbia) | ✅ keep; document |
| intraday profiles | ❌ MLIT has only day/night | MITMA hourly → real intraday profiles |
| HDBSCAN functional signatures | ✅ negative result: 100 % noise → declared thresholds | + Hopkins statistic, parameter sweep, continuum scatter |
| UMAP visual aid | ❌ dropped (deliberately) | document why (Chari & Pachter 2023) |
| PostGIS workflow | "PostGIS-ready" | `omfm.io.to_postgis` + docker-compose PostGIS |
| OSRM | ❌ | travel time to nearest core / validate delimitation — or drop and edit programme page |
| QGIS-ready layers | ❌ | GeoPackage + .qgz project with styles |
| Docker/conda, pinned env, end-to-end scripts | ❌ | ✅ this repo |
| Decision matrix | ✅ slide 15 | corrected rows (Spain, Agoop, census pairs) in README |
