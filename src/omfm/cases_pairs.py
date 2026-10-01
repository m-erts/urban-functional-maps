"""Cases added in revision 2: the Coombes-Bond algorithm (Istat implementation), the recombination
null, and two more countries with origin-destination pairs (Netherlands 2023, Spain 2023).

The Coombes-Bond partitions are computed in R (``r/run_lma.R``) because that is where the
reference implementation lives; their outputs are committed in ``outputs/tables/*_areas_lma.csv``
and read here. Everything else runs in Python.
"""

from __future__ import annotations

import pandas as pd

from .analysis import agreement as A
from .analysis import contiguity as C
from .analysis import delimitation as D
from .analysis import nullmodel as N
from .analysis import recom as R
from .analysis import selfcontainment as SC
from .analysis import ttwa as T
from .config import params, path

__all__ = ["lma_uk", "netherlands_municipal", "spain", "decomposition"]


def _tab(name: str):
    return path("tables", name, mkdir=True)


def _read_lma(name: str) -> pd.Series:
    """Partition written by ``r/run_lma.R``; raises if the R step has not been run."""
    f = _tab(name)
    if not f.exists():
        raise FileNotFoundError(f"{f.name} missing: run r/run_lma.R first (see README, 'Coombes-Bond step')")
    d = pd.read_csv(f, dtype={"unit": str, "area": str})
    return pd.Series(d.area.to_numpy(), index=d.unit.to_numpy(), name="area")


def _lma_seconds(name: str) -> float:
    """Run time of the R step, from the file ``r/run_lma.R`` writes next to its output."""
    return float(pd.read_csv(_tab(name.replace(".csv", "_run.csv"))).seconds.iloc[0])


def _adjacency(g, key: str) -> dict:
    cache = path("interim", f"adj_{key}.parquet", mkdir=True)
    if cache.exists():
        edges = pd.read_parquet(cache)
    else:
        adj = C.queen_adjacency(g, "unit")
        edges = pd.DataFrame([(a, b) for a, nb in adj.items() for b in nb if a < b], columns=["a", "b"])
        edges.to_parquet(cache)
    adj: dict = {u: set() for u in g.unit}
    for a, b in edges.itertuples(index=False):
        adj[a].add(b)
        adj[b].add(a)
    return adj


def _centroids(g) -> pd.DataFrame:
    c = g.set_index("unit").geometry.representative_point()
    return pd.DataFrame({"x": c.x, "y": c.y})


def _own(od: pd.DataFrame, adj: dict) -> pd.Series:
    """The two-rule delimitation with the parameters used for England and Wales, then contiguity repair."""
    dl = params()["uk"]["delimitation"]
    asg = D.delimit(od, dl["core_quantile"], dl["merge_threshold"], dl["attach_threshold"], dl["min_job_ratio"])
    lab = asg.dropna(subset=["area"]).set_index("unit").area
    cores = set(asg[asg.is_core].unit)
    lab = lab[lab.index.isin(adj)]
    return pd.Series(C.repair(od, dict(lab), adj, cores), name="area")


def _validity(od: pd.DataFrame, labels: pd.Series) -> float:
    st = SC.two_sided_sc(od, labels)
    return float(T.is_valid(st).mean())


def _decompose(od, labels, adj, cen, tag: str) -> dict:
    """Self-containment split into scale, contiguity and placement, with the recombination null.

    The result is cached in ``data/interim`` under a key made of the partition, the chain settings and
    the seed, so an unchanged partition is not run again.
    """
    import hashlib
    import json

    cfg, seed = params()["recom"], params()["project"]["seed"]
    labels = labels[labels.index.isin(adj)].dropna()
    key = hashlib.sha256(
        (
            json.dumps(sorted(map(list, zip(labels.index.astype(str), labels.astype(str)))))
            + json.dumps(cfg)
            + str(seed)
            + f"{float(od.flow.sum()):.3f}"
        ).encode()
    ).hexdigest()[:16]
    cache = path("interim", f"recom_{tag}_{key}.json", mkdir=True)
    if cache.exists():
        return json.loads(cache.read_text())
    e = N.expected_sc(od, labels)
    r = R.recom_null(
        od,
        labels,
        adj,
        steps=cfg["steps"],
        burn_in=cfg["burn_in"],
        every=cfg["every"],
        tol=cfg["tolerance"],
        seed=seed,
        centroids=cen,
    )
    r["trace"].to_csv(_tab(f"recom_trace_{tag}.csv"), index=False)
    row = {
        "partition": tag,
        "areas": int(labels.nunique()),
        "units": int(labels.size),
        "effective_areas": N.effective_areas(labels),
        "observed": r["observed"],
        "scale_null": e["expected"],
        "recom_mean": r["recom_mean"],
        "recom_sd": r["recom_sd"],
        "recom_min": r["recom_min"],
        "recom_max": r["recom_max"],
        "effective_areas_null": r["effective_areas_null"],
        "acceptance": r["acceptance"],
        "ari_with_start_mean": r["ari_with_start_mean"],
        "ari_between_samples_mean": r["ari_between_samples_mean"],
        "samples": r["samples"],
        "share_of_null_below_observed": r["share_below_observed"],
        "from_scale": e["expected"],
        "from_contiguity": r["recom_mean"] - e["expected"],
        "from_placement": r["observed"] - r["recom_mean"],
    }
    cache.write_text(json.dumps(row))
    return row


# ------------------------------------------------------------------ England and Wales, Coombes-Bond
def lma_uk() -> dict:
    """The Istat implementation of Coombes-Bond with the parameters of the 2011 official areas."""
    from .sources import uk_census as src

    od = pd.read_parquet(path("interim", "uk_od_2011.parquet"))
    lma = _read_lma("uk_2011_areas_lma.csv")
    g = src.load_boundaries(2011)
    adj = _adjacency(g, "uk_2011")
    weights = od.groupby("origin").flow.sum()
    ref = src.msoa_to_ttwa(2011).set_index("unit").ttwa
    ref = ref.reindex(sorted(set(od.origin) | set(od.dest))).dropna()
    own = pd.read_csv(_tab("uk_2011_areas_contiguous.csv"), dtype=str).set_index("unit").area
    frag = C.fragmentation_report(dict(lma), adj)
    out = {
        "uk_lma_areas_2011": int(lma.nunique()),
        "uk_lma_unassigned_2011": int(len(set(od.origin) | set(od.dest)) - lma.size),
        "uk_lma_noncontig_2011": int((frag.n_components > 1).sum()),
        "uk_lma_valid_share_2011": _validity(od, lma),
        "uk_lma_sc_2011": SC.partition_sc(od, lma),
        "uk_lma_largest_share_2011": float(SC.two_sided_sc(od, lma).residents.max() / weights.sum()),
        "uk_lma_seconds_2011": _lma_seconds("uk_2011_areas_lma.csv"),
    }
    area_w = g.set_index("unit").area / 1e6
    rows = []
    for name, part, reference in [("lma", lma, ref), ("own", own, ref), ("lma_vs_own", lma, own)]:
        s = A.summary(part, reference, weights)
        rows.append({"comparison": name, **s})
        out[f"uk_ari_{name}_2011"] = s["ari_weighted"]
        out[f"uk_iou_{name}_2011"] = s["mean_iou_weighted"]
        out[f"uk_median_iou_{name}_2011"] = s["median_iou"]
        out[f"uk_iou_area_{name}_2011"] = A.summary(part, reference, area_w)["mean_iou_weighted"]
    if _tab("uk_2011_areas_lma_ons.csv").exists():
        # the same algorithm on the matrix as ONS coded it: home workers counted at their residence
        ons = pd.read_parquet(path("interim", "uk_od_2011_ons.parquet"))
        lo = _read_lma("uk_2011_areas_lma_ons.csv")
        s = A.summary(lo, ref, weights)
        rows.append({"comparison": "lma_ons", **s})
        out.update(
            {
                "uk_lma_ons_areas_2011": int(lo.nunique()),
                "uk_lma_ons_unassigned_2011": int(len(set(ons.origin) | set(ons.dest)) - lo.size),
                "uk_lma_ons_noncontig_2011": int((C.fragmentation_report(dict(lo), adj).n_components > 1).sum()),
                "uk_lma_ons_valid_share_2011": _validity(ons, lo),
                "uk_lma_ons_largest_share_2011": float(
                    SC.two_sided_sc(ons, lo).residents.max() / ons.groupby("origin").flow.sum().sum()
                ),
                "uk_ari_lma_ons_2011": s["ari_weighted"],
                "uk_iou_lma_ons_2011": s["mean_iou_weighted"],
                "uk_median_iou_lma_ons_2011": s["median_iou"],
                "uk_iou_area_lma_ons_2011": A.summary(lo, ref, area_w)["mean_iou_weighted"],
                "uk_ari_lma_ons_vs_lma_2011": A.summary(lo, lma, weights)["ari_weighted"],
                "uk_lma_ons_seconds_2011": _lma_seconds("uk_2011_areas_lma_ons.csv"),
                "uk_diag_2011_ons": SC.unit_diagonal_share(ons),
                "uk_ons_added_2011": float(ons.flow.sum() - od.flow.sum()),
            }
        )
    pd.DataFrame(rows).to_csv(_tab("uk_lma_agreement.csv"), index=False)
    c = A.contingency(lma, ref, weights)
    A.match_report(c).sort_values("weight", ascending=False).to_csv(_tab("uk_2011_lma_match_report.csv"))
    return out


# ------------------------------------------------------------------------ Netherlands, 2023 pairs
def netherlands_municipal() -> dict:
    from .sources import nl_cbs as src

    cfg = params()["netherlands"]["municipal"]
    raw = src.fetch_municipal()
    od, retained = src.municipal_matrix(raw)
    od.to_parquet(path("interim", "nl_od_2023.parquet", mkdir=True))
    od.to_csv(path("interim", "nl_od_2023.csv"), index=False)  # input of r/run_lma.R
    g = src.load_boundaries("gemeente_gegeneraliseerd", cfg["year"])
    corop_poly = src.load_boundaries("coropgebied_gegeneraliseerd", cfg["year"])
    pts = g.assign(geometry=g.representative_point())
    corop = pts.sjoin(corop_poly[["unit", "geometry"]].rename(columns={"unit": "corop"}), predicate="within")
    corop = corop.set_index("unit").corop
    corop.rename_axis("unit").to_csv(_tab("nl_2023_corop_assignment.csv"))
    adj = _adjacency(g, "nl_2023")
    weights = od.groupby("origin").flow.sum()

    own = _own(od, adj)
    own.rename_axis("unit").to_csv(_tab("nl_2023_areas_contiguous.csv"))
    lma = _read_lma("nl_2023_areas_lma.csv")
    corop_st = SC.two_sided_sc(od, corop)
    corop_st.to_csv(_tab("nl_2023_corop.csv"))

    out = {
        "nl23_units": int(len(set(od.origin) | set(od.dest))),
        "nl23_jobs": float(od.flow.sum()),
        "nl23_retained_total": float(
            od.flow.sum()
            / (
                raw[
                    (raw.dest == "NL01") & raw.origin.str.startswith("GM") & (raw.origin != src.UNKNOWN)
                ].jobs_thousands.sum()
                * 1000
            )
        ),
        "nl23_retained_median": float(retained.median()),
        "nl23_retained_min": float(retained.min()),
        "nl23_unknown_jobs": float(raw[(raw.origin == src.UNKNOWN) & (raw.dest == "NL01")].jobs_thousands.sum() * 1000),
        "nl23_diag": SC.unit_diagonal_share(od),
        "nl23_corop_sc_median": float(corop_st.sc_supply.median()),
        "nl23_corop_pass": float((corop_st.sc_supply >= params()["netherlands"]["pass_threshold"]).mean()),
        "nl23_corop_pass_two_sided": float((corop_st.sc_two_sided >= params()["netherlands"]["pass_threshold"]).mean()),
        "nl23_corop_valid_share": _validity(od, corop),
        "nl23_own_areas": int(own.nunique()),
        "nl23_own_unassigned": int(len(set(od.origin) | set(od.dest)) - own.size),
        "nl23_own_largest_share": float(weights.groupby(own).sum().max() / weights.sum()),
        "nl23_own_largest_holds_randstad": int(own.reindex(["GM0363", "GM0599", "GM0518", "GM0344"]).nunique() == 1),
        "nl23_lma_areas": int(lma.nunique()),
        "nl23_lma_unassigned": int(len(set(od.origin) | set(od.dest)) - lma.size),
        "nl23_lma_valid_share": _validity(od, lma),
        "nl23_lma_noncontig": int((C.fragmentation_report(dict(lma), adj).n_components > 1).sum()),
        "nl23_lma_seconds": _lma_seconds("nl_2023_areas_lma.csv"),
    }
    rows = []
    for name, part in [("own", own), ("lma", lma)]:
        s = A.summary(part, corop, weights)
        rows.append({"comparison": f"{name}_vs_corop", **s})
        out[f"nl23_ari_{name}_corop"] = s["ari_weighted"]
        out[f"nl23_iou_{name}_corop"] = s["mean_iou_weighted"]
    s = A.summary(own, lma, weights)
    rows.append({"comparison": "own_vs_lma", **s})
    out["nl23_ari_own_lma"] = s["ari_weighted"]
    pd.DataFrame(rows).to_csv(_tab("nl_2023_agreement.csv"), index=False)
    A.match_report(A.contingency(lma, corop, weights)).to_csv(_tab("nl_2023_lma_vs_corop.csv"))
    return out


# ------------------------------------------------------------------------------ Spain, 2023 trips
def spain() -> dict:
    from .sources import es_mitma as src

    cfg = params()["spain"]
    f_od, f_h = path("interim", "es_home_work_od.parquet", mkdir=True), path("interim", "es_hours.parquet")
    if not (f_od.exists() and f_h.exists()):  # about 8 minutes for five days of 180 MB each
        raw, hours = src.read_trips()
        raw.to_parquet(f_od)
        hours.to_parquet(f_h)
    raw, hours = pd.read_parquet(f_od), pd.read_parquet(f_h)
    od = src.home_to_work(raw, study=cfg["study"])
    od = od[od.flow > 0].reset_index(drop=True)
    od.to_parquet(path("interim", "es_od_work.parquet"))
    od.assign(flow=od.flow.round(3)).to_csv(path("interim", "es_od_2023.csv"), index=False)  # input of r/run_lma.R
    g = src.load_districts()
    adj = _adjacency(g, "es_districts")
    weights = od.groupby("origin").flow.sum()
    own = _own(od, adj)
    own.rename_axis("unit").to_csv(_tab("es_2023_areas_contiguous.csv"))
    lma = _read_lma("es_2023_areas_lma.csv")

    h = src.hourly(hours)
    h.to_csv(_tab("es_hourly.csv"))
    commute = h["casa > trabajo_estudio"]
    s = A.summary(own, lma, weights)
    pd.DataFrame([{"comparison": "own_vs_lma", **s}]).to_csv(_tab("es_2023_agreement.csv"), index=False)
    return {
        "es_days": len(cfg["days"]),
        "es_units": int(len(set(od.origin) | set(od.dest))),
        "es_districts": int(len(g)),
        "es_zones_spain": int(g.unit.str.match(r"^[0-9]").sum()),
        "es_zones_foreign": int((~g.unit.str.match(r"^[0-9]")).sum()),
        "es_units_foreign": int(sum(not str(u)[0].isdigit() for u in set(od.origin) | set(od.dest))),
        "es_trips_home_work": float(od.flow.sum()),
        "es_trips_home_work_study_all": float(src.home_to_work(raw, study="all").flow.sum()),
        "es_trips_all": float(hours.trips.sum()),
        "es_diag": SC.unit_diagonal_share(od),
        "es_commute_peak_hour": int(commute.idxmax()),
        "es_commute_share_6_9": float(commute.loc[6:9].sum() / commute.sum()),
        "es_own_areas": int(own.nunique()),
        "es_own_unassigned": int(len(set(od.origin) | set(od.dest)) - own.size),
        "es_own_unassigned_share": float(1 - weights.reindex(own.index).sum() / weights.sum()),
        "es_lma_areas": int(lma.nunique()),
        "es_lma_unassigned": int(len(set(od.origin) | set(od.dest)) - lma.size),
        "es_lma_valid_share": _validity(od, lma),
        "es_lma_noncontig": int((C.fragmentation_report(dict(lma), adj).n_components > 1).sum()),
        "es_lma_seconds": _lma_seconds("es_2023_areas_lma.csv"),
        "es_ari_own_lma": s["ari_weighted"],
        "es_iou_own_lma": s["mean_iou_weighted"],
    }


# ------------------------------------------------------------------------ decomposition, all pairs
def decomposition() -> dict:
    """Scale, contiguity and placement for every partition of the three countries with pairs."""
    from .sources import es_mitma as es
    from .sources import nl_cbs as nl
    from .sources import uk_census as uk

    jobs = []
    for yr in (2011, 2021):
        od = pd.read_parquet(path("interim", f"uk_od_{yr}.parquet"))
        g = uk.load_boundaries(yr)
        adj, cen = _adjacency(g, f"uk_{yr}"), _centroids(g)
        units = sorted(set(od.origin) | set(od.dest))
        ref = uk.msoa_to_ttwa(yr).set_index("unit").ttwa.reindex(units).dropna()
        own = pd.read_csv(_tab(f"uk_{yr}_areas_contiguous.csv"), dtype=str).set_index("unit").area
        jobs += [(f"uk_{yr}_own", od, own, adj, cen), (f"uk_{yr}_official", od, ref, adj, cen)]
        if yr == 2011 and _tab("uk_2011_areas_lma.csv").exists():
            jobs.append(("uk_2011_lma", od, _read_lma("uk_2011_areas_lma.csv"), adj, cen))
        if yr == 2011 and _tab("uk_2011_areas_lma_ons.csv").exists():  # evaluated on the same matrix as the rest
            jobs.append(("uk_2011_lma_ons", od, _read_lma("uk_2011_areas_lma_ons.csv"), adj, cen))

    od = pd.read_parquet(path("interim", "nl_od_2023.parquet"))
    g = nl.load_boundaries("gemeente_gegeneraliseerd", params()["netherlands"]["municipal"]["year"])
    adj, cen = _adjacency(g, "nl_2023"), _centroids(g)
    corop = pd.read_csv(_tab("nl_2023_corop_assignment.csv"), dtype=str).set_index("unit").corop
    own = pd.read_csv(_tab("nl_2023_areas_contiguous.csv"), dtype=str).set_index("unit").area
    jobs += [
        ("nl_2023_own", od, own, adj, cen),
        ("nl_2023_lma", od, _read_lma("nl_2023_areas_lma.csv"), adj, cen),
        ("nl_2023_corop", od, corop, adj, cen),
    ]

    od = pd.read_parquet(path("interim", "es_od_work.parquet"))
    g = es.load_districts()
    adj, cen = _adjacency(g, "es_districts"), _centroids(g)
    own = pd.read_csv(_tab("es_2023_areas_contiguous.csv"), dtype=str).set_index("unit").area
    jobs.append(("es_2023_own", od, own, adj, cen))
    if _tab("es_2023_areas_lma.csv").exists():
        jobs.append(("es_2023_lma", od, _read_lma("es_2023_areas_lma.csv"), adj, cen))

    rows = [_decompose(od_, lab, adj_, cen_, tag) for tag, od_, lab, adj_, cen_ in jobs]
    burn_in = params()["recom"]["burn_in"]
    for r in rows:
        r.update(R.trace_diagnostics(pd.read_csv(_tab(f"recom_trace_{r['partition']}.csv")), burn_in))
    df = pd.DataFrame(rows)
    df.to_csv(_tab("decomposition.csv"), index=False)
    out = {}
    for r in df.itertuples():
        for col in (
            "areas",
            "effective_areas",
            "observed",
            "scale_null",
            "recom_mean",
            "recom_sd",
            "recom_max",
            "effective_areas_null",
            "acceptance",
            "ari_with_start_mean",
            "ari_between_samples_mean",
            "from_scale",
            "from_contiguity",
            "from_placement",
            "share_of_null_below_observed",
        ):
            out[f"dec_{r.partition}_{col}"] = getattr(r, col)
        for part in ("scale", "contiguity", "placement"):
            out[f"dec_{r.partition}_share_{part}"] = getattr(r, f"from_{part}") / r.observed
    out["dec_recom_steps"] = params()["recom"]["steps"]
    out["dec_recom_samples"] = int(df.samples.iloc[0])
    out["dec_recom_tolerance"] = params()["recom"]["tolerance"]
    out["dec_recom_burn_in"] = params()["recom"]["burn_in"]
    out["dec_recom_every"] = params()["recom"]["every"]
    out["dec_partitions"] = int(len(df))
    out["dec_contiguity_share_min"] = float((df.from_contiguity / df.observed).min())
    out["dec_contiguity_share_max"] = float((df.from_contiguity / df.observed).max())
    out["dec_contiguity_largest_rows"] = int(
        ((df.from_contiguity > df.from_scale) & (df.from_contiguity > df.from_placement)).sum()
    )
    out["dec_placement_min"] = float(df.from_placement.min())
    out["dec_placement_max"] = float(df.from_placement.max())
    out["dec_placement_share_max"] = float((df.from_placement / df.observed).max())
    out["dec_ari_gap_max"] = float((df.ari_with_start_mean - df.ari_between_samples_mean).abs().max())
    out["dec_share_below_min"] = float(df.share_of_null_below_observed.min())
    out["dec_steps_to_range_max"] = int(df.steps_to_range.max())
    out["dec_lag1_min"] = float(df.lag1.min())
    out["dec_lag1_max"] = float(df.lag1.max())
    out["dec_geweke_abs_max"] = float(df.geweke_z.abs().max())
    return out
