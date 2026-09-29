"""Self-containment measures on an origin→destination table.

OD convention everywhere: DataFrame with columns ``origin``, ``dest``, ``flow``
(residence unit → workplace unit). Special place-of-work categories must be removed
BEFORE calling these functions (see sources.uk_census.clean_od).
"""
from __future__ import annotations

import pandas as pd


def unit_diagonal_share(od: pd.DataFrame) -> float:
    """Share of all flows that stay in the same unit (Trap 1: 0.103 / 0.506 / 0.093)."""
    total = od["flow"].sum()
    return float(od.loc[od["origin"] == od["dest"], "flow"].sum() / total) if total else float("nan")


def _with_areas(od: pd.DataFrame, labels: pd.Series) -> pd.DataFrame:
    out = od.copy()
    out["a_o"] = out["origin"].map(labels)
    out["a_d"] = out["dest"].map(labels)
    if out[["a_o", "a_d"]].isna().any().any():
        raise ValueError("units in OD without an area label")
    return out


def partition_sc(od: pd.DataFrame, labels: pd.Series) -> float:
    """Flow-weighted self-containment of a partition: trips staying inside their area / all trips.

    ``labels``: Series index = unit id, value = area id.
    """
    d = _with_areas(od, labels)
    return float(d.loc[d["a_o"] == d["a_d"], "flow"].sum() / d["flow"].sum())


def two_sided_sc(od: pd.DataFrame, labels: pd.Series) -> pd.DataFrame:
    """Per-area supply-side, demand-side and two-sided (min) self-containment + worker counts.

    supply  = residents of a working in a / employed residents of a
    demand  = jobs in a filled by residents of a / jobs in a
    """
    d = _with_areas(od, labels)
    internal = d[d["a_o"] == d["a_d"]].groupby("a_o")["flow"].sum()
    residents = d.groupby("a_o")["flow"].sum()
    jobs = d.groupby("a_d")["flow"].sum()
    res = pd.DataFrame({"internal": internal, "residents": residents, "jobs": jobs}).fillna(0)
    res["sc_supply"] = res["internal"] / res["residents"]
    res["sc_demand"] = res["internal"] / res["jobs"]
    res["sc_two_sided"] = res[["sc_supply", "sc_demand"]].min(axis=1)
    res["workers"] = res[["residents", "jobs"]].max(axis=1)  # TODO confirm which size ONS uses
    res.index.name = "area"
    return res
