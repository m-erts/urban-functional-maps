# Corrections to deck v1

Deck v1 is the version prepared for the talk of 3 September 2026 (text in `talk/deck_v1_text.md`).
The slides in `docs/slides/` are version 2. This file lists what changed and why.
Numbers are compared one by one in [RESULTS.md](RESULTS.md).

## Statements of fact

| Slide of v1 | Deck v1 | Corrected | Source |
|---|---|---|---|
| 2, 4, 12, 15 | The Japanese people-flow data are aggregated operator data of NTT docomo | The provider is Agoop Corp.: a panel of smartphone applications with GPS, expanded to population. It is not operator data | data definition document of the dataset; dataset page of the Geospatial Information Center |
| 2, 4 | Only Japan publishes time of day; the operator-based statistics of Europe are "a standard without data" | Spain publishes hourly origin-destination matrices from operator data. No cross-country European dataset exists | Kotov et al. 2026, doi:10.1177/23998083251415040 |
| 2, 15 | Japan publishes distance bands only | True for the people-flow product. The Japanese census publishes commuting pairs between municipalities | e-Stat |
| 11 | The Dutch table was discontinued after 2014 | Table 81252NED ends in 2014. Successor tables exist; the current one publishes pairs of municipalities | CBS StatLine |
| 6 | No mention of the census date | Census day was 21 March 2021, in a national lockdown | ONS, travel to work quality information for Census 2021 |
| 8 | "The algorithm is the moat" | The construction is described in published reports and an open European implementation exists. What is not published is code that reproduces the official map | ONS 2016; R package LabourMarketAreas |
| 9, 16 | "Kosovo excluded", "a Kosovo polygon wearing Belgrade data" | The 2022 census does not cover Kosovo\*. A polygon outside the census territory was matched by pattern to a Belgrade municipality | see footnote |

## Numbers

| Slide of v1 | Deck v1 | Corrected | Cause |
|---|---|---|---|
| 7 | District level: 0.961 observed, 0.798 random; "80 % of the result was arithmetic" | 0.947 and 0.657; 69 % | The stage values come from the 2021 matrix before people coded at their residence were removed |
| 8 | "235 areas ... 67 after enforcing the rule" | 235 is the 2021 matrix. 67 comes from the 197 areas of the 2011 matrix. The 2021 matrix gives 66 | Two census years in one sentence |
| 10 | r = −0.28 between the education-work difference and the area share of urban classes | −0.28 is the correlation of work self-containment with the area share. For the difference the value is +0.17. Rank correlations are near zero for both weightings | Wrong quantity |
| 10 | r = 0.82 between work and education self-containment | 0.80 on 160 municipalities (Spearman 0.81); 0.85 if the eight structural zeros are kept | No variant gives 0.82 |
| 11 | Most open region Delfzijl 0.45; most closed Zeeuwsch-Vlaanderen 0.88 | Zaanstreek 0.45; Zuid-Limburg 0.88. Delfzijl en omgeving is 0.54, Zeeuwsch-Vlaanderen 0.85 | Wrong names |
| 11 | Median 0.66; 20 % pass the 75 % test | These are supply-side values. Under the two-sided test of the official areas: 0.656 and 17.5 % | Side not stated |
| 13 | HDBSCAN returns 100 % noise | At 9 of 12 settings on the four-slot composition. On the two log-ratio axes never | Condition left out |
| 13 | 155, 102, 50, 115 cells "of Hiroshima city with 100 or more people" | The counts are reproduced for the map window (not the city limits), for cells whose four slot means sum to 100 or more, with the order of rules office, leisure, residential | Definitions were not on the slide |
| 12 | Day/night ratio from x0.13 to x7.9 | These are the ends of the colour scale, clipped at the 97th percentile. The data run from x0.07 to x23.9 | Clipping not stated |
| 3 | Belgrade: Spearman +0.67; Hiroshima: 51 % in one cell, +0.80 | +0.72; 50 %, +0.79 | The table of places was regenerated after the slide was made |
| 14 | Yearly totals agree within ±0.3 % | Within 0.11 % | The slide gave an upper bound |

\* This designation is without prejudice to positions on status, and is in line with UNSCR 1244/1999 and the ICJ Opinion on the Kosovo declaration of independence.
