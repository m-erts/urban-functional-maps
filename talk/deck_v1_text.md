> This is the text of deck v1, kept as a record. It contains statements and numbers that were later corrected:
> see `docs/ERRATA.md`. The current slides are `docs/slides/index.html`.

# Deck v1: text of the slides and speaker notes

17 slides, prepared in August 2026 for the talk of 3 September 2026.

---
## Slide 1 — title
Eurostat vs OSM vs Census
Choosing Open Mobility Data for Urban Function Maps
What survives when the paid mobile-operator feed is gone — and where exactly the boundary runs
Marija Ercegovac · Senior Geospatial Analyst, Rockup · URBAN_MASH
FOSS4G 2026 Hiroshima · Sep 3, 14:00 · Room 2 · CC BY 4.0
**Notes:** Hook: two years ago this analysis needed a paid operator feed. Today: how far do we get on fully open data, and where exactly is the wall.

## Slide 2 — Three open sources. The 2026 reality check.
What the abstract promised in spring — and what each source turned out to be when I pulled it
- **Eurostat MNO statistics — A standard without data.** Multi-MNO is an open methodological standard in progress. No published cross-country dataset yet. The mature open MNO product today is Japan: MLIT people-flow (NTT docomo).
- **OSM public GPS traces — A behaviour sample of contributors.** Trace density follows mappers, not population. Three city windows: 200k points each, but only 2.4–10k unique minutes; Belgrade median year 2014.
- **Census commuting flows — The anchor — with traps.** Full origin→destination pairs (UK), distance bands only (Serbia, Japan). Free, total-population, no intraday time.
Footer: Eurostat/ESS position paper KS-FT-23-001 · cros.ec.europa.eu Multi-MNO · api.openstreetmap.org/0.6/trackpoints · nomisweb.co.uk
**Notes:** Spring abstract promised three sources. Reality check: Eurostat MNO = Multi-MNO standard, no cross-country dataset yet; the mature open MNO product is Japanese. OSM traces measure contributors. Census is the anchor.

## Slide 3 — Same streets, two communities
Overture Places density (purple) vs OSM public GPS traces (cyan) · H3 res 8
Figure `osm_overture.png`: Belgrade — 200k pts · 5,695 unique minutes · median year 2014 · 35 % in one cell · ρ = +0.67; Hiroshima — 200k pts · 2,395 unique minutes · two campaigns (2019, 2026) · 51 % in one cell · ρ = +0.80
Footer: traces: api.openstreetmap.org/0.6/trackpoints, 40 pages/box · Overture Places 2026-07 · Spearman +0.67 / +0.80 on shared cells
**Notes:** Two open communities, same streets. Ranks correlate — but 51% of Hiroshima trace points sit in ONE cell, and the effective sample is minutes, not points. Overture aggregates half a million sources; a bright line here is one logger.

## Slide 4 — Every source sacrifices one of three dimensions
and the sacrifice is silent — the metadata look perfect
| source | origin→destination pairs | trip purpose | time of day / week |
|---|---|---|---|
| UK census WU/ODWP | full matrix | work only | none |
| Serbia census 2022 | 4 distance bands | work + education (merged) | none |
| Japan MLIT (MNO) | 4 distance bands | none — all presence | month × day/night × wd/hol |
| NL ODiN survey | residence only | full purpose set | yes |
| NL register OD 2006–14 | pairs — but 40 pre-drawn regions | work only | none |
ISO 19157 quality elements all pass on these files. The defect is a sixth kind: correct data answering a different question.
Footer: Surveys give purpose without destination geography · censuses give geography without purpose · only Japan publishes the clock
**Notes:** The core claim of the talk. Read the table slowly. ISO 19157 passes on all of these — the defect metadata cannot express: right data, different question.

## Slide 5 — Where pairs exist, functional areas fall out
England & Wales, census 2021 home→work matrix · 7,264 MSOA · 15.1 M commuters with a fixed workplace
Figure `uk_areas.png`: "Functional areas of England & Wales · Census 2021 home→work flows, home-workers excluded". Left: "Flows only, no geography — 235 areas · 26 non-contiguous · cut-off fragments in coral". Right: "After contiguity repair — fragments handed to adjacent areas · 3 true islands remain". Caption: "An MSOA near Bristol can send 15 % of its commuters to London — 'London' by flows, not on the map." Small print: ONS ODWP01EW · MSOA 2021 BGC boundaries · EPSG:27700 · cores q95, core merge 0.10, attach 0.15
Footer: cores at q95 external inflow · iterative 15 % attachment · coral = fragments cut off from their area
**Notes:** UK: the only case with true pairs. 15.1M commuters, 7264 zones. This is what delimitation needs.

## Slide 6 — Trap 1 · one code category flips the story
Census 2021 place-of-work coding, England & Wales
- **12.6 M** people coded "mainly at home / no fixed place". Their workplace equals their residence — they all land on the diagonal.
- **0.103 → 0.506** the naive 2011→2021 self-containment jump if you keep them. "Britain quintupled its localism." It did not.
- **0.103 → 0.093** the real change once category 1 is excluded. Commuting geometry barely moved — the workforce split instead.
Fixed-workplace commuting: 21.6 M → 15.1 M journeys (−30 %). Home / no-fixed-base: 4.9 M (19 %) → 12.6 M (45 %).
One glance at the code list catches it. Nothing in the file format warns you.
Footer: ODWP01EW category 1 vs 3 · 2011: WU01EW codes OD0000001/3 · both matrices cleaned the same way before any comparison
**Notes:** Trap 1 killed my own first comparison. 12.6M category-1 people sit on the diagonal. Naive story: Britain quintupled localism. Real story: workforce split, geometry unchanged.

## Slide 7 — Trap 2 · aggregation flatters you for free
the null model: same units, same area sizes, assignment random — 60 runs
Chart (native): self-containment — 2011: delimited 0.740 vs random same-size 0.157; 2021: 0.695 vs 0.130.
Earlier, at coarse district level, the null model already scored 0.798 of my proud 0.961 — 80 % of the "result" was arithmetic of bigger boxes.
At MSOA the excess over random is +0.58. The number that looks worse is the correct one.
Run the shuffle before you believe your own map.
Footer: self-containment = trips staying inside their area / all trips · random assignment preserves the size distribution exactly
**Notes:** Trap 2 killed my second result. At district level random scored 0.798 of my 0.961. At MSOA excess is +0.58 — real. Line to land: the number that looks worse is the correct one.

## Slide 8 — Trap 3 · the criterion is open, the algorithm is the moat
reproducing official Travel-to-Work Areas from the same open matrix
- **167** official TTWAs in England & Wales (2011). The validity rule is published: ≥3,500 workers, self-containment on a sliding scale.
- **235** areas my delimitation finds before the size rule — close, looks great, means little: several parameter sets hit ≈230 with different maps.
- **67** areas after enforcing the official rule with a naive merge. London swallows 6.1 M workers. The published criterion + my algorithm ≠ their map.
ONS publishes the validity rule but the placement algorithm (Coombes–Bond) behaviour is what actually draws the boundaries. Open data does not make a method reproducible.
Footer: sliding scale: 3,500 @ 75 % → 25,000 @ 66.7 % · two-sided self-containment · fragments repaired by queen contiguity on MSOA BGC polygons
**Notes:** Trap 3: 235 looks like 167 plus noise — but several parameter sets hit 230 with different maps. Enforcing the official rule naively: 67 areas, London eats 6.1M. Criterion is open; algorithm is the moat.

## Slide 9 — Serbia · bands instead of pairs
census 2022 daily migrations · 168 municipalities · 795,779 workers
Figure `rs_selfcont.png`: left "Work self-containment — share of daily migrants staying in their municipality · Census 2022" (colorbar "RBSC" 0–1); right "Education minus work — green = education commuting is MORE local than work" (diverging −0.3…+0.3). Caption: "Hatched: 8 single-settlement municipalities where the metric is structurally zero — a definition artefact, not a finding." Small print: SORS Popis 2022 · boundaries GeoSrbija, Kosovo excluded · EPSG:32634 · pupils and students are published as one number
Footer: no origin→destination matrix exists — self-containment is computable, delimitation is not
**Notes:** Serbia has no matrix at all — four distance bands. You can still do self-containment honestly.

## Slide 10 — What bands still buy you — if you respect the definition
three findings, one artefact
- **50.3 %** of Serbian daily migrants stay inside their municipality. Median municipality: 0.53.
- **+0.08** education commuting is systematically MORE local than work (median 0.65 vs 0.53, r = 0.82) — one non-work purpose is open, but pupils and students are one merged number.
- **0.00** self-containment of 8 single-settlement municipalities. A daily migrant is defined as leaving the SETTLEMENT — for them any migrant leaves. Artefact, not finding.
Urbanisation does not explain the education–work gap: correlation +0.03 against GHS-SMOD degree-of-urbanisation (population-weighted, DEGURBA logic).
First pass used area share of urban classes and "found" r = −0.28. Half the municipalities have zero urban area — the correlation was noise. Weight by population, not pixels.
Footer: SORS Popis 2022 · GHS-SMOD/POP R2023A Mollweide · shapefile encoding destroyed Cyrillic names — matching needs exact-first, pattern-second, Kosovo excluded
**Notes:** Education is MORE local than work — one open non-work purpose exists. Zeros are a definition artefact: name them, don't interpret them. Urbanisation does not explain the gap — and mention the area-vs-population weighting trap.

## Slide 11 — Netherlands · pairs exist — pre-aggregated into the answer
CBS register OD 81252NED · jobs by residence × workplace region · discontinued after 2014
- **0.66** median self-containment of COROP regions in 2014 — regions that were DESIGNED as commuter basins in 1970. Only 20 % still pass the 75 % test.
- **2** functional areas my delimitation finds on top of the 40 regions. The whole Randstad + the north collapses into one labour market; the south is the other.
- **40×40** the only resolution the OD is published at. You cannot re-draw basins from data aggregated to the 1970 answer — the circularity is invisible in the metadata.
Resolution is a policy choice. Publishing flows only inside half-century-old functional boundaries makes those boundaries unfalsifiable.
Footer: opendata.cbs.nl 81252NED · 7.54 M jobs, Dec 2014 · most open COROP: Delfzijl 0.45 · most closed: Zeeuwsch-Vlaanderen 0.88
**Notes:** The only Dutch OD is register-based jobs, aggregated to COROP regions - which were themselves drawn as commuter basins in 1970. Median self-containment of those basins is now 0.66, only 20 percent pass the TTWA test, and delimitation on top returns two areas: the Randstad is one labour market. Resolution is a policy choice.

## Slide 12 — Japan · the clock censuses never see
MLIT people-flow open data = aggregated anonymised MNO (NTT docomo)   ← FACTUAL ERROR, see review §1.1
Figure `jp_daynight.png`: "Population presence, Hiroshima agglomeration · weekday, October 2019". Left "Where people sleep 深夜" (people per 1 km² cell, log 10¹–10⁴). Right "Where they go by day 昼/深夜" (ratio ×0.13…×7.9, diverging blue–yellow). Caption: "Yellow: 2×+ more people by day than by night — job clusters. Blue: dormitory areas. Censuses cannot see this axis at all." Small print: MLIT 全国の人流オープンデータ (NTT docomo) · 1 km mesh JIS X 0410 · values under 10 suppressed · volumes normalised, compare composition only
Footer: weekday October 2019 · central Hiroshima ward: 27 % of daytime presence is local residents — three quarters commute in
**Notes:** Japan gives the axis nobody else has: the clock. Central ward: 27% locals by day. This is what we paid operators for.

## Slide 13 — Temporal signatures — the honest version
the abstract promised HDBSCAN. HDBSCAN answered: there are no clusters.
Figure `jp_signatures.png`: "Temporal signatures from open MNO data · Hiroshima city, 2019 average". Legend: Mixed — flat profile (155); Residential — nights dominant (102); Leisure / retail — holiday-day dominant (50); Office / industrial — weekday-day dominant (115). Caption: "Axes: log₂(weekday day/night) and log₂(holiday/weekday day), 1.5× thresholds, cells ≥100 people. HDBSCAN finds a continuum, not clusters — cuts here are declared, not discovered." Small print: MLIT people-flow open data · profile = 2019 monthly mean · delta area: leisure strip along the rivers, office core, residential slopes
- Density-based clustering on composition profiles returns one continuum (100 % noise at honest settings).
- k-means would have happily cut "4 functional classes" anyway.
- So the cuts are declared thresholds on two named axes — visible, criticisable, reproducible.
Footer: axes: log₂(weekday day/night), log₂(holiday/weekday) · 1.5× thresholds · cells ≥ 100 people · 2019 monthly mean
**Notes:** Honesty slide: HDBSCAN refuses to find clusters — the space is a continuum. Declared thresholds beat discovered fictions.

## Slide 14 — Two caveats that must be said from the stage
before someone says them from the floor
- **±0.3 %** total presence volume across 2019 / 2020 / 2021 is IDENTICAL — the series is normalised. Never compare volumes across years; only composition. (Composition does move: weekday local share 0.632 → 0.677 in 2020.)
- **"From–To"** the file name promises an OD matrix. from_area is four nested distance bands — same structure as the Serbian census. Read the 定義書 before the filename.
Footer: MLIT データ定義書 p.6 · 2019–2021 window includes COVID · values under 10 people suppressed
**Notes:** Say both caveats before Q&A does: volumes are normalised (compare composition only), and From-To is not an OD matrix.

## Slide 15 — The decision matrix
what to reach for first — and what to check before trusting it
| you need | reach for | before trusting, check |
|---|---|---|
| commuting structure, delimitation | census OD pairs (UK-style; EU Census Hub at NUTS-2) | special place-of-work codes; null model; contiguity |
| intraday presence, day/night | MNO-derived products (JP MLIT today; Eurostat Multi-MNO when it ships) | volume normalisation; suppression threshold; band definitions |
| self-containment where no matrix exists | census distance bands (RS, JP) | the migrant DEFINITION — settlement vs municipality |
| fine-grain routes / activity traces | OSM GPS traces | contributor bias: density follows mappers, not people |
Where sources agree, classification is robust. Where they diverge, the divergence is the finding.
**Notes:** The promised takeaway. Pairs->census; clock->MNO; no matrix->bands with definition check; traces->contributor bias.

## Slide 16 — Three checks that cost an afternoon
and each of them killed one of my own results this month
1. **Shuffle** — Rebuild your areas with random assignment of the same sizes. If random scores 80 % of your result, your result is the aggregation.
2. **Read the code list** — Every special category (home workers, offshore, no fixed place) — where does it land in YOUR denominator? 12.6 M people flipped a national trend.
3. **Draw it** — Join the geometry and look. A 587 km² Kosovo polygon wearing Belgrade data, a red Hiroshima, a fragmented London — none were visible in the tables.
Footer: pipeline: Python · GeoPandas · DuckDB · PostGIS-ready · full repo published under CC BY 4.0 after the talk
**Notes:** Closing argument: three checks, one afternoon, each killed one of my results this month. Shuffle, read the code list, draw it.

## Slide 17 — closing
The blind spot is not missing data. It is the dimension your source silently sacrificed.
Marija Ercegovac · URBAN_MASH · talks.osgeo.org/foss4g-2026
slides + code: CC BY 4.0 · questions welcome — the room has no microphone, I will repeat every question
**Notes:** Repeat questions — no microphone in this room.
