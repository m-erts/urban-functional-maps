# Backlog

Generated from `docs/backlog.yaml`. P0 = must, P1 = should, P2 = could.

## M0 — Recovery & scaffold
- [ ] **P0** Place v1 pptx in talk/ and run scripts/extract_deck.py  `talk`
- [ ] **P0** Search Mac for legacy code/figures from Cowork session practical-upbeat-brown; import as-is into legacy/  `recovery`
- [ ] **P0** Pinned conda env + Dockerfile + docker-compose (PostGIS) working  `infra`
- [ ] **P0** GitHub Actions CI: ruff + pytest (unit tests without data)  `infra`
- [ ] **P1** Marija: record what was asked in Q&A on 3 Sep and which review fixes made it into the delivered deck  `talk`
- [ ] **P1** Decide: publish docs/internal (Russian review) or move to private  `meta`

## M1 — UK pipeline (slides 5–8)
- [ ] **P0** Fetch + clean ODWP01EW (2021) and WU01EW (2011); exclude home/no-fixed-place identically  `uk, data`
- [ ] **P0** Unit diagonal share: reproduce 0.103 / 0.506 / 0.093  `uk, golden`
- [ ] **P0** Own delimitation (q95 cores, 0.10 merge, 0.15 attach) → 235 areas, 26 non-contiguous  `uk`
- [ ] **P0** Queen contiguity repair → 3 islands  `uk`
- [ ] **P0** Null model 60 runs with sd; MSOA and LAD level (0.961 vs 0.798)  `uk, golden`
- [ ] **P0** TTWA validity rule + naive merge → 67 areas, London 6.1M; verify Coombes-Bond trade-off formula  `uk`
- [ ] **P1** Run Istat LabourMarketAreas (R) on same matrix; 3-map comparison with ARI vs official TTWA 2011  `uk, new`
- [ ] **P1** Parameter sensitivity: several parameter sets ≈230 areas with different maps (triptych)  `uk, viz`
- [ ] **P1** Add lockdown context (21 Mar 2021, ONS guidance) to docs and figure captions  `uk, docs`

## M2 — Serbia + NL (slides 9–11)
- [ ] **P0** Serbia: fetch SORS daily migrations + boundaries; robust Cyrillic name matching with unmatched log  `rs, data`
- [ ] **P0** Serbia: self-containment work/education, artefact flag for 8 single-settlement municipalities  `rs, golden`
- [ ] **P0** GHSL population-weighted urbanisation; keep area-share as negative control  `rs`
- [ ] **P0** Regression test: no polygon inherits another unit's values (587 km² bug); Kosovo* footnote  `rs, test`
- [ ] **P1** Serbia maps: colour-blind-safe diverging palette, decode RBSC, outline artefacts  `rs, viz`
- [ ] **P0** NL: 81252NED COROP 2014 two-sided SC, delimitation → 2 (labelled artefact)  `nl, golden`
- [ ] **P1** NL: extend to 83628NED and 85481NED; fix 'discontinued' wording  `nl`

## M3 — Japan (slides 12–14)
- [ ] **P0** Japan: verify provider in データ定義書 (Agoop vs docomo); fix all labels  `jp, facts`
- [ ] **P0** Japan: fetch Hiroshima MLIT mesh; day/night map Oct 2019 weekday; local share of central ward  `jp, golden`
- [ ] **P0** Japan: normalisation check (±0.3 %) and composition 0.632→0.677  `jp, golden`
- [ ] **P0** Signatures: declared thresholds → 155/102/50/115; decide precedence  `jp, golden`
- [ ] **P0** HDBSCAN sweep + Hopkins statistic + k-means silhouette contrast  `jp, ml`
- [ ] **P0** Continuum scatter with threshold lines and worded quadrants (key missing figure)  `jp, viz`
- [ ] **P1** Third caveat: panel coverage of Agoop app-GPS  `jp, docs`
- [ ] **P2** Japan census OD pairs (e-Stat) as fourth census case; link to 都市雇用圏  `jp, new`

## M4 — OSM traces vs Overture (slide 3)
- [ ] **P0** OSM trackpoints fetcher (pagination, rate limit, cache, private-trace handling)  `osm, data`
- [ ] **P0** Unique minutes, median year, top-cell share, Spearman vs Overture H3 r8  `osm, golden`
- [ ] **P0** Decisive test: rho(traces, MLIT daytime) vs rho(traces, Overture) in Hiroshima  `osm, new`
- [ ] **P1** Third window or fix 'three windows' claim  `osm`

## M5 — Spain MITMA + promised extras
- [ ] **P1** Spain MITMA: Madrid day/night + hourly intraday profiles  `es, new`
- [ ] **P2** Urban Atlas polygons + DEGURBA as common reference (or drop in README)  `promise`
- [ ] **P2** OSRM travel time to area core (or remove from programme page)  `promise`
- [ ] **P2** QGIS: GeoPackage of all layers + .qgz with styles; PostGIS export  `promise`

## M6 — Deck v2, README, release v1.0
- [ ] **P0** Deck v2 with all P0 fixes (review §1–2); regenerate figures from code  `talk`
- [ ] **P0** README with corrected decision matrix, data licences, how to reproduce  `docs`
- [ ] **P1** All golden values reproduced or differences documented  `golden`
- [ ] **P1** Zenodo DOI, CITATION.cff, release v1.0; link from pretalx  `release`
- [ ] **P2** Blog post / URBAN_MASH write-up; proceedings text if applicable  `outreach`
