# Data sources

Addresses, sizes and checksums of the exact files: [`data/manifest.yaml`](../data/manifest.yaml).
`python scripts/fetch_data.py` downloads what has a public address and verifies the rest.

## Used

| Source | Publisher | What is read | Licence | Attribution line |
|---|---|---|---|---|
| ODWP01EW, Census 2021 origin-destination, MSOA and LTLA | Office for National Statistics, through Nomis | residence, workplace, place-of-work indicator, count | Open Government Licence v3.0 | Source: Office for National Statistics licensed under the Open Government Licence v3.0 |
| WU01EW, Census 2011 origin-destination, MSOA | Office for National Statistics, through Nomis | residence, workplace, count | OGL v3.0 | same |
| MSOA boundaries 2011 and 2021 (BGC), TTWA 2011 boundaries, look-ups OA/LSOA to MSOA and to TTWA | ONS Open Geography Portal | polygons, codes | OGL v3.0 | Contains OS data © Crown copyright and database right |
| Daily migrations, Census 2022, two workbooks | Statistical Office of the Republic of Serbia | migrants by destination band, by municipality | terms of use of SORS; source must be cited | Source: Statistical Office of the Republic of Serbia |
| Municipal boundaries `Op_tina.shp` | Republic Geodetic Authority, GeoSrbija | polygons, register codes | terms of use of GeoSrbija; registration needed | GeoSrbija, Republic Geodetic Authority |
| 81252NED, jobs of employees by region of residence and of work | Statistics Netherlands (CBS) | 40 x 40 COROP matrix, December 2014 | CC BY 4.0 | Source: CBS |
| 85481NED, jobs of employees and commuting distance by region of residence and of work | Statistics Netherlands (CBS) | municipality x municipality, December 2023 | CC BY 4.0 | Source: CBS |
| Municipal and COROP boundaries 2023 (gebiedsindelingen, generalised) | CBS, through PDOK | polygons | CC BY 4.0 | Source: CBS, PDOK |
| Open mobility study, trips between districts, 17 to 19 and 24 to 25 October 2023; district zoning | Ministry of Transport and Sustainable Mobility of Spain (MITMS); mobile network data of Orange España, processed by Nommon | trips by origin, destination, hour, activity at both ends | Licencia de datos abiertos del Ministerio (reuse, also commercial, with attribution) | Basado en datos abiertos Ministerio de Transportes y Movilidad Sostenible (transportes.gob.es) |
| Nationwide people-flow open data, prefecture 34 | Ministry of Land, Infrastructure, Transport and Tourism of Japan; provider Agoop Corp. | presence per 1 km mesh and per municipality | Government of Japan Standard Terms of Use 2.0 | Source: MLIT people-flow open data |
| GHS-POP R2023A (100 m) and GHS-SMOD R2023A (1 km), epoch 2030 | European Commission, Joint Research Centre | population, settlement class | CC BY 4.0 | GHSL, European Commission JRC |
| Public GPS traces, API v0.6 `trackpoints` | OpenStreetMap | position, time | ODbL 1.0 | © OpenStreetMap contributors |
| Places, release 2026-07-22.0 | Overture Maps Foundation | counts per H3 cell (archived aggregate) | CDLA-Permissive-2.0 and source licences | Overture Maps Foundation |

## What the files do not announce

| Source | Property | Where it is documented |
|---|---|---|
| ODWP01EW | Indicator 1 (mainly at or from home, no fixed place) is coded with workplace = residence | ONS user guide to Census 2021 origin-destination data |
| ODWP01EW | Census day 21 March 2021, in a lockdown | ONS travel to work quality information |
| WU01EW | The same people carry pseudo-codes OD0000001 and OD0000003; offshore and abroad are OD0000002 and OD0000004 | Nomis table description |
| SORS | A daily migrant leaves the settlement of residence, not the municipality. Rows "Град X" inside an area are sums over city municipalities | methodological notes of the census |
| GeoSrbija | The attribute table has lost its encoding: every non-ASCII letter is "?" | the file |
| CBS OData | `$skip` is ignored; values are thousands of jobs; region codes are padded with spaces | the service |
| MLIT | `from_area` is four nested rings, not an origin. Volumes are normalised. Cells under 10 people are not published | data definition document, p. 6 |
| OSM API | 5,000 points per page; the archive changes daily | API documentation |
| CBS 85481NED | Values in thousands with one decimal: a pair is known to the nearest 100 jobs, pairs under 50 appear as 0. The place of work is modelled. All figures are provisional. Code GM0000 is "municipality unknown" | table description; DataProperties |
| MITMS trips | `trabajo_estudio` is work and study together; `estudio_destino_posible = si` flags a possible place of study. Trips are expanded to the resident population. 26 and 27 October 2023 are missing (incident at the operator). A method change on 1 July 2025 breaks the series | methodology report v8; data dictionary; note on the method change |
| Overture | A release stays on the public bucket for about two months | release notes |

## Named and not processed

| Source | Why it matters | Address |
|---|---|---|
| Multi-MNO reference pipeline of Eurostat | method and code, no data | https://github.com/eurostat/multimno |
| Japanese census commuting pairs | pairs for the country that has the clock | https://www.e-stat.go.jp |

The 2022 census of Serbia does not cover Kosovo\*. \* This designation is without prejudice to positions on status, and is in line with UNSCR 1244/1999 and the ICJ Opinion on the Kosovo declaration of independence.
