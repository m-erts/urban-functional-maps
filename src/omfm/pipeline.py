"""End-to-end analysis: raw files -> tables in ``outputs/tables`` -> ``golden_actual.yaml``.

One function per case. Each returns a flat dict of the numbers that appear in the paper, the
slides and the README; `run` merges them and writes the register. Nothing here draws.
"""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
import yaml

from .analysis import agreement as A
from .analysis import contiguity as C
from .analysis import delimitation as D
from .analysis import diversity as V
from .analysis import nullmodel as N
from .analysis import osm as O
from .analysis import selfcontainment as SC
from .analysis import signatures as S
from .analysis import ttwa as T
from .config import ROOT, params, path

__all__ = ["uk", "uk_sweep", "uk_cases", "serbia", "netherlands", "japan", "osm", "run", "CASES"]


def _tab(name: str):
    return path("tables", name, mkdir=True)


def _labels(df: pd.DataFrame) -> pd.Series:
    d = df.dropna(subset=["area"])
    return pd.Series(d.area.to_numpy(), index=d.unit.to_numpy(), name="area")


def _null_row(od, labels, runs, seed, **tag) -> dict:
    r = N.shuffle_sc(od, labels, runs=runs, seed=seed)
    e = N.expected_sc(od, labels)
    return {
        **tag,
        "areas": int(labels.nunique()),
        "effective_areas": N.effective_areas(labels),
        "units": int(labels.size),
        "observed": r["observed"],
        "null_mean": r["null_mean"],
        "null_sd": r["null_sd"],
        "null_min": float(r["runs"].min()),
        "null_max": float(r["runs"].max()),
        "null_closed_form": e["expected"],
        "h": e["h"],
        "diagonal_share": e["diagonal_share"],
        "excess": r["excess"],
        "null_share": r["null_share"],
        "chance_corrected": (r["observed"] - r["null_mean"]) / (1 - r["null_mean"]),
        "modularity": N.modularity(od, labels),
        "runs": runs,
    }


# --------------------------------------------------------------------------- United Kingdom
def uk() -> dict:
    from .sources import uk_census as src

    cfg, seed = params()["uk"], params()["project"]["seed"]
    dl, runs = cfg["delimitation"], cfg["null_model"]["runs_paper"]
    out: dict = {}

    ind = src.indicator_totals_2021()
    sp = src.special_totals_2011()
    out["uk_home_2021"] = float(ind.xs(1, level=0).sum())
    out["uk_home_2011"] = float(sp["mainly at or from home"] + sp["no fixed place"])
    ind.rename("people").reset_index().to_csv(_tab("uk_2021_place_of_work_indicator.csv"), index=False)
    sp.rename("people").rename_axis("category").reset_index().to_csv(_tab("uk_2011_special_codes.csv"), index=False)

    od = {2011: src.read_od_2011(), 2021: src.read_od_2021("fixed")}
    naive = src.read_od_2021("naive")
    for yr, m in od.items():
        m.to_parquet(path("interim", f"uk_od_{yr}.parquet", mkdir=True))
    out["uk_msoa_n"] = len(set(od[2021].origin) | set(od[2021].dest))
    out["uk_msoa_n_2011"] = len(set(od[2011].origin) | set(od[2011].dest))
    out["uk_fixed_2021"], out["uk_fixed_2011"] = float(od[2021].flow.sum()), float(od[2011].flow.sum())
    out["uk_home_share_2021"] = out["uk_home_2021"] / float(ind[ind.index.get_level_values(0) > 0].sum())
    out["uk_diag_2011"] = SC.unit_diagonal_share(od[2011])
    out["uk_diag_2021_clean"] = SC.unit_diagonal_share(od[2021])
    out["uk_diag_2021_naive"] = SC.unit_diagonal_share(naive)

    null_rows, agree_rows, contig_rows = [], [], []
    for yr, m in od.items():
        asg = D.delimit(m, dl["core_quantile"], dl["merge_threshold"], dl["attach_threshold"], dl["min_job_ratio"])
        asg.to_csv(_tab(f"uk_{yr}_areas_flows_only.csv"), index=False)
        lab, cores = _labels(asg), set(asg[asg.is_core].unit)
        weights = m.groupby("origin").flow.sum()
        out[f"uk_cores_{yr}"] = int(asg.is_core.sum())
        out[f"uk_unassigned_{yr}"] = int(asg.area.isna().sum())

        g = src.load_boundaries(yr)
        adj = C.queen_adjacency(g, "unit")
        pd.DataFrame([(a, b) for a, nb in adj.items() for b in nb if a < b], columns=["a", "b"]).to_parquet(
            path("interim", f"uk_msoa_adj_{yr}.parquet", mkdir=True)
        )
        out[f"uk_adjacency_edges_{yr}"] = sum(len(v) for v in adj.values()) // 2
        before = C.fragmentation_report(dict(lab), adj)
        fixed = pd.Series(C.repair(m, dict(lab), adj, cores), name="area").rename_axis("unit")
        after = C.fragmentation_report(dict(fixed), adj)
        fixed.to_csv(_tab(f"uk_{yr}_areas_contiguous.csv"))
        after[after.n_components > 1].to_csv(_tab(f"uk_{yr}_islands.csv"), index=False)
        out[f"uk_noncontig_{yr}"] = int((before.n_components > 1).sum())
        out[f"uk_cut_units_{yr}"] = int(before.cut_units.sum())
        out[f"uk_islands_{yr}"] = int((after.n_components > 1).sum())
        out[f"uk_island_units_{yr}"] = int(after.cut_units.sum())
        out[f"uk_sc_contiguous_{yr}"] = SC.partition_sc(m, fixed)

        greedy = pd.Series(T.enforce_greedy_merge(m, dict(lab)), name="area").rename_axis("unit")
        dissolved = pd.Series(T.enforce_by_dissolution(m, dict(lab)), name="area").rename_axis("unit")
        greedy.to_csv(_tab(f"uk_{yr}_areas_ttwa_greedy.csv"))
        dissolved.to_csv(_tab(f"uk_{yr}_areas_ttwa_dissolution.csv"))
        for name, part in [("greedy", greedy), ("dissolution", dissolved)]:
            st = SC.two_sided_sc(m, part)
            out[f"uk_ttwa_{name}_{yr}"] = int(part.nunique())
            out[f"uk_ttwa_{name}_largest_{yr}"] = float(st.residents.max())
            out[f"uk_ttwa_{name}_largest_share_{yr}"] = float(st.residents.max() / st.residents.sum())

        ref = src.msoa_to_ttwa(yr).set_index("unit")
        ref = ref.reindex(sorted(set(m.origin) | set(m.dest))).dropna(subset=["ttwa"])
        out[f"uk_ttwa_official_touching_ew_{yr}"] = int(ref.ttwa.nunique())
        codes = pd.Series(ref.ttwa.unique())
        out["uk_ttwa_official"] = int(codes.str.startswith(("E30", "W22")).sum())
        out["uk_ttwa_official_cross_border"] = int(codes.str.startswith("K01").sum())
        out[f"uk_msoa_cut_by_ttwa_{yr}"] = int((ref.share < 1).sum())
        area_w = g.set_index("unit").area / 1e6

        # zoning effect: random contiguous partitions with the same area sizes
        full_adj = {u: adj.get(u, set()) for u in sorted(set(m.origin) | set(m.dest))}
        for name, part in [("contiguous", fixed), ("official_ttwa_2011", ref.ttwa)]:
            r = N.contiguous_null(m, part, full_adj, runs=cfg["null_model"]["runs_contiguous"], seed=seed)
            e = N.expected_sc(m, part)
            contig_rows.append(
                {
                    "year": yr,
                    "partition": name,
                    "areas": int(part.nunique()),
                    "effective_areas": N.effective_areas(part),
                    "observed": r["observed"],
                    "scale_null": e["expected"],
                    "contiguous_null": r["contiguous_mean"],
                    "contiguous_sd": r["contiguous_sd"],
                    "contiguous_min": r["contiguous_min"],
                    "contiguous_max": r["contiguous_max"],
                    "effective_areas_null": r["effective_areas_null"],
                    "from_scale": e["expected"],
                    "from_contiguity": r["contiguous_mean"] - e["expected"],
                    "from_placement": r["observed"] - r["contiguous_mean"],
                    "share_of_null_below_observed": r["share_below_observed"],
                    "runs": cfg["null_model"]["runs_contiguous"],
                }
            )

        parts = {"flows_only": lab, "contiguous": fixed, "ttwa_greedy": greedy, "ttwa_dissolution": dissolved}
        for name, part in parts.items():
            null_rows.append(_null_row(m, part, runs, seed, scale="MSOA", year=yr, partition=name))
            s = A.summary(part, ref.ttwa, weights)
            s_area = A.summary(part, ref.ttwa, area_w)
            agree_rows.append(
                {
                    "year": yr,
                    "partition": name,
                    **s,
                    "mean_iou_area": s_area["mean_iou_weighted"],
                    "ari_area": s_area["ari_weighted"],
                }
            )
        null_rows.append(_null_row(m, ref.ttwa, runs, seed, scale="MSOA", year=yr, partition="official_ttwa_2011"))

        c = A.contingency(fixed, ref.ttwa, weights)
        c.to_csv(_tab(f"uk_{yr}_error_matrix.csv"))
        rep = A.match_report(c).join(ref.drop_duplicates("ttwa").set_index("ttwa").ttwa_name)
        rep.sort_values("weight", ascending=False).to_csv(_tab(f"uk_{yr}_match_report.csv"))

    # district scale, same rules: what aggregation alone does to the score
    for mode in ("fixed", "naive"):
        lad = src.read_od_2021(mode, level="lad")
        for tag, p in [("q95", dl), ("q85", cfg["delimitation_lad"])]:
            asg = D.delimit(lad, p["core_quantile"], p["merge_threshold"], p["attach_threshold"], p["min_job_ratio"])
            null_rows.append(
                _null_row(lad, _labels(asg), runs, seed, scale="LAD", year=2021, partition=f"flows_only_{mode}_{tag}")
            )
        out[f"uk_lad_diag_{mode}"] = SC.unit_diagonal_share(lad)
    out["uk_lad_n"] = len(set(lad.origin) | set(lad.dest))
    out["uk_largest_area_unit_share_2021"] = float(
        pd.read_csv(_tab("uk_2021_areas_contiguous.csv")).area.value_counts(normalize=True).iloc[0]
    )

    cn = pd.DataFrame(contig_rows)
    cn.to_csv(_tab("uk_contiguous_null.csv"), index=False)
    for r in cn.itertuples():
        tag = "own" if r.partition == "contiguous" else "official"
        out[f"uk_{tag}_sc_{r.year}"] = r.observed
        out[f"uk_{tag}_from_scale_{r.year}"] = r.from_scale
        out[f"uk_{tag}_from_contiguity_{r.year}"] = r.from_contiguity
        out[f"uk_{tag}_from_placement_{r.year}"] = r.from_placement
        out[f"uk_{tag}_contiguous_null_{r.year}"] = r.contiguous_null
        out[f"uk_{tag}_contiguous_null_sd_{r.year}"] = r.contiguous_sd
        out[f"uk_{tag}_contiguous_null_max_{r.year}"] = r.contiguous_max
        out[f"uk_{tag}_contiguous_null_effective_areas_{r.year}"] = r.effective_areas_null
        out[f"uk_{tag}_effective_areas_{r.year}"] = r.effective_areas
    out["uk_own_contiguous_null_runs"] = int(cfg["null_model"]["runs_contiguous"])

    nm = pd.DataFrame(null_rows)
    nm.to_csv(_tab("uk_null_model.csv"), index=False)
    ag = pd.DataFrame(agree_rows)
    ag.to_csv(_tab("uk_agreement.csv"), index=False)

    def pick(scale, year, partition, col):
        r = nm[(nm.scale == scale) & (nm.year == year) & (nm.partition == partition)]
        return float(r[col].iloc[0])

    for yr in (2011, 2021):
        out[f"uk_areas_flows_only_{yr}"] = int(pick("MSOA", yr, "flows_only", "areas"))
        out[f"uk_effective_areas_{yr}"] = pick("MSOA", yr, "flows_only", "effective_areas")
        out[f"uk_sc_{yr}_areas"] = pick("MSOA", yr, "flows_only", "observed")
        out[f"uk_sc_{yr}_random"] = pick("MSOA", yr, "flows_only", "null_mean")
        out[f"uk_sc_{yr}_random_sd"] = pick("MSOA", yr, "flows_only", "null_sd")
        out[f"uk_sc_{yr}_closed_form"] = pick("MSOA", yr, "flows_only", "null_closed_form")
        out[f"uk_excess_msoa_{yr}"] = pick("MSOA", yr, "flows_only", "excess")
        out[f"uk_null_share_msoa_{yr}"] = pick("MSOA", yr, "flows_only", "null_share")
        out[f"uk_modularity_{yr}"] = pick("MSOA", yr, "contiguous", "modularity")
        out[f"uk_modularity_official_{yr}"] = pick("MSOA", yr, "official_ttwa_2011", "modularity")
        out[f"uk_sc_official_ttwa_{yr}"] = pick("MSOA", yr, "official_ttwa_2011", "observed")
        out[f"uk_sc_official_ttwa_random_{yr}"] = pick("MSOA", yr, "official_ttwa_2011", "null_mean")
        for name in ("flows_only", "contiguous", "ttwa_greedy", "ttwa_dissolution"):
            r = ag[(ag.year == yr) & (ag.partition == name)].iloc[0]
            out[f"uk_ari_{name}_{yr}"] = float(r.ari_weighted)
            out[f"uk_iou_{name}_{yr}"] = float(r.mean_iou_weighted)
            out[f"uk_iou_area_{name}_{yr}"] = float(r.mean_iou_area)
            out[f"uk_median_iou_{name}_{yr}"] = float(r.median_iou)
    out["uk_district_observed_clean"] = pick("LAD", 2021, "flows_only_fixed_q95", "observed")
    out["uk_district_random_clean"] = pick("LAD", 2021, "flows_only_fixed_q95", "null_mean")
    out["uk_district_random_clean_sd"] = pick("LAD", 2021, "flows_only_fixed_q95", "null_sd")
    out["uk_district_areas_clean"] = int(pick("LAD", 2021, "flows_only_fixed_q95", "areas"))
    out["uk_district_null_share_clean"] = pick("LAD", 2021, "flows_only_fixed_q95", "null_share")
    out["uk_district_observed_deck_v1"] = pick("LAD", 2021, "flows_only_naive_q85", "observed")
    out["uk_district_random_deck_v1"] = pick("LAD", 2021, "flows_only_naive_q85", "null_mean")
    return out


def uk_sweep() -> dict:
    """Iso-count experiment on the 2021 matrix.

    The number of areas is fixed by the core quantile and the core-merge threshold alone (it is
    the number of core groups). Step 1 counts core groups over a grid of those two. Step 2 takes
    every setting whose count falls within the tolerance of the reference count, runs the full
    delimitation for each attachment threshold, and compares the resulting maps with each other
    and with the official areas.
    """
    from .sources import uk_census as src

    cfg = params()["uk"]
    sw, ratio = cfg["sweep"], cfg["delimitation"]["min_job_ratio"]
    od = pd.read_parquet(path("interim", "uk_od_2021.parquet"))
    weights = od.groupby("origin").flow.sum()
    ref = src.msoa_to_ttwa(2021).set_index("unit").ttwa
    stats = D.unit_stats(od)

    grid = []
    for q, mt in itertools.product(sw["core_quantile"], sw["merge_threshold"]):
        cores = D.find_cores(stats, q, ratio)
        groups = len(set(D.merge_cores(od, cores, mt).values()))
        grid.append({"core_quantile": q, "merge_threshold": mt, "cores": len(cores), "areas": groups})
    grid = pd.DataFrame(grid)
    grid.to_csv(_tab("uk_sweep_counts.csv"), index=False)

    near = grid[(grid.areas - sw["target_areas"]).abs() <= sw["target_tolerance"]]
    rows, parts = [], {}
    for r in near.itertuples():
        for at in sw["attach_threshold"]:
            lab = _labels(D.delimit(od, r.core_quantile, r.merge_threshold, at, ratio))
            e = N.expected_sc(od, lab)
            sc = SC.partition_sc(od, lab)
            key = f"{r.core_quantile:g}/{r.merge_threshold:g}/{at:g}"
            c = A.contingency(lab, ref, weights)
            rows.append(
                {
                    "setting": key,
                    "core_quantile": r.core_quantile,
                    "merge_threshold": r.merge_threshold,
                    "attach_threshold": at,
                    "areas": int(lab.nunique()),
                    "assigned": int(lab.size),
                    "sc": sc,
                    "null": e["expected"],
                    "excess": sc - e["expected"],
                    "ari_official": A.adjusted_rand(c),
                    "mean_iou_official": float(np.average(A.match_report(c).iou, weights=A.match_report(c).weight)),
                }
            )
            parts[key] = lab
    df = pd.DataFrame(rows)
    df.to_csv(_tab("uk_sweep.csv"), index=False)
    pair = [
        {
            "a": a,
            "b": b,
            "same_cores": a.rsplit("/", 1)[0] == b.rsplit("/", 1)[0],
            "ari_weighted": A.adjusted_rand(A.contingency(parts[a], parts[b], weights)),
        }
        for a, b in itertools.combinations(parts, 2)
    ]
    pw = pd.DataFrame(pair)
    pw.to_csv(_tab("uk_sweep_pairwise_ari.csv"), index=False)
    other = pw[~pw.same_cores]
    return {
        "uk_sweep_grid": int(len(grid)),
        "uk_sweep_areas_min": int(grid.areas.min()),
        "uk_sweep_areas_max": int(grid.areas.max()),
        "uk_sweep_lo": int(sw["target_areas"] - sw["target_tolerance"]),
        "uk_sweep_hi": int(sw["target_areas"] + sw["target_tolerance"]),
        "uk_sweep_near_core_settings": int(len(near)),
        "uk_sweep_near_maps": int(len(df)),
        "uk_sweep_near_ari_min": float(pw.ari_weighted.min()),
        "uk_sweep_near_ari_median": float(pw.ari_weighted.median()),
        "uk_sweep_near_ari_max": float(pw.ari_weighted.max()),
        "uk_sweep_near_ari_median_other_cores": float(other.ari_weighted.median()),
        "uk_sweep_near_ari_official_min": float(df.ari_official.min()),
        "uk_sweep_near_ari_official_max": float(df.ari_official.max()),
        "uk_sweep_near_sc_min": float(df.sc.min()),
        "uk_sweep_near_sc_max": float(df.sc.max()),
    }


def uk_cases() -> dict:
    """Six cases of boundary divergence on the 2021 matrix, chosen by rule and not by eye.

    1, 2  the cut-off component with most employed residents that has a neighbour in another area,
          before and after the contiguity repair
    3     the component with most employed residents that the repair could not place
    4     the official area (over 100,000 employed residents, omission under 0.2) with the
          highest commission: it lies inside a larger delimited area
    5     the official area (over 100,000 employed residents) with the highest omission
    6     the unit with the lowest plurality share: the official boundary cuts it
    """
    import json

    from .sources import uk_census as src

    od = pd.read_parquet(path("interim", "uk_od_2021.parquet"))
    edges = pd.read_parquet(path("interim", "uk_msoa_adj_2021.parquet"))
    adj: dict = {}
    for a_, b_ in edges.itertuples(index=False):
        adj.setdefault(a_, set()).add(b_)
        adj.setdefault(b_, set()).add(a_)
    flows = _labels(pd.read_csv(_tab("uk_2021_areas_flows_only.csv")))
    fixed = pd.read_csv(_tab("uk_2021_areas_contiguous.csv")).set_index("unit").area
    weight = od.groupby("origin").flow.sum()
    lut = src.msoa_to_ttwa(2021).set_index("unit")
    names = (
        pd.read_json(path("raw", params()["uk"]["lookup_oa21_msoa21"]))[["MSOA21CD", "MSOA21NM"]]
        .drop_duplicates()
        .set_index("MSOA21CD")
        .MSOA21NM
    )
    geo = src.load_boundaries(2021).set_index("unit").geometry

    def place(unit: str) -> str:
        return names[unit].rsplit(" ", 1)[0]

    def fragments(lab: pd.Series) -> pd.DataFrame:
        rows = []
        for area, units in lab.groupby(lab).groups.items():
            for comp in C.components(list(units), adj)[1:]:
                nb = {lab[v] for u in comp for v in adj.get(u, ()) if v in lab.index and lab[v] != area}
                rows.append(
                    {
                        "area": area,
                        "units": sorted(comp),
                        "island": not nb,
                        "workers": float(weight.reindex(list(comp)).sum()),
                    }
                )
        return pd.DataFrame(rows).sort_values(["workers", "area"], ascending=[False, True])

    before, after = fragments(flows), fragments(fixed)
    tele = before[~before.island].iloc[0]
    isle = after.iloc[0]
    rep = pd.read_csv(_tab("uk_2021_match_report.csv"))
    big = rep[rep.weight > 100_000]
    swallowed = big[big.omission < 0.2].sort_values("commission", ascending=False).iloc[0]
    split = big.sort_values("omission", ascending=False).iloc[0]
    cut = lut[lut.index.isin(geo.index)].sort_values(["share", "ttwa"]).iloc[0]

    body = flows[flows == tele.area].index.difference(tele.units)
    distance = float(geo.loc[tele.units].union_all().distance(geo.loc[list(body)].union_all())) / 1000
    new_area = fixed[tele.units[0]]
    cases = {
        "attachment": {"units": tele.units, "area": tele.area, "new_area": new_area},
        "island": {"units": isle.units, "area": isle.area},
        "swallowed": {"official": swallowed.reference, "match": swallowed.match},
        "split": {"official": split.reference, "match": split.match},
        "cut_unit": {"unit": cut.name, "official": cut.ttwa},
    }
    _tab("uk_edge_cases.json").write_text(json.dumps(cases, indent=1), encoding="utf-8")
    return {
        "uk_case_attach_units": len(tele.units),
        "uk_case_attach_workers": tele.workers,
        "uk_case_attach_distance_km": distance,
        "uk_case_attach_area": place(tele.area),
        "uk_case_attach_new_area": place(new_area),
        "uk_case_island_units": len(isle.units),
        "uk_case_island_workers": isle.workers,
        "uk_case_island_name": place(isle.units[0]),
        "uk_case_swallowed_name": str(swallowed.ttwa_name),
        "uk_case_swallowed_match": place(swallowed.match),
        "uk_case_swallowed_workers": float(swallowed.weight),
        "uk_case_swallowed_iou": float(swallowed.iou),
        "uk_case_swallowed_omission": float(swallowed.omission),
        "uk_case_swallowed_commission": float(swallowed.commission),
        "uk_case_split_name": str(split.ttwa_name),
        "uk_case_split_workers": float(split.weight),
        "uk_case_split_parts": int(split.n_candidates),
        "uk_case_split_iou": float(split.iou),
        "uk_case_split_omission": float(split.omission),
        "uk_case_split_held": float(1 - split.omission),
        "uk_case_swallowed_held": float(1 - swallowed.omission),
        "uk_case_cut_name": str(names[cut.name]),
        "uk_case_cut_share": float(cut.share),
        "uk_london_official_iou": float(rep[rep.ttwa_name == "London"].iou.iloc[0]),
        "uk_london_official_commission": float(rep[rep.ttwa_name == "London"].commission.iloc[0]),
        "uk_london_official_parts": int(rep[rep.ttwa_name == "London"].n_candidates.iloc[0]),
    }


# ------------------------------------------------------------------------------------ Serbia
def serbia() -> dict:
    from scipy.stats import spearmanr

    from .sources import ghsl
    from .sources import serbia_census as rc
    from .sources import serbia_geo as rg

    cfg = params()["serbia"]
    w = rc.add_self_containment(rc.read_daily_migration(path("raw", cfg["work"])))
    e = rc.add_self_containment(rc.read_daily_migration(path("raw", cfg["education"])))
    shp = f"zip://{path('raw', cfg['boundaries'])}!{cfg['boundaries_member']}"
    j = rg.join_census(rg.load_municipalities(shp), w)
    j = j.merge(e[["key", "sc", "total"]].rename(columns={"sc": "sc_edu", "total": "total_edu"}), on="key")
    j["gap"] = j.sc_edu - j.sc
    j["area_km2"] = j.to_crs(cfg["crs"]).area / 1e6
    u = ghsl.urbanisation(j)
    keep = [
        "matched",
        "name",
        "area",
        "total",
        "same_municipality",
        "total_edu",
        "sc",
        "sc_edu",
        "gap",
        "single_settlement",
        "area_km2",
        "pop_ghsl",
        "deg_urb",
        "deg_city",
        "area_urb",
        "clipped",
    ]
    u[keep].to_csv(_tab("rs_municipalities.csv"), index=False)
    u[keep + ["geometry"]].to_parquet(path("interim", "rs_municipalities.parquet", mkdir=True))

    real = u[~u.single_settlement.astype(bool)]
    d = real[(~real.clipped) & (real.pop_ghsl > 0)]
    rho = lambda a, b: float(spearmanr(a, b).statistic)  # noqa: E731
    return {
        "rs_municipalities": int(len(w)),
        "rs_workers": float(w.total.sum()),
        "rs_students": float(e.total.sum()),
        "rs_sc_national": float(w.same_municipality.sum() / w.total.sum()),
        "rs_single_settlement": int(w.single_settlement.sum()),
        "rs_structural_zero_matches_single": bool(set(w[w.sc == 0].name) == set(w[w.single_settlement].name)),
        "rs_sc_median_work": float(real.sc.median()),
        "rs_sc_median_edu": float(real.sc_edu.median()),
        "rs_share_pass_075_work": float((real.sc >= 0.75).mean()),
        "rs_share_pass_075_edu": float((real.sc_edu >= 0.75).mean()),
        "rs_gap_median": float(real.gap.median()),
        "rs_gap_of_medians": float(real.sc_edu.median() - real.sc.median()),
        "rs_gap_median_all168": float(u.gap.median()),
        "rs_r_edu_work": float(real.sc.corr(real.sc_edu)),
        "rs_rho_edu_work": rho(real.sc, real.sc_edu),
        "rs_r_edu_work_all168": float(u.sc.corr(u.sc_edu)),
        "rs_r_gap_urb_pop": float(d.gap.corr(d.deg_urb)),
        "rs_r_gap_urb_area": float(d.gap.corr(d.area_urb)),
        "rs_r_sc_urb_pop": float(d.sc.corr(d.deg_urb)),
        "rs_r_sc_urb_area": float(d.sc.corr(d.area_urb)),
        "rs_rho_sc_urb_pop": rho(d.sc, d.deg_urb),
        "rs_rho_sc_urb_area": rho(d.sc, d.area_urb),
        "rs_area_urb_median": float(d.area_urb.median()),
        "rs_deg_urb_median": float(d.deg_urb.median()),
        "rs_zero_urban": int((d.deg_urb == 0).sum()),
        "rs_n_urbanisation": int(len(d)),
        "rs_pop_ghsl": float(u.pop_ghsl.sum()),
        "rs_polygons_joined": int(u.matched.nunique()),
        "rs_largest_single_settlement_km2": float(u[u.single_settlement.astype(bool)].area_km2.max()),
    }


# ------------------------------------------------------------------------------- Netherlands
def netherlands() -> dict:
    from .sources import nl_cbs as src

    cfg = params()["netherlands"]
    df = src.load()
    od = src.corop_matrix(df)
    st = SC.two_sided_sc(od, pd.Series({u: u for u in od.origin.unique()}))
    names = _nl_region_names()
    st = st.join(names)
    st.to_csv(_tab("nl_corop.csv"))
    dl = cfg["delimitation"]
    asg = D.delimit(od, dl["core_quantile"], dl["merge_threshold"], dl["attach_threshold"], dl["min_job_ratio"])
    asg.to_csv(_tab("nl_areas.csv"), index=False)
    thr = cfg["pass_threshold"]
    return {
        "nl_regions": int(len(st)),
        "nl_jobs_2014": float(od.flow.sum()),
        "nl_sc_median": float(st.sc_supply.median()),
        "nl_sc_median_two_sided": float(st.sc_two_sided.median()),
        "nl_share_pass": float((st.sc_supply >= thr).mean()),
        "nl_share_pass_two_sided": float((st.sc_two_sided >= thr).mean()),
        "nl_sc_min": float(st.sc_supply.min()),
        "nl_sc_min_region": str(st.sc_supply.idxmin()),
        "nl_sc_max": float(st.sc_supply.max()),
        "nl_sc_max_region": str(st.sc_supply.idxmax()),
        "nl_sc_min_name": str(st.name[st.sc_supply.idxmin()]),
        "nl_sc_max_name": str(st.name[st.sc_supply.idxmax()]),
        "nl_areas": int(asg.area.nunique()),
        **{f"nl_sc_{k}": float(st.sc_supply[code]) for k, code in cfg["named_regions"].items()},
    }


def _nl_region_names() -> pd.Series:
    import requests

    cfg = params()["netherlands"]
    cache = path("interim", "nl_region_names.csv", mkdir=True)
    if not cache.exists():
        r = requests.get(f"{cfg['odata']}/{cfg['table_2014']}/WoonregioS", params={"$format": "json"}, timeout=60)
        pd.DataFrame([{"area": v["Key"].strip(), "name": v["Title"].strip()} for v in r.json()["value"]]).to_csv(
            cache, index=False
        )
    return pd.read_csv(cache).set_index("area").name


# ------------------------------------------------------------------------------------- Japan
def japan_profiles(mesh: pd.DataFrame, year: int) -> pd.DataFrame:
    """Mean monthly presence per cell for the four slots of the profile.

    Slots: weekday day, weekday night, holiday day, holiday night. A cell is kept when all four
    exist (published, i.e. at least 10 people, in at least one month of the year).
    ``volume`` is the sum of the four means.
    """
    y = mesh[(mesh.year == year) & mesh.dayflag.isin([0, 1]) & mesh.timezone.isin([0, 1])]
    pv = y.pivot_table(
        index=["mesh1kmid", "month"], columns=["dayflag", "timezone"], values="population", aggfunc="sum"
    )
    pv.columns = [{(1, 0): "wd_day", (1, 1): "wd_night", (0, 0): "hol_day", (0, 1): "hol_night"}[c] for c in pv.columns]
    m = pv.groupby("mesh1kmid").mean().dropna()
    ax = S.axes(m.wd_day, m.wd_night, m.hol_day)
    m["x"], m["y"] = ax.x.to_numpy(), ax.y.to_numpy()
    m["volume"] = m[["wd_day", "wd_night", "hol_day", "hol_night"]].sum(axis=1)
    return m


def japan() -> dict:
    from .sources import jp_mlit as src

    cfg = params()["japan"]
    seed = params()["project"]["seed"]
    mesh, ft, co = src.read_mesh(), src.read_fromto(), src.read_mesh_coords()
    mesh.to_parquet(path("interim", "jp_mesh1km.parquet", mkdir=True))
    ps = src.presence_shares(ft)
    out: dict = {}

    dn = cfg["daynight"]
    ward = ps[
        (ps.citycode == cfg["central_ward"])
        & (ps.year == dn["year"])
        & (ps.month == dn["month"])
        & (ps.dayflag == dn["dayflag"])
    ].set_index("timezone")
    out["jp_local_share_ward"] = float(ward.local_share[0])
    out["jp_local_share_ward_night"] = float(ward.local_share[1])

    wd = ft[(ft.dayflag == 1) & (ft.timezone == 0)].groupby(["year", "from_area"]).population.sum().unstack()
    share = wd[0] / wd.sum(axis=1)
    for yr in (2019, 2020, 2021):
        out[f"jp_local_share_{yr}"] = float(share[yr])
    drift = []
    for (dflag, tz), g in ft.groupby(["dayflag", "timezone"]):
        t = g.groupby("year").population.sum()
        drift.append(
            {
                "product": "fromto",
                "dayflag": dflag,
                "timezone": tz,
                "max_abs_dev": float((t / t.mean() - 1).abs().max()),
            }
        )
    for (dflag, tz), g in mesh.groupby(["dayflag", "timezone"]):
        t = g.groupby("year").population.sum()
        drift.append(
            {"product": "mesh", "dayflag": dflag, "timezone": tz, "max_abs_dev": float((t / t.mean() - 1).abs().max())}
        )
    drift = pd.DataFrame(drift)
    drift.to_csv(_tab("jp_volume_drift.csv"), index=False)
    out["jp_volume_drift"] = float(drift.max_abs_dev.max())

    x = mesh[(mesh.year == dn["year"]) & (mesh.month == dn["month"]) & (mesh.dayflag == dn["dayflag"])]
    p = x[x.timezone.isin([0, 1])].pivot_table(
        index="mesh1kmid", columns="timezone", values="population", aggfunc="sum"
    )
    p.columns = ["day", "night"]
    p = p.dropna().join(co, how="inner")
    p["ratio"] = p.day / p.night
    p.to_csv(_tab("jp_daynight_cells.csv"))
    w = cfg["map_window"]
    v = p[p.lon_center.between(w[0], w[1]) & p.lat_center.between(w[2], w[3])]
    lim = float(np.nanpercentile(np.abs(np.log2(v.ratio)), 97))
    out.update(
        {
            "jp_daynight_cells": int(len(p)),
            "jp_ratio_median": float(p.ratio.median()),
            "jp_ratio_share_above_1": float((p.ratio > 1).mean()),
            "jp_ratio_max": float(2**lim),
            "jp_ratio_min": float(2**-lim),
            "jp_ratio_true_max": float(v.ratio.max()),
            "jp_ratio_true_min": float(v.ratio.min()),
        }
    )

    sg = cfg["signatures"]
    prof = japan_profiles(mesh, sg["year"]).join(co, how="left")
    prof["signature"] = S.classify(prof.x, prof.y, sg["threshold_ratio"], tuple(sg["precedence"]))
    cw = cfg["city_window"]
    prof["in_window"] = prof.lon_center.between(cw[0], cw[1]) & prof.lat_center.between(cw[2], cw[3])
    prof["in_city"] = prof.citycode.isin(cfg["city_codes"])
    prof.to_csv(_tab("jp_signatures.csv"))
    out["jp_profile_cells"] = int(len(prof))
    shares = prof.signature.value_counts(normalize=True)
    sel = prof[prof.in_window & (prof.volume >= sg["min_people_per_cell"])]
    counts = sel.signature.value_counts()
    for k in S.CLASSES:
        out[f"jp_sig_{k}"] = int(counts.get(k, 0))
        out[f"jp_sig_share_{k}"] = float(shares.get(k, 0.0))
    out["jp_sig_cells"] = int(len(sel))
    out["jp_sig_cells_city_admin"] = int((prof.in_city & (prof.volume >= sg["min_people_per_cell"])).sum())
    two = ((prof.x.abs() >= np.log2(sg["threshold_ratio"])) & (prof.y >= np.log2(sg["threshold_ratio"]))).mean()
    out["jp_sig_two_rules_fire"] = float(two)

    rows = []
    for ratio in sg["threshold_sweep"]:
        c = pd.Series(S.classify(prof.x, prof.y, ratio, tuple(sg["precedence"]))).value_counts()
        prf = V.profile(c.to_numpy())
        rows.append(
            {
                "threshold_ratio": ratio,
                **{k: int(c.get(k, 0)) for k in S.CLASSES},
                "mixed_share": float(c.get("mixed", 0) / c.sum()),
                "shannon": prf["shannon"],
                "evenness": prf["evenness"],
                "hill_q2": prf["hill_q2"],
            }
        )
    pd.DataFrame(rows).to_csv(_tab("jp_threshold_sweep.csv"), index=False)
    base = next(r for r in rows if r["threshold_ratio"] == sg["threshold_ratio"])
    out["jp_sig_entropy"], out["jp_sig_evenness"] = base["shannon"], base["evenness"]
    out["jp_sig_mixed_share_min"] = min(r["mixed_share"] for r in rows)
    out["jp_sig_mixed_share_max"] = max(r["mixed_share"] for r in rows)

    X = prof[["x", "y"]].to_numpy()
    hs = S.hdbscan_sweep(X, cfg["hdbscan"]["min_cluster_size"], cfg["hdbscan"]["min_samples"])
    hs.to_csv(_tab("jp_hdbscan_sweep.csv"), index=False)
    comp = prof[["wd_day", "wd_night", "hol_day", "hol_night"]].div(prof.volume, axis=0).to_numpy()
    hc = S.hdbscan_sweep(comp, cfg["hdbscan"]["min_cluster_size"], cfg["hdbscan"]["min_samples"])
    hc.to_csv(_tab("jp_hdbscan_sweep_composition.csv"), index=False)
    km = S.kmeans_silhouette(X, cfg["kmeans_k"], seed)
    km.to_csv(_tab("jp_kmeans.csv"), index=False)
    hop = [S.hopkins(X, seed=s) for s in range(20)]
    out.update(
        {
            "jp_hdbscan_noise_min": float(hs.noise_share.min()),
            "jp_hdbscan_noise_max": float(hs.noise_share.max()),
            "jp_hdbscan_clusters_max": int(hs.n_clusters.max()),
            "jp_hdbscan_largest_cluster_share_max": float(hs.largest_cluster_share.max()),
            "jp_hdbscan_comp_noise_min": float(hc.noise_share.min()),
            "jp_hdbscan_comp_noise_max": float(hc.noise_share.max()),
            "jp_hdbscan_comp_clusters_max": int(hc.n_clusters.max()),
            "jp_hdbscan_settings": int(len(hc)),
            "jp_hdbscan_comp_all_noise_settings": int((hc.noise_share == 1).sum()),
            "jp_hdbscan_comp_noise_max_partial": float(hc.noise_share[hc.noise_share < 1].max()),
            "jp_hdbscan_comp_largest_cluster_share_max": float(hc.largest_cluster_share.max()),
            "jp_hopkins": float(np.mean(hop)),
            "jp_hopkins_sd": float(np.std(hop, ddof=1)),
            "jp_kmeans4_silhouette": float(km.set_index("k").silhouette[4]),
            "jp_kmeans_best_silhouette": float(km.silhouette.max()),
        }
    )
    return out


# --------------------------------------------------------------------------------- OSM traces
def osm() -> dict:
    import h3

    from .sources import jp_mlit

    cfg, res = params()["osm_traces"], params()["osm_traces"]["h3_resolution"]
    cached = params()["overture"]["cached"]
    out, rows, counts = {}, [], {}
    for window in cfg["windows"]:
        t = pd.read_csv(path("raw", f"OSM/osm_traces_{window}.csv"))
        cells = pd.Series([h3.latlng_to_cell(a, b, res) for a, b in zip(t.lat, t.lon)])
        counts[window] = cells.value_counts()
        city = window.split("_")[0]
        row = {
            "window": window,
            "points": int(len(t)),
            "cap": cfg["points_per_page"] * cfg["pages_per_box"],
            "with_timestamp": float(pd.to_datetime(t.time, errors="coerce", utc=True).notna().mean()),
            "unique_minutes": O.unique_minutes(t),
            "median_year": O.median_year(t),
            "cells": int(cells.nunique()),
            "top_cell_share": O.top_cell_share(cells),
        }
        if city in cached:
            g = pd.read_parquet(ROOT / cached[city])
            poi = pd.Series(g.poi_count.to_numpy(), index=[h3.int_to_str(int(c)) for c in g.cell])
            row.update({f"overture_{k}": v for k, v in O.spearman_shared(counts[window], poi).items()})
            counts[f"poi_{city}"] = poi
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(_tab("osm_summary.csv"), index=False)
    key = {"hiroshima_centre": "hij", "belgrade_centre": "bgd", "london_soho": "lon"}
    for r in df.itertuples():
        k = key[r.window]
        out[f"osm_{k}_points"], out[f"osm_{k}_unique_min"] = r.points, r.unique_minutes
        out[f"osm_{k}_median_year"], out[f"osm_{k}_top_cell"] = r.median_year, r.top_cell_share
        if not np.isnan(getattr(r, "overture_rho", np.nan)):
            out[f"osm_{k}_spearman"], out[f"osm_{k}_spearman_n"] = r.overture_rho, int(r.overture_n)

    # Hiroshima: do traces rank cells like people (MLIT daytime presence) or like mapped places?
    _jp, dn = params()["japan"], params()["japan"]["daynight"]
    mesh = jp_mlit.read_mesh()
    day = (
        mesh[
            (mesh.year == dn["year"])
            & (mesh.month == dn["month"])
            & (mesh.dayflag == dn["dayflag"])
            & (mesh.timezone == 0)
        ]
        .groupby("mesh1kmid")
        .population.sum()
    )
    day = day.to_frame("day").join(jp_mlit.read_mesh_coords(), how="inner")
    day["h3"] = [h3.latlng_to_cell(a, b, res) for a, b in zip(day.lat_center, day.lon_center)]
    presence = day.groupby("h3").day.sum()
    j = pd.concat(
        {"traces": counts["hiroshima_centre"], "presence": presence, "places": counts["poi_hiroshima"]}, axis=1
    ).dropna()
    rho = j.corr(method="spearman")
    j.to_csv(_tab("osm_hiroshima_three_way.csv"))
    out.update(
        {
            "osm_hij_three_way_n": int(len(j)),
            "osm_hij_rho_traces_presence": float(rho.loc["traces", "presence"]),
            "osm_hij_rho_traces_places": float(rho.loc["traces", "places"]),
            "osm_hij_rho_presence_places": float(rho.loc["presence", "places"]),
        }
    )
    for k in ("traces_presence", "traces_places"):
        lo, hi = O.spearman_interval(out[f"osm_hij_rho_{k}"], len(j))
        out[f"osm_hij_rho_{k}_lo"], out[f"osm_hij_rho_{k}_hi"] = lo, hi
    wide = O.spearman_shared(presence, counts["poi_hiroshima"])
    out["osm_hij_rho_presence_places_city"], out["osm_hij_rho_presence_places_city_n"] = wide["rho"], wide["n"]
    return out


CASES = {
    "uk": uk,
    "uk_sweep": uk_sweep,
    "uk_cases": uk_cases,
    "rs": serbia,
    "nl": netherlands,
    "jp": japan,
    "osm": osm,
}


def _plain(v):
    if isinstance(v, (np.floating, float)):
        return round(float(v), 6)
    if isinstance(v, (np.integer, int)) and not isinstance(v, bool):
        return int(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    return v


def run(only: list[str] | None = None) -> dict:
    """Run the selected cases and merge their numbers into ``golden_actual.yaml``."""
    target = _tab("golden_actual.yaml")
    # a full run starts from nothing, so no number of an earlier version can survive in the file
    actual = yaml.safe_load(target.read_text()) if (only and target.exists()) else {}
    import time

    timing = _tab("runtime.csv")
    times = pd.read_csv(timing).set_index("case").seconds.to_dict() if timing.exists() else {}
    for key in only or list(CASES):
        print(f"[omfm] {key} ...", flush=True)
        t0 = time.perf_counter()
        actual.update({k: _plain(v) for k, v in CASES[key]().items()})
        times[key] = round(time.perf_counter() - t0, 1)
        target.write_text(yaml.safe_dump(dict(sorted(actual.items())), allow_unicode=True, sort_keys=True))
        pd.Series(times, name="seconds").rename_axis("case").to_csv(timing)
    return actual
