"""Self-containment measures on an origin-destination table.

Special place-of-work categories must be removed BEFORE calling these functions
(see ``omfm.sources.uk_census``): a person coded at their residence sits on the diagonal
and inflates every measure defined here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["unit_diagonal_share", "partition_sc", "two_sided_sc", "band_self_containment"]


def unit_diagonal_share(od: pd.DataFrame) -> float:
    """Share of all flows that start and end in the same unit."""
    total = od["flow"].sum()
    return float(od.loc[od["origin"] == od["dest"], "flow"].sum() / total) if total else float("nan")


def _with_areas(od: pd.DataFrame, labels: pd.Series, require_all: bool) -> pd.DataFrame:
    out = od.assign(a_o=od["origin"].map(labels), a_d=od["dest"].map(labels))
    if require_all and out[["a_o", "a_d"]].isna().any().any():
        raise ValueError("units in OD without an area label")
    return out


def partition_sc(od: pd.DataFrame, labels: pd.Series, require_all: bool = False) -> float:
    """Flow-weighted self-containment of a partition.

    Numerator: flows whose origin and destination carry the same area label.
    Denominator: all flows leaving labelled origins (flows to unlabelled destinations count as
    leakage). ``labels``: index = unit id, value = area id.
    """
    d = _with_areas(od, labels, require_all).dropna(subset=["a_o"])
    return float(d.loc[d["a_o"] == d["a_d"], "flow"].sum() / d["flow"].sum())


def two_sided_sc(od: pd.DataFrame, labels: pd.Series) -> pd.DataFrame:
    """Per-area supply-side, demand-side and two-sided self-containment.

    supply = residents of a working in a / employed residents of a
    demand = jobs in a filled by residents of a / jobs in a
    two-sided = min(supply, demand), the quantity the TTWA validity rule constrains.
    Only flows with both ends labelled enter the counts.
    """
    d = _with_areas(od, labels, require_all=False).dropna(subset=["a_o", "a_d"])
    res = pd.DataFrame(
        {
            "internal": d[d["a_o"] == d["a_d"]].groupby("a_o")["flow"].sum(),
            "residents": d.groupby("a_o")["flow"].sum(),
            "jobs": d.groupby("a_d")["flow"].sum(),
        }
    ).fillna(0.0)
    res["sc_supply"] = (res["internal"] / res["residents"]).where(res["residents"] > 0, 0.0)
    res["sc_demand"] = (res["internal"] / res["jobs"]).where(res["jobs"] > 0, 0.0)
    res["sc_two_sided"] = res[["sc_supply", "sc_demand"]].min(axis=1)
    res.index.name = "area"
    return res


def band_self_containment(total, same_unit) -> np.ndarray:
    """Self-containment where only nested destination bands are published (Serbia, MLIT).

    ``same_unit / total``; NaN where ``total`` is zero. The denominator is whatever population
    the publisher counted (daily migrants in Serbia, presence in Japan), so values are not
    comparable with pair-based self-containment.
    """
    total = np.asarray(total, dtype=float)
    same = np.asarray(same_unit, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(total > 0, same / total, np.nan)
