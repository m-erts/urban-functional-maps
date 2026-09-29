# Methodology

Reconstructed from the v1 slides, speaker notes and figure captions. Where the deck is silent the
item is marked **[DECIDE]** — recover it from legacy code if found, otherwise choose, document here,
and add to `config/params.yaml`. Parameters: `config/params.yaml`. Targets: `tests/golden_values.yaml`.

## 0. Frame: the three dimensions
Every source is scored on: (1) origin→destination pairs, (2) trip purpose, (3) time of day/week.
The "sacrifice matrix" (slide 4) is data: `docs/sacrifice_matrix.csv` should be generated from
source metadata, not typed. Framing against ISO 19157: the five computable quality element groups pass;
the failure is **usability / fitness for a stated purpose** (ISO 19157 usability element).

## 1. OSM public GPS traces vs Overture Places (slide 3)
1. Fetch trackpoints per window: `GET /api/0.6/trackpoints?bbox=…&page=0..39` (5,000 pts/page) →
   cap = 200,000 points/window. Record that 200k is a cap, not a property of the data.
2. Parse GPX; keep lat, lon, time, trace id (if identifiable). Private traces have no time — count separately.
3. Effective sample: `unique minutes` = n distinct `floor(time, 1 min)`; median year of points.
4. Aggregate to H3 res 8 (`h3.latlng_to_cell`); concentration = max cell share ("35 % / 51 % in one cell").
5. Overture Places (release 2026-07) within the window via DuckDB → H3 res 8 counts.
6. Spearman ρ between trace counts and place counts on shared cells [DECIDE: cells with both > 0, or union with zeros — report both].
7. **New test (review §2.3):** in Hiroshima, ρ(traces, MLIT daytime presence) vs ρ(traces, Overture). If the
   latter ≫ former → traces follow mappers, not people. Aggregate MLIT 1 km mesh to H3 via area-weighting or
   compare on the 1 km mesh.
Figure: `viz.osm_overture` — two panels, purple = places (with legend!), cyan = traces, attribution line.

## 2. UK — census OD pairs (slides 5–8)
### 2.1 Cleaning
- 2021: ODWP01EW MSOA→MSOA; drop place-of-work categories "mainly at/from home" and "no fixed place"
  (they are coded at the residence → sit on the diagonal). 2011: WU01EW; drop OD0000001 and OD0000003
  (also exclude OD0000002 offshore, OD0000004 outside UK from pairs). Clean both years identically.
- Harmonise 2011 MSOAs to 2021 via the ONS lookup [DECIDE: or run each year on its own geography].
- Result: 15.1 M fixed-workplace commuters over 7,264 MSOAs (2021); 21.6 M (2011).
### 2.2 Self-containment
- Unit-level diagonal share (Trap 1): `Σ_i T_ii / Σ_ij T_ij` over units → 0.103 (2011) vs 0.093 (2021 cleaned), 0.506 (2021 naive).
- Area-level (Trap 2): `SC = Σ_a Σ_{i,j∈a} T_ij / Σ_ij T_ij` for a partition of units into areas.
- Per-area two-sided (Trap 3): supply-side `SCs = residents working in a / employed residents of a`;
  demand-side `SCd = jobs in a filled by residents / jobs in a`; two-sided = `min(SCs, SCd)`.
### 2.3 Delimitation (own heuristic, NOT the ONS algorithm)
1. External inflow per unit = commuters arriving from other units. Cores = units with inflow ≥ q95.
2. Merge cores whose mutual flow share ≥ 0.10 [DECIDE: share of which side — smaller core's outflow?].
3. Iterative attachment: each non-core unit joins the area receiving the largest share of its outgoing
   commuters if that share ≥ 0.15; repeat until no change [DECIDE: order, treatment of never-attached units].
4. Result "flows only": 235 areas, 26 non-contiguous.
5. Contiguity repair: split each area into queen-contiguous components (MSOA BGC polygons); hand every
   fragment not containing the core to the adjacent area with the strongest flow link → 3 true islands remain.
### 2.4 Null model (Trap 2)
Keep the partition's size distribution (number of units per area) exactly; randomly permute unit→area
labels; recompute area-level SC; 60 runs; report mean **and sd** (v1 showed only means).
Repeat at LAD (district) level: 0.961 observed vs 0.798 random.
Excess = observed − random mean (+0.58 at MSOA).
### 2.5 TTWA validity rule (Trap 3)
Valid if workers ≥ 3,500 and two-sided SC ≥ threshold(size), threshold linear from 0.75 @ 3,500 to
0.667 @ 25,000, flat 0.667 above [DECIDE/verify the exact Coombes & Bond 2008 trade-off form].
"Naive merge": repeatedly take the least-valid area and merge it into the neighbour with the strongest
flow link until all valid → 67 areas, London = 6.1 M workers. Compare with 167 official 2011 TTWAs (E&W).
Add (review): run Istat `LabourMarketAreas` (R) on the same matrix; compare three maps
(own heuristic / open implementation / official) with ARI or V-measure against official TTWAs.
Report the parameter sensitivity: several parameter sets give ≈230 areas with different maps.

## 3. Serbia — distance bands (slides 9–10)
- Input: per municipality, daily migrants (work; education = pupils+students merged) by destination band.
  Daily migrant = person leaving their **settlement** (насеље) of residence daily.
- Self-containment (RBSC — [DECIDE name: residence-based self-containment]) = migrants to another
  settlement in the same municipality / all daily migrants. National: 50.3 %; median municipality 0.53.
- 8 single-settlement municipalities → SC ≡ 0 by definition → flag as artefact (hatch/outline), exclude from stats.
- Education vs work: median 0.65 vs 0.53; gap = SC_edu − SC_work, median per-municipality gap +0.08
  (state "median of per-municipality gaps" on slides — differs from difference of medians 0.12); r(SC_edu, SC_work) = 0.82.
- Urbanisation: GHS-SMOD class per 1 km cell × GHS-POP → **population-weighted** share in urban classes
  (DEGURBA logic) per municipality → r(gap, urbanisation) = +0.03. Area-share version gave r = −0.28 (spurious;
  half the municipalities have zero urban area) — keep as a documented negative control.
- Name matching: exact → pattern; log unmatched. Kosovo* not covered by the census → excluded with footnote.
  Regression test: no polygon > X km² receives another unit's values (the "587 km² polygon" bug).

## 4. Netherlands — pre-aggregated pairs (slide 11)
- 81252NED, Dec 2014, jobs by residence COROP × workplace COROP (40×40), 7.54 M jobs.
- Per-COROP two-sided SC: median 0.66; share passing 0.75 = 20 %; extremes Delfzijl 0.45, Zeeuwsch-Vlaanderen 0.88.
- Delimitation (§2.3) on top → 2 areas. Label as **artefact of the 40-region cage**, not a finding.
- Extend: 83628NED (2014–2020) and 85481NED (current) — same analysis, check region level.

## 5. Japan — MLIT people-flow (slides 12–14)
- Data: 1 km mesh (JIS X 0410), monthly, weekday/holiday × day/night, from_area bands
  (same municipality / same prefecture / same region / other). Provider Agoop (app-GPS panel expanded) — verify.
- Day/night map: weekday Oct 2019, ratio = day / night per mesh (log colour scale ×0.13…×7.9).
- Local share: for the central ward (中区 Naka-ku — verify), day presence from "same municipality" / all
  day presence = 27 %. Say "come from outside by day", not "commute".
- Caveats: annual totals identical within ±0.3 % (normalised) → compare composition only. Weekday local
  share 0.632 (2019) → 0.677 (2020) [DECIDE: which area].
- Signatures: 2019 monthly mean; cells ≥ 100 people; x = log2(weekday day / weekday night),
  y = log2(holiday day / weekday day); thresholds ±log2(1.5):
  office (x ≥ log2 1.5), residential (x ≤ −log2 1.5), leisure/retail (y ≥ log2 1.5), else mixed
  [DECIDE precedence]. Counts: mixed 155, residential 102, leisure 50, office 115 (= 422 cells).
- HDBSCAN on composition profiles: 100 % noise "at honest settings". Make it rigorous: sweep
  min_cluster_size × min_samples, report noise share; Hopkins statistic; k-means silhouette for contrast.
- Figure (review): add the continuum scatter with threshold lines and worded quadrants.

## 6. Spain — MITMA (new)
Madrid: hourly presence/OD (v2, 2022→) → day/night ratio comparable to Hiroshima; real intraday profiles
(the abstract's promise). Decide unit (districts) and period (e.g. weekday October 2023).

## 7. Promised but not yet built
- Urban Atlas polygons as common reference; DEGURBA classes per polygon.
- OSRM: travel time from each unit to its area core (plausibility of delimitation) or drop from README.
- QGIS: GeoPackage of all layers + `.qgz` with styles; PostGIS export via docker-compose.
