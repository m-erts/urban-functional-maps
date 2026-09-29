# Response to reviewers

Manuscript: *Open mobility data for functional-area maps: what each source leaves out, and how much of the result is scale, contiguity and algorithm.* Revised version.

Two reviews were received. They agree on five points, which we answer together; we then take up the points on which the reviews differ. Every number below is produced by the pipeline of the revised version and is the number printed in the revised text.

## Summary of changes

1. The standard Coombes-Bond algorithm is now run with the parameters of the official Travel to Work Areas, on England and Wales 2011 and on the two new countries. We use the R package LabourMarketAreas 3.4, the Istat implementation of the method recommended for European labour market areas. It is compared with the official map beside the two naive repairs, which stay in the paper labelled as such (Sections 3.6 and 4.3).
2. The contiguous null is now a recombination Markov chain on spanning trees [DeFord et al. 2021] that holds the size of every area within 5 % of the partition under test. Region growing, which both reviews criticised, is kept only for comparison in Appendix B (Sections 3.5 and 4.2).
3. Two countries with origin-destination pairs are added. For the Netherlands we use municipal pairs of December 2023 from table 85481NED. For Spain we use trips between 3,792 districts from operator data, with purpose and hour, October 2023. The decomposition of Section 4.2 and the comparison of constructions in Section 4.3 now cover three countries and 11 partitions.
4. The rank-correlation test on OpenStreetMap traces ($n$ = 11) is removed. The traces remain in the audit of sources as a statement about sample size (Appendix A).
5. The Japanese section is shortened to two paragraphs in Section 4.6, with the detail in Appendix C. It is now framed as a check on a practice that the literature follows.

## Points raised by both reviewers

### 1. The official areas were compared with a home-made heuristic, not with the official algorithm

We agree that the comparison needed the reference construction. LabourMarketAreas 3.4 [Ichim et al. 2023] implements the Coombes-Bond (2008) version of the TTWA algorithm as documented by Franconi et al. (2016). We run it with minimum size 3,500, minimum self-containment 0.667, target size 25,000 and target self-containment 0.75, which are the parameters of the official 2011 areas.

On the 2011 matrix of commuters in England and Wales it returns 59 areas; the official map has 173. Their adjusted Rand index with the official areas is 0.42 and their mean intersection over union 0.35. For the heuristic the two values are 0.54 and 0.58; for the greedy merge, 0.46 and 0.48. 95 % of its areas meet the validity rule as we read it (Eq. 6); the package applies its own validity function with the same four parameters.

Running the standard construction also exposed a difference in the input. The ONS methodology note on the 2011 areas (reproduced in Coombes and ONS 2015) says that people who work mainly at or from home, offshore or with no fixed workplace were counted as working at their residence. Our matrix leaves them out, for the reasons of Section 4.1. Coded as ONS coded them, the same algorithm with the same parameters returns 95 areas, with an adjusted Rand index of 0.49 with the official map. The paper now reports both codings (Sections 3.6 and 4.3). The rest of the distance to the official map has causes the open matrix cannot remove: LSOAs as units, other code, and the revision of the draft areas.

The comparison is now also made on the placement term of Eq. 5, which removes scale and contiguity. For England and Wales 2011 it is 0.153 for the standard construction on the matrix of commuters, 0.160 on the ONS coding, 0.186 for the heuristic and 0.215 for the official areas. In Spain the standard construction leads clearly (0.220 against 0.068), and in the Netherlands the two are level. We report this as found; no construction leads everywhere.

Two clarifications. First, the original text did not criticise the position of the official boundaries. It reported that the official areas have the larger placement term, that is, that the official construction places boundaries better than the heuristic. Reviewer 2 calls this finding trivial, since the heuristic is simple. We agree that the direction was expected. The contribution is that Eq. 5 turns the expectation into a measured quantity, and that the raw score hides most of the difference. Second, the package is not the production code. Eurostat (2020) reports that its outputs were "not wholly comparable" with the Newcastle Fortran code used for the official areas. The draft areas were also revised after consultation with their users and cleaned of non-contiguities [ONS 2016; Coombes and ONS 2015], and they were built from LSOAs. Section 3.6 now says so. Agreement with the official map is interpreted as the distance an open implementation of the published method gets on the open matrix.

The greedy merge and the dissolution stay, described as naive repairs. They show that the rule alone does not determine a map. With the standard construction in the comparison, the argument is measured rather than asserted. Rule plus naive repair gives 61 to 67 areas; rule plus the standard construction gives 59 or 95, depending on the coding.

### 2. The contiguous null did not hold the area sizes

We agree. Region growing produced 35.3 effective areas where the heuristic of 2021 has 24.5. The recombination chain holds each area's size within 5 % of the partition under test; for the same partition it returns 24.8 effective areas against 24.5. Each chain runs 200,000 steps. The first 100,000 are discarded, and one state is kept every 1,000 steps. We report four diagnostics, for every chain:

- the chains reach the range of the kept states within 3,000 steps;
- the lag-1 autocorrelation of the kept states is -0.17 to +0.43;
- the Geweke statistic stays below 1.7 in absolute value;
- the adjusted Rand index of the kept states with the start differs from that between kept states by at most 0.05.

The recombination chain does not sample uniformly either. It targets the spanning-tree distribution, which favours compact areas [DeFord et al. 2021; Cannon et al. 2026]. Uniform sampling over contiguous partitions of graphs of this size is out of reach [DeFord et al. 2021], and Cannon et al. (2026) propose the spanning-tree distribution as the canonical ensemble. Region growing, by contrast, has no known target distribution [Fifield et al. 2020]. Section 3.5 and Limitation 4 state this.

The numbers of the first version move little under the new null. For England and Wales 2021 the placement term of the heuristic moves from 0.131 (region growing) to 0.134 (recombination). For the official areas it moves from 0.186 to 0.196. All four British rows are in Appendix B.

### 3. The OpenStreetMap test had eleven cells

We agree and have removed it. OpenStreetMap traces remain one row of the source audit. The reviewers' own summary of the section is a finding about the source: in Hiroshima, 200,000 points hold 2,395 distinct minutes of recording. Appendix A gives the sample statistics and says why the correlation is not reported. The figure no longer shows it.

### 4. That functional classes are not natural clusters is trivial

We agree that classes of land use are normative, and the revised Section 4.6 says so first. We do not agree that the check is superfluous. Studies of mobile phone data report unsupervised clusters as land-use types, for example Soto and Frías-Martínez (2011) and Lenormand et al. (2015). The latter report that four groups consistently appear, although the method is unsupervised. The Japanese data give no groups at all: HDBSCAN labels every cell as noise at 9 of 12 settings. The share of the residual class moves from 17 % to 65 % with the threshold. The section is now two paragraphs, and the rest is in Appendix C.

### 5. Spain was not analysed; Serbia and the Netherlands add no insight

*Spain* is added: 11.31 million trips a day on weekdays, from home to work or study, between 3,792 districts, October 2023. It is the only source in the study with pairs, a purpose and the hour together (Figure 9). The heuristic returns 69 areas and leaves 751 zones, with 14 % of trips, unassigned. The standard construction returns 271 areas, and the two agree at an adjusted Rand index of 0.59. On this matrix the standard construction has a placement term of 0.220, against 0.068 for the heuristic.

*The Netherlands* now has a real delimitation. The successor table 85481NED publishes pairs between the 342 municipalities. The first version could only pose the question whether the COROP regions, designed in 1970 as nodal regions, still hold their commuters. Now it can be answered. Their median self-containment in 2023 is 0.66, and 45 % of them meet the TTWA validity rule. The standard construction on municipal pairs agrees with them at an adjusted Rand index of 0.50. Their placement term is 0.065, against 0.085 for the standard construction.

*Serbia* stays short. Its contribution is methodological rather than cartographic. The definition of a daily migrant makes 8 municipalities zero by construction. A weighting choice turns a null correlation ($r$ = -0.02 by population) into $r$ = -0.28 (by area). Reviewer 2 considered this useful, and we kept it at its present length.

## Points on which the reviews differ

**Scope of the conclusions about the official areas.** Reviewer 1 reads the paper as a critique of the official boundaries, and Reviewer 2 as a comparison of constructions. The revised text follows the second reading and says so in Section 1 and Section 5.

**The 2021 census.** Reviewer 1 attributes the jump from 0.093 to 0.506 to remote work during the pandemic. The mechanism is the coding. The same category of people existed in 2011 (4.9 million) and was coded outside the matrix. The pandemic made the category larger; the code list decides where it lands. Section 4.1 already made this distinction, and it now states it in one sentence.

## Smaller changes

- The Japanese provider, the Spanish licence and the Dutch table are described from their primary documents (Section 2).
- The bibliography gains 19 entries, each checked against Crossref, DataCite, the EU Publications Office or the publisher.
- The Dutch figures and the source table give CBS's own description of the COROP regions (nodal regions designed in 1970) instead of "commuter basins".
- In the Coombes-Bond step one per-row operation of the package is replaced by an equivalent vectorised one, for speed; the partitions are identical where both versions were run (Section 3.6).
- All tables, figures and numbers are regenerated from raw data, and the regression snapshot and the register of the conference numbers are updated.
