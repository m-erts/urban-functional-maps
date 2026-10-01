"""Functional-area delimitation from an origin-destination table.

Two declared rules, applied to flows only:

1. cores   - units whose external inflow is at or above a quantile and which hold at least as
             many jobs as employed residents; cores exchanging a large share of their external
             outflow are merged (union-find), so a polycentric centre is one core group;
2. attach  - every other unit joins the area that receives the largest share of its external
             outflow, if that share reaches the threshold; repeated until nothing changes.

This is a commuting-threshold heuristic in the OECD functional-urban-area family. It is NOT the
ONS / Coombes-Bond travel-to-work-area algorithm; `omfm.analysis.agreement` measures the distance
between the two.

OD convention everywhere: DataFrame with columns ``origin``, ``dest``, ``flow``.
"""

from __future__ import annotations

import pandas as pd

__all__ = ["prepare_od", "unit_stats", "find_cores", "merge_cores", "delimit", "area_summary"]


def prepare_od(df: pd.DataFrame, o_col: str, d_col: str, w_col: str) -> pd.DataFrame:
    """Coerce any OD table to ``origin, dest, flow`` with positive flows and unique pairs."""
    od = df[[o_col, d_col, w_col]].rename(columns={o_col: "origin", d_col: "dest", w_col: "flow"})
    od["origin"] = od["origin"].astype(str).str.strip()
    od["dest"] = od["dest"].astype(str).str.strip()
    od["flow"] = pd.to_numeric(od["flow"], errors="coerce")
    od = od[od["flow"] > 0]
    return od.groupby(["origin", "dest"], as_index=False)["flow"].sum()


def unit_stats(od: pd.DataFrame) -> pd.DataFrame:
    """Per unit: internal flow, totals, external in/out, self-containment, job ratio."""
    internal = od[od.origin == od.dest].set_index("origin")["flow"]
    out_all = od.groupby("origin")["flow"].sum()
    in_all = od.groupby("dest")["flow"].sum()
    s = pd.DataFrame(
        {
            "internal": internal,
            "out_total": out_all,
            "in_total": in_all,
            "out_external": out_all.sub(internal, fill_value=0),
            "in_external": in_all.sub(internal, fill_value=0),
        }
    ).fillna(0.0)
    s["self_containment"] = (s.internal / s.out_total).where(s.out_total > 0)
    s["job_ratio"] = (s.in_total / s.out_total).where(s.out_total > 0)
    return s.sort_values("in_external", ascending=False)


def find_cores(stats: pd.DataFrame, inflow_quantile: float, min_job_ratio: float = 1.0) -> list[str]:
    """Units with external inflow >= quantile and job ratio >= ``min_job_ratio``."""
    thr = stats.in_external.quantile(inflow_quantile)
    return list(stats[(stats.in_external >= thr) & (stats.job_ratio >= min_job_ratio)].index)


def merge_cores(od: pd.DataFrame, cores: list[str], merge_thr: float) -> dict[str, str]:
    """Group cores linked by a flow >= ``merge_thr`` of the sender's external outflow.

    Returns core -> head, where the head of a group is its member with the largest external inflow.
    """
    cs = set(cores)
    ext_all = od[od.origin != od.dest]
    ext = ext_all[ext_all.origin.isin(cs) & ext_all.dest.isin(cs)]
    out_ext = ext_all.groupby("origin")["flow"].sum()
    parent = {c: c for c in cores}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for r in ext.itertuples():
        denom = out_ext.get(r.origin, 0)
        if denom > 0 and r.flow / denom >= merge_thr:
            ra, rb = find(r.origin), find(r.dest)
            if ra != rb:
                parent[rb] = ra

    groups: dict[str, list[str]] = {}
    for c in cores:
        groups.setdefault(find(c), []).append(c)
    inflow = ext_all.groupby("dest")["flow"].sum()
    out = {}
    for members in groups.values():
        head = max(members, key=lambda m: inflow.get(m, 0))
        out.update({m: head for m in members})
    return out


def delimit(
    od: pd.DataFrame,
    core_quantile: float,
    merge_thr: float,
    attach_thr: float,
    min_job_ratio: float = 1.0,
    max_iter: int = 50,
) -> pd.DataFrame:
    """Run both rules. Returns ``unit, area, is_core``; ``area`` is NaN for never-attached units."""
    cores = find_cores(unit_stats(od), core_quantile, min_job_ratio)
    assign = merge_cores(od, cores, merge_thr) if cores else {}
    ext = od[od.origin != od.dest]
    out_ext = ext.groupby("origin")["flow"].sum()

    for _ in range(max_iter):
        e = ext.assign(area=ext["dest"].map(assign)).dropna(subset=["area"])
        e = e[~e.origin.isin(assign)]
        if e.empty:
            break
        share = e.groupby(["origin", "area"])["flow"].sum().div(out_ext, level="origin").reset_index(name="share")
        best = share.sort_values("share", ascending=False).drop_duplicates("origin")
        joined = best[best.share >= attach_thr]
        if joined.empty:
            break
        assign.update(dict(zip(joined.origin, joined.area)))

    units = sorted(set(od.origin) | set(od.dest))
    core_set = set(cores)
    return pd.DataFrame(
        {"unit": units, "area": [assign.get(u) for u in units], "is_core": [u in core_set for u in units]}
    )


def area_summary(od: pd.DataFrame, assignment: pd.DataFrame) -> pd.DataFrame:
    """Units, departures, internal flow and supply-side self-containment of every area."""
    m = dict(zip(assignment.unit, assignment.area))
    d = od.assign(o_area=od.origin.map(m), d_area=od.dest.map(m)).dropna(subset=["o_area"])
    out = pd.DataFrame(
        {
            "units": assignment.dropna(subset=["area"]).groupby("area").size(),
            "departures": d.groupby("o_area")["flow"].sum(),
            "internal": d[d.o_area == d.d_area].groupby("o_area")["flow"].sum(),
        }
    ).fillna(0.0)
    out["self_containment"] = out.internal / out.departures
    return out.sort_values("departures", ascending=False)
