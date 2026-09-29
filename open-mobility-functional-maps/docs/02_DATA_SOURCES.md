# Data sources

Raw data is never committed. Each source has a fetch script and an entry in `data/manifest.yaml`
(URL, release/version, access date, licence, sha256). Verify every "verify" item at fetch time.

## Used in the v1 talk

| id | Dataset | Publisher | Access | Licence | Notes |
|---|---|---|---|---|---|
| `osm_traces` | OSM public GPS trackpoints | OpenStreetMap | `GET https://api.openstreetmap.org/api/0.6/trackpoints?bbox=l,b,r,t&page=N` (5,000 pts/page) | ODbL — "© OpenStreetMap contributors" | Respect API usage policy https://operations.osmfoundation.org/policies/api/. Private traces come back anonymised without timestamps → "unique minutes" counts only timestamped (trackable/identifiable) points — verify & state. |
| `overture_places` | Overture Maps Places, release 2026-07 | Overture Maps Foundation | GeoParquet on S3/Azure, query with DuckDB (`s3://overturemaps-us-west-2/release/<tag>/theme=places/type=place/`) | CDLA-Permissive-2.0 (+ source attributions) — https://docs.overturemaps.org/attribution/ | |
| `uk_od_2021` | ODWP01EW — location of usual residence and place of work, MSOA | ONS / Nomis | https://www.nomisweb.co.uk/sources/census_2021_od | OGL v3 | People working at/from home or with no fixed place are "counted at their usual residence as place of work" (ONS user guide). Census day 21 Mar 2021 (lockdown). |
| `uk_od_2011` | WU01EW — location of usual residence and place of work, MSOA | ONS / Nomis | https://www.nomisweb.co.uk/census/2011/wu01ew | OGL v3 | Special codes OD0000001 (home), OD0000002 (offshore), OD0000003 (no fixed place), OD0000004 (outside UK) |
| `uk_msoa_2021` | MSOA Dec 2021 Boundaries EW BGC | ONS Open Geography Portal | https://geoportal.statistics.gov.uk | OGL v3 | EPSG:27700 |
| `uk_msoa_2011` + lookup | MSOA 2011 BGC; MSOA11→MSOA21 lookup | ONS OGP | same | OGL v3 | needed for 2011 vs 2021 comparison |
| `uk_lad` | Local authority districts (for the "district level 0.961/0.798" result) | ONS OGP | same | OGL v3 | TODO: which LAD vintage |
| `uk_ttwa_2011` | Travel to Work Areas (Dec 2011) boundaries | ONS OGP | same | OGL v3 | 167 in England & Wales (verify count incl. cross-border) |
| `rs_daily_migrations` | Popis 2022 — дневни мигранти по општинама (work, education) | SORS (РЗС) | https://popis2022.stat.gov.rs/sr-cyrl/5-vestisaopstenja/news-events/20240719-dnevne-migracije/ ; https://data.stat.gov.rs | SORS terms (verify; attribution) | 168 municipalities, 795,779 daily migrant workers |
| `rs_boundaries` | Municipal boundaries | GeoSrbija / RGZ | https://geosrbija.rs ; https://data.gov.rs | verify | shapefile encoding breaks Cyrillic → use UTF-8 source / .cpg |
| `ghsl` | GHS-SMOD R2023A, GHS-POP R2023A (1 km, Mollweide) | EC JRC | https://ghsl.jrc.ec.europa.eu/download.php | CC BY 4.0 | epoch TODO |
| `nl_od_2014` | 81252NED Banen van werknemers; woon- en werkregio (2006–2014) | CBS | https://opendata.cbs.nl/#/CBS/nl/dataset/81252NED ; OData `https://opendata.cbs.nl/ODataApi/odata/81252NED` | CC BY 4.0 | 40 COROP; 7.54 M jobs Dec 2014 |
| `nl_od_successors` | 83628NED (2014–2020); 85481NED (current) | CBS | https://www.cbs.nl/nl-nl/cijfers/detail/83628NED ; https://opendata.cbs.nl/#/CBS/nl/dataset/85481NED | CC BY 4.0 | check finest region level |
| `nl_corop` | COROP boundaries | CBS/PDOK gebiedsindelingen | https://www.pdok.nl (CBS gebiedsindelingen) | CC BY 4.0 | |
| `nl_odin` | ODiN travel survey | CBS / DANS | https://www.cbs.nl (ODiN) ; microdata via DANS | registration | only used conceptually in the sacrifice matrix |
| `jp_mlit_flow` | 全国の人流オープンデータ（1kmメッシュ、市区町村単位発地別）2019–2021 | MLIT 政策統括官; provider **Agoop** | https://www.geospatial.jp/ckan/dataset/mlit-1km-fromto ; https://www.mlit.go.jp/tochi_fudousan_kensetsugyo/tochi_fudousan_kensetsugyo_fr17_000001_00006.html | 政府標準利用規約 (CC BY 4.0-compatible) | monthly × day/night × weekday/holiday; from_area = 4 nested bands; <10 suppressed; normalised volumes; データ定義書 p.6 |
| `jp_boundaries` | 行政区域 N03 | 国土数値情報 | https://nlftp.mlit.go.jp/ksj/ | 国土数値情報利用約款 | for ward names (e.g. 中区) |

## To add (from the review)

| id | Dataset | Access | Why |
|---|---|---|---|
| `es_mitma` | Spain MITMA "Estudio de movilidad con Big Data" v1 (2020-02-14…2021-05-09), v2 (2022-01-01→, hourly OD, districts/municipalities/GAU) | https://www.transportes.gob.es/ministerio/proyectos-singulares/estudios-de-movilidad-con-big-data ; R: https://ropenspain.github.io/spanishoddata/ | the real open MNO product in Europe; intraday profiles promised in abstract |
| `es_ine_em` | INE experimental mobility studies EM-1…EM-4 | https://www.ine.es/en/experimental/movilidad/experimental_em4_en.htm | NSO counterpart |
| `eu_multimno` | Eurostat Multi-MNO reference pipeline (code, no data) | https://github.com/eurostat/multimno ; https://cros.ec.europa.eu/landing-page/multi-mno-project | project ended 06/2025; successor MNO-MINDS https://cros.ec.europa.eu/mno-minds |
| `jp_census_od` | 国勢調査 従業・通学市区町村 OD (常住地×従業地) | https://www.e-stat.go.jp (table 6-1, statdisp_id=0003454527) | Japan census DOES have pairs |
| `fr_mobpro` | INSEE MOBPRO commune→commune 2022 | https://www.insee.fr/fr/statistiques/8589904 | EU example of full municipal pairs |
| `de_ba_pendler` | BA Pendlerstatistik / Pendleratlas | https://statistik.arbeitsagentur.de/DE/Navigation/Statistiken/Interaktive-Statistiken/Pendleratlas/Pendleratlas-Nav.html | EU example of pairs |
| `eu_census_hub` | Eurostat Census Hub (commuting at NUTS-2) | https://ec.europa.eu/CensusHub2 | abstract said "census flows from Eurostat" |
| `urban_atlas` | Copernicus Urban Atlas | https://land.copernicus.eu/en/products/urban-atlas (policy: https://land.copernicus.eu/en/data-policy) | promised common spatial reference |
| `degurba` | DEGURBA methodology | https://ec.europa.eu/eurostat/web/degree-of-urbanisation/methodology | |
| `osrm` | OSRM backend + OSM extracts (Geofabrik) | https://github.com/Project-OSRM/osrm-backend | promised in abstract |
| `lma_r` | Istat LabourMarketAreas (R) | https://cran.r-project.org/package=LabourMarketAreas ; https://www.istat.it/en/archive/182743 | open implementation of EU-TTWA / Coombes-type algorithm for Trap 3 |

## Reference documents
- ONS travel-to-work quality info, Census 2021: https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/methodologies/traveltoworkqualityinformationforcensus2021
- ONS user guide to Census 2021 OD data: https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/methodologies/userguidetocensus2021origindestinationdataenglandandwales
- TTWA 2011 report (Coombes & Bond / Newcastle CURDS): https://www.ncl.ac.uk/mediav8/centre-for-urban-and-regional-development-studies/files/travel-to-work-great-britain.pdf
- Eurostat/ESS MNO position paper KS-FT-23-001: https://ec.europa.eu/eurostat/documents/7870049/17468840/KS-FT-23-001-EN-N.pdf
- e-Stat big data portal: モバイル空間統計 (docomo) https://www.e-stat.go.jp/bigdataportal/dataintro/130 vs Agoop ポイント型流動人口 https://www.e-stat.go.jp/bigdataportal/dataintro/126
- Urban Data Challenge page (提供元：国土交通省、株式会社Agoop): https://urbandata-challenge.jp/idc/data-zenkokujinryuopendata
