# Response to reviewers

Manuscript: *Open mobility data for functional-area maps: what each source leaves out, and how much of the result is scale, contiguity and algorithm.* Revised version.

Two reviews were received. They agree on five points, which we answer together; we then take up the points on which the reviews differ. Every number below is produced by the pipeline of the revised version and is the number printed in the revised text.

## Summary of changes

1. The standard Coombes-Bond algorithm is now run with the parameters of the official Travel to Work Areas, on England and Wales 2011 and on the two new countries. We use the R package LabourMarketAreas 3.4, the Istat implementation of the method recommended for European labour market areas. It is compared with the official map beside the two naive repairs, which stay in the paper labelled as such (Sections 3.6 and 4.3).
2. The contiguous null is now a recombination Markov chain on spanning trees [DeFord et al. 2021] that holds the size of every area within {{dec_recom_tolerance*100:.0f}} % of the partition under test. Region growing, which both reviews criticised, is kept only for comparison in Appendix B (Sections 3.5 and 4.2).
3. Two countries with origin-destination pairs are added. For the Netherlands we use municipal pairs of December 2023 from table 85481NED. For Spain we use trips between {{es_zones_spain:,}} districts from operator data, with purpose and hour, October 2023. The decomposition of Section 4.2 and the comparison of constructions in Section 4.3 now cover three countries and {{dec_partitions}} partitions.
4. The rank-correlation test on OpenStreetMap traces ($n$ = {{osm_hij_three_way_n}}) is removed. The traces remain in the audit of sources as a statement about sample size (Appendix A).
5. The Japanese section is shortened to two paragraphs in Section 4.6, with the detail in Appendix C. It is now framed as a check on a practice that the literature follows.

## Points raised by both reviewers

### 1. The official areas were compared with a home-made heuristic, not with the official algorithm

We agree that the comparison needed the reference construction. LabourMarketAreas 3.4 [Ichim et al. 2023] implements the Coombes-Bond (2008) version of the TTWA algorithm as documented by Franconi et al. (2016). We run it with minimum size 3,500, minimum self-containment 0.667, target size 25,000 and target self-containment 0.75, which are the parameters of the official 2011 areas.

On the 2011 matrix of commuters in England and Wales it returns {{uk_lma_areas_2011}} areas; the official map has {{uk_ttwa_official_touching_ew_2011}}. Their adjusted Rand index with the official areas is {{uk_ari_lma_2011:.2f}} and their mean intersection over union {{uk_iou_lma_2011:.2f}}. For the heuristic the two values are {{uk_ari_contiguous_2011:.2f}} and {{uk_iou_contiguous_2011:.2f}}; for the greedy merge, {{uk_ari_ttwa_greedy_2011:.2f}} and {{uk_iou_ttwa_greedy_2011:.2f}}. {{uk_lma_valid_share_2011*100:.0f}} % of its areas meet the validity rule as we read it (Eq. 6); the package applies its own validity function with the same four parameters.

Running the standard construction also exposed a difference in the input. The ONS methodology note on the 2011 areas (reproduced in Coombes and ONS 2015) says that people who work mainly at or from home, offshore or with no fixed workplace were counted as working at their residence. Our matrix leaves them out, for the reasons of Section 4.1. Coded as ONS coded them, the same algorithm with the same parameters returns {{uk_lma_ons_areas_2011}} areas, with an adjusted Rand index of {{uk_ari_lma_ons_2011:.2f}} with the official map. The paper now reports both codings (Sections 3.6 and 4.3). The rest of the distance to the official map has causes the open matrix cannot remove: LSOAs as units, other code, and the revision of the draft areas.

The comparison is now also made on the placement term of Eq. 5, which removes scale and contiguity. For England and Wales 2011 it is {{dec_uk_2011_lma_from_placement:.3f}} for the standard construction on the matrix of commuters, {{dec_uk_2011_lma_ons_from_placement:.3f}} on the ONS coding, {{dec_uk_2011_own_from_placement:.3f}} for the heuristic and {{dec_uk_2011_official_from_placement:.3f}} for the official areas. In Spain the standard construction leads clearly ({{dec_es_2023_lma_from_placement:.3f}} against {{dec_es_2023_own_from_placement:.3f}}), and in the Netherlands the two are level. We report this as found; no construction leads everywhere.

Two clarifications. First, the original text did not criticise the position of the official boundaries. It reported that the official areas have the larger placement term, that is, that the official construction places boundaries better than the heuristic. Reviewer 2 calls this finding trivial, since the heuristic is simple. We agree that the direction was expected. The contribution is that Eq. 5 turns the expectation into a measured quantity, and that the raw score hides most of the difference. Second, the package is not the production code. Eurostat (2020) reports that its outputs were "not wholly comparable" with the Newcastle Fortran code used for the official areas. The draft areas were also revised after consultation with their users and cleaned of non-contiguities [ONS 2016; Coombes and ONS 2015], and they were built from LSOAs. Section 3.6 now says so. Agreement with the official map is interpreted as the distance an open implementation of the published method gets on the open matrix.

The greedy merge and the dissolution stay, described as naive repairs. They show that the rule alone does not determine a map. With the standard construction in the comparison, the argument is measured rather than asserted. Rule plus naive repair gives {{uk_ttwa_dissolution_2011}} to {{uk_ttwa_greedy_2011}} areas; rule plus the standard construction gives {{uk_lma_areas_2011}} or {{uk_lma_ons_areas_2011}}, depending on the coding.

### 2. The contiguous null did not hold the area sizes

We agree. Region growing produced {{uk_own_contiguous_null_effective_areas_2021:.1f}} effective areas where the heuristic of 2021 has {{uk_own_effective_areas_2021:.1f}}. The recombination chain holds each area's size within {{dec_recom_tolerance*100:.0f}} % of the partition under test; for the same partition it returns {{dec_uk_2021_own_effective_areas_null:.1f}} effective areas against {{dec_uk_2021_own_effective_areas:.1f}}. Each chain runs {{dec_recom_steps:,}} steps. The first {{dec_recom_burn_in:,}} are discarded, and one state is kept every {{dec_recom_every:,}} steps. We report four diagnostics, for every chain:

- the chains reach the range of the kept states within {{dec_steps_to_range_max:,}} steps;
- the lag-1 autocorrelation of the kept states is {{dec_lag1_min:+.2f}} to {{dec_lag1_max:+.2f}};
- the Geweke statistic stays below {{dec_geweke_abs_max:.1f}} in absolute value;
- the adjusted Rand index of the kept states with the start differs from that between kept states by at most {{dec_ari_gap_max:.2f}}.

The recombination chain does not sample uniformly either. It targets the spanning-tree distribution, which favours compact areas [DeFord et al. 2021; Cannon et al. 2026]. Uniform sampling over contiguous partitions of graphs of this size is out of reach [DeFord et al. 2021], and Cannon et al. (2026) propose the spanning-tree distribution as the canonical ensemble. Region growing, by contrast, has no known target distribution [Fifield et al. 2020]. Section 3.5 and Limitation 4 state this.

The numbers of the first version move little under the new null. For England and Wales 2021 the placement term of the heuristic moves from {{uk_own_from_placement_2021:.3f}} (region growing) to {{dec_uk_2021_own_from_placement:.3f}} (recombination). For the official areas it moves from {{uk_official_from_placement_2021:.3f}} to {{dec_uk_2021_official_from_placement:.3f}}. All four British rows are in Appendix B.

### 3. The OpenStreetMap test had eleven cells

We agree and have removed it. OpenStreetMap traces remain one row of the source audit. The reviewers' own summary of the section is a finding about the source: in Hiroshima, 200,000 points hold {{osm_hij_unique_min:,}} distinct minutes of recording. Appendix A gives the sample statistics and says why the correlation is not reported. The figure no longer shows it.

### 4. That functional classes are not natural clusters is trivial

We agree that classes of land use are normative, and the revised Section 4.6 says so first. We do not agree that the check is superfluous. Studies of mobile phone data report unsupervised clusters as land-use types, for example Soto and Frías-Martínez (2011) and Lenormand et al. (2015). The latter report that four groups consistently appear, although the method is unsupervised. The Japanese data give no groups at all: HDBSCAN labels every cell as noise at {{jp_hdbscan_comp_all_noise_settings}} of {{jp_hdbscan_settings}} settings. The share of the residual class moves from {{jp_sig_mixed_share_min*100:.0f}} % to {{jp_sig_mixed_share_max*100:.0f}} % with the threshold. The section is now two paragraphs, and the rest is in Appendix C.

### 5. Spain was not analysed; Serbia and the Netherlands add no insight

*Spain* is added: {{es_trips_home_work/1e6:.2f}} million trips a day on weekdays, from home to work or study, between {{es_zones_spain:,}} districts, October 2023. It is the only source in the study with pairs, a purpose and the hour together (Figure 9). The heuristic returns {{es_own_areas}} areas and leaves {{es_own_unassigned:,}} zones, with {{es_own_unassigned_share*100:.0f}} % of trips, unassigned. The standard construction returns {{es_lma_areas}} areas, and the two agree at an adjusted Rand index of {{es_ari_own_lma:.2f}}. On this matrix the standard construction has a placement term of {{dec_es_2023_lma_from_placement:.3f}}, against {{dec_es_2023_own_from_placement:.3f}} for the heuristic.

*The Netherlands* now has a real delimitation. The successor table 85481NED publishes pairs between the {{nl23_units}} municipalities. The first version could only pose the question whether the COROP regions, designed in 1970 as nodal regions, still hold their commuters. Now it can be answered. Their median self-containment in 2023 is {{nl23_corop_sc_median:.2f}}, and {{nl23_corop_valid_share*100:.0f}} % of them meet the TTWA validity rule. The standard construction on municipal pairs agrees with them at an adjusted Rand index of {{nl23_ari_lma_corop:.2f}}. Their placement term is {{dec_nl_2023_corop_from_placement:.3f}}, against {{dec_nl_2023_lma_from_placement:.3f}} for the standard construction.

*Serbia* stays short. Its contribution is methodological rather than cartographic. The definition of a daily migrant makes {{rs_single_settlement}} municipalities zero by construction. A weighting choice turns a null correlation ($r$ = {{rs_r_sc_urb_pop:+.2f}} by population) into $r$ = {{rs_r_sc_urb_area:+.2f}} (by area). Reviewer 2 considered this useful, and we kept it at its present length.

## Points on which the reviews differ

**Scope of the conclusions about the official areas.** Reviewer 1 reads the paper as a critique of the official boundaries, and Reviewer 2 as a comparison of constructions. The revised text follows the second reading and says so in Section 1 and Section 5.

**The 2021 census.** Reviewer 1 attributes the jump from {{uk_diag_2021_clean:.3f}} to {{uk_diag_2021_naive:.3f}} to remote work during the pandemic. The mechanism is the coding. The same category of people existed in 2011 ({{uk_home_2011/1e6:.1f}} million) and was coded outside the matrix. The pandemic made the category larger; the code list decides where it lands. Section 4.1 already made this distinction, and it now states it in one sentence.

## Smaller changes

- The Japanese provider, the Spanish licence and the Dutch table are described from their primary documents (Section 2).
- The bibliography gains 19 entries, each checked against Crossref, DataCite, the EU Publications Office or the publisher.
- The Dutch figures and the source table give CBS's own description of the COROP regions (nodal regions designed in 1970) instead of "commuter basins".
- In the Coombes-Bond step one per-row operation of the package is replaced by an equivalent vectorised one, for speed; the partitions are identical where both versions were run (Section 3.6).
- All tables, figures and numbers are regenerated from raw data, and the regression snapshot and the register of the conference numbers are updated.
