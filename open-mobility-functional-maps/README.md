# open-mobility-functional-maps

**Which open mobility dataset answers which question?** Reproducible pipeline and materials behind the
FOSS4G 2026 Hiroshima talk *"Eurostat vs OSM vs Census: Choosing Open Mobility Data for Urban Function Maps"*
(Marija Ercegovac, 3 Sep 2026).

> 🚧 Work in progress — the pipeline is being rebuilt into a fully reproducible form. Status per result:
> [`docs/04_RESULTS_REGISTER.md`](docs/04_RESULTS_REGISTER.md).

## The argument in one table
Every open source silently sacrifices one of three dimensions.

| source | origin→destination pairs | trip purpose | time of day / week |
|---|---|---|---|
| UK census 2011/2021 (WU01EW / ODWP01EW) | full MSOA matrix | work only | none |
| Serbia census 2022 (daily migrants) | nested administrative rings | work + education (merged) | none |
| Netherlands CBS register OD | pairs — but only 40 pre-drawn COROP regions | work only | none |
| Japan MLIT people-flow (Agoop app-GPS panel)¹ | nested rings (From-To ≠ OD) | none — presence | month × day/night × weekday/holiday |
| Spain MITMA big-data mobility (MNO)² | pairs (districts) | limited activity types | hourly |
| OSM public GPS traces | fine-grained, but contributor sample | none | timestamps, sparse |

¹ provider to be verified against the MLIT データ定義書. ² being added.

## Three checks that cost an afternoon
1. **Shuffle** — rebuild your areas with random same-size assignment; if random scores 80 % of your result, your result is the aggregation.
2. **Read the code list** — special place-of-work categories (home, no fixed place, offshore) land on the diagonal: 12.6 M people flipped a national trend in Census 2021.
3. **Draw it** — join the geometry and look.

## Decision matrix (corrected after review)
| you need | reach for | before trusting, check |
|---|---|---|
| commuting structure, delimitation | census/register OD pairs (UK, FR MOBPRO, DE BA, JP census; Eurostat Census Hub only at NUTS-2 — too coarse) | special place-of-work codes; null model; contiguity; census date (2021 = lockdown in E&W) |
| intraday presence, day/night | MNO/app-derived products (ES MITMA hourly; JP MLIT 2019–21; Eurostat Multi-MNO next) | who is in the panel; volume normalisation; suppression; band definitions |
| self-containment without a matrix | census bands (RS) | the migrant definition — settlement vs municipality |
| fine-grain routes / activity traces | OSM GPS traces | contributor bias: density follows mappers, not people |

## Reproduce
```bash
make env && conda activate omfm
make fetch interim analysis figures test     # or: docker compose up --build
```
Parameters: `config/params.yaml` · Methods: `docs/03_METHODOLOGY.md` · Data & licences: `docs/02_DATA_SOURCES.md`
· Literature: `docs/07_LITERATURE.md` · Roadmap: `docs/06_BACKLOG.md` · Talk: `talk/`.

## Licences
Code: MIT. Slides, figures, docs: CC BY 4.0. Data: original licences — © OpenStreetMap contributors (ODbL);
Overture Maps Foundation; ONS (OGL v3); SORS; CBS (CC BY 4.0); MLIT (政府標準利用規約); JRC GHSL (CC BY 4.0).
Kosovo*: not covered by the Serbian census 2022 (UNSCR 1244).

## Cite
See `CITATION.cff`.
