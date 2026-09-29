# Results register

Generated from `tests/golden_values.yaml` (source of truth). Regenerate with `python scripts/render_results_register.py`.

| id | slide | value | tol | producing function | note | status |
|---|---|---|---|---|---|---|
| `osm_bgd_points` | 3 | 200000 | 0 | sources.osm_traces.fetch_window | API cap 40×5000 | unverified |
| `osm_bgd_unique_min` | 3 | 5695 | 50 | analysis.osm.unique_minutes |  | unverified |
| `osm_bgd_median_year` | 3 | 2014 | 0 | analysis.osm.median_year |  | unverified |
| `osm_bgd_top_cell` | 3 | 0.35 | 0.01 | analysis.osm.top_cell_share |  | unverified |
| `osm_bgd_spearman` | 3 | 0.67 | 0.02 | analysis.osm.spearman_vs_places |  | unverified |
| `osm_hij_unique_min` | 3 | 2395 | 50 | analysis.osm.unique_minutes |  | unverified |
| `osm_hij_top_cell` | 3 | 0.51 | 0.01 | analysis.osm.top_cell_share |  | unverified |
| `osm_hij_spearman` | 3 | 0.8 | 0.02 | analysis.osm.spearman_vs_places |  | unverified |
| `uk_msoa_n` | 5 | 7264 | 0 | sources.uk_census.load_msoa |  | unverified |
| `uk_fixed_2021` | 5 | 15.1e6 | 0.05e6 | sources.uk_census.clean_od |  | unverified |
| `uk_fixed_2011` | 6 | 21.6e6 | 0.05e6 | sources.uk_census.clean_od |  | unverified |
| `uk_home_2021` | 6 | 12.6e6 | 0.05e6 |  | 45 % of workers | unverified |
| `uk_home_2011` | 6 | 4.9e6 | 0.05e6 |  | 19 % of workers | unverified |
| `uk_diag_2011` | 6 | 0.103 | 0.002 | analysis.selfcontainment.unit_diagonal_share |  | unverified |
| `uk_diag_2021_naive` | 6 | 0.506 | 0.002 |  |  | unverified |
| `uk_diag_2021_clean` | 6 | 0.093 | 0.002 |  |  | unverified |
| `uk_areas_flows_only` | 5 | 235 | 0 | analysis.delimitation.delimit |  | unverified |
| `uk_areas_noncontig` | 5 | 26 | 0 |  |  | unverified |
| `uk_islands_after_fix` | 5 | 3 | 0 | analysis.delimitation.repair_contiguity |  | unverified |
| `uk_sc_2011_areas` | 7 | 0.74 | 0.005 | analysis.selfcontainment.partition_sc |  | unverified |
| `uk_sc_2011_random` | 7 | 0.157 | 0.005 | analysis.nullmodel.shuffle_sc |  | unverified |
| `uk_sc_2021_areas` | 7 | 0.695 | 0.005 |  |  | unverified |
| `uk_sc_2021_random` | 7 | 0.13 | 0.005 |  |  | unverified |
| `uk_excess_msoa` | 7 | 0.58 | 0.01 |  | ≈0.740−0.157 (2011); state year | unverified |
| `uk_district_observed` | 7 | 0.961 | 0.005 |  |  | unverified |
| `uk_district_random` | 7 | 0.798 | 0.005 |  |  | unverified |
| `uk_ttwa_official` | 8 | 167 | 0 |  | 2011 TTWAs in E&W — verify | unverified |
| `uk_ttwa_naive_merge` | 8 | 67 | 0 | analysis.ttwa.enforce_rule_naive |  | unverified |
| `uk_london_workers` | 8 | 6.1e6 | 0.1e6 |  |  | unverified |
| `rs_municipalities` | 9 | 168 | 0 |  |  | unverified |
| `rs_workers` | 9 | 795779 | 0 |  |  | unverified |
| `rs_sc_national` | 10 | 0.503 | 0.001 |  |  | unverified |
| `rs_sc_median_work` | 10 | 0.53 | 0.005 |  |  | unverified |
| `rs_sc_median_edu` | 10 | 0.65 | 0.005 |  |  | unverified |
| `rs_gap_median` | 10 | 0.08 | 0.005 |  | median of per-municipality gaps | unverified |
| `rs_r_edu_work` | 10 | 0.82 | 0.01 |  |  | unverified |
| `rs_single_settlement` | 10 | 8 | 0 |  |  | unverified |
| `rs_r_gap_urb_pop` | 10 | 0.03 | 0.02 |  |  | unverified |
| `rs_r_gap_urb_area` | 10 | -0.28 | 0.02 |  | negative control | unverified |
| `nl_jobs_2014` | 11 | 7.54e6 | 0.01e6 |  |  | unverified |
| `nl_sc_median` | 11 | 0.66 | 0.005 |  |  | unverified |
| `nl_share_pass` | 11 | 0.2 | 0.0 |  | 8 of 40 | unverified |
| `nl_areas` | 11 | 2 | 0 |  |  | unverified |
| `nl_sc_delfzijl` | 11 | 0.45 | 0.005 |  |  | unverified |
| `nl_sc_zvl` | 11 | 0.88 | 0.005 |  |  | unverified |
| `jp_local_share_ward` | 12 | 0.27 | 0.005 |  |  | unverified |
| `jp_ratio_max` | 12 | 7.9 | 0.1 |  |  | unverified |
| `jp_ratio_min` | 12 | 0.13 | 0.01 |  |  | unverified |
| `jp_sig_mixed` | 13 | 155 | 0 | analysis.signatures.classify |  | unverified |
| `jp_sig_residential` | 13 | 102 | 0 |  |  | unverified |
| `jp_sig_leisure` | 13 | 50 | 0 |  |  | unverified |
| `jp_sig_office` | 13 | 115 | 0 |  |  | unverified |
| `jp_hdbscan_noise` | 13 | 1.0 | 0.0 |  |  | unverified |
| `jp_volume_drift` | 14 | 0.003 | 0.001 |  | max |Δ total| across 2019–2021 | unverified |
| `jp_local_share_2019` | 14 | 0.632 | 0.002 |  |  | unverified |
| `jp_local_share_2020` | 14 | 0.677 | 0.002 |  |  | unverified |
