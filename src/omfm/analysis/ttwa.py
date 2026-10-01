"""Travel-to-work-area validity rule and two ways of enforcing it.

Published criterion (Coombes & Bond 2008; ONS 2015): an area is valid if it has at least
3,500 employed residents and its two-sided self-containment reaches a threshold that falls
linearly from 75 % at 3,500 to 66.7 % at 25,000 and stays at 66.7 % above.

The criterion says when an area is acceptable. It does not say how to repair one that is not;
that is the job of the placement algorithm, and the two repairs below give different maps.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .selfcontainment import two_sided_sc

__all__ = ["sc_threshold", "is_valid", "enforce_greedy_merge", "enforce_by_dissolution"]

MIN_SIZE, BIG_SIZE = 3_500, 25_000
SC_SMALL, SC_BIG = 0.75, 2.0 / 3.0


def sc_threshold(size, min_size=MIN_SIZE, big_size=BIG_SIZE, sc_small=SC_SMALL, sc_big=SC_BIG):
    """Required two-sided self-containment as a function of area size; NaN below ``min_size``."""
    size = np.asarray(size, dtype=float)
    t = np.clip((size - min_size) / (big_size - min_size), 0.0, 1.0)
    return np.where(size < min_size, np.nan, sc_small + t * (sc_big - sc_small))


def is_valid(stats: pd.DataFrame) -> pd.Series:
    """Validity of each row of a `two_sided_sc` table (size = employed residents)."""
    thr = sc_threshold(stats["residents"])
    return (stats["residents"] >= MIN_SIZE) & (stats["sc_two_sided"] >= np.nan_to_num(thr, nan=np.inf))


def _deficit(size: np.ndarray, sc: np.ndarray, bad: np.ndarray) -> np.ndarray:
    """Ordering key: undersized areas first (key > 1), then by self-containment shortfall."""
    thr = SC_SMALL + np.clip((size - MIN_SIZE) / (BIG_SIZE - MIN_SIZE), 0, 1) * (SC_BIG - SC_SMALL)
    d = np.where(bad, thr - sc, -np.inf)
    return np.where(bad & (size < MIN_SIZE), 1.0 + (MIN_SIZE - size) / MIN_SIZE, d)


def enforce_greedy_merge(od: pd.DataFrame, assign: dict, max_iter: int = 10_000) -> dict:
    """Merge the least valid area, whole, into the area it exchanges most flow with; repeat.

    Works on the area x area matrix, updated by adding one row and one column per merge.
    """
    names = sorted(set(assign.values()))
    idx = {n: i for i, n in enumerate(names)}
    k = len(names)
    o = od.origin.map(assign).map(idx).to_numpy(dtype=float)
    d = od.dest.map(assign).map(idx).to_numpy(dtype=float)
    ok = ~(np.isnan(o) | np.isnan(d))
    M = np.zeros((k, k))
    np.add.at(M, (o[ok].astype(int), d[ok].astype(int)), od.flow.to_numpy(dtype=float)[ok])

    alive = np.ones(k, dtype=bool)
    target = np.arange(k)
    for _ in range(max_iter):
        res, job, ins = M.sum(axis=1), M.sum(axis=0), np.diag(M)
        with np.errstate(divide="ignore", invalid="ignore"):
            sc = np.minimum(np.where(res > 0, ins / res, 0.0), np.where(job > 0, ins / job, 0.0))
        thr = SC_SMALL + np.clip((res - MIN_SIZE) / (BIG_SIZE - MIN_SIZE), 0, 1) * (SC_BIG - SC_SMALL)
        bad = alive & ((res < MIN_SIZE) | (sc < thr))
        if not bad.any():
            break
        worst = int(np.argmax(_deficit(res, sc, bad)))
        link = M[worst] + M[:, worst]
        link[worst] = -np.inf
        link[~alive] = -np.inf
        if not np.isfinite(link).any() or link.max() <= 0:
            alive[worst] = False  # isolated: withdraw from the check, keep as is
            continue
        tgt = int(np.argmax(link))
        M[tgt, :] += M[worst, :]
        M[:, tgt] += M[:, worst]
        M[worst, :] = 0.0
        M[:, worst] = 0.0
        alive[worst] = False
        target[target == worst] = tgt
    return {u: names[target[idx[a]]] for u, a in assign.items()}


def enforce_by_dissolution(od: pd.DataFrame, assign: dict, max_iter: int = 2_000) -> dict:
    """Dissolve the least valid area and hand its units, one by one, to the valid area each
    exchanges most flow with. Closer in spirit to Coombes-Bond than the greedy merge."""
    assign = dict(assign)
    for _ in range(max_iter):
        st = two_sided_sc(od, pd.Series(assign))
        valid = is_valid(st)
        bad = st[~valid]
        if bad.empty:
            break
        key = _deficit(bad["residents"].to_numpy(), bad["sc_two_sided"].to_numpy(), np.ones(len(bad), dtype=bool))
        worst = bad.index[int(np.argmax(key))]
        members = [u for u, a in assign.items() if a == worst]
        targets = set(st.index[valid]) - {worst}
        if not targets:
            break
        ms = set(members)
        d = od[(od.origin.isin(ms)) | (od.dest.isin(ms))]
        d = d.assign(oa=d.origin.map(assign), da=d.dest.map(assign))
        out = d[d.origin.isin(ms)].groupby(["origin", "da"]).flow.sum().rename_axis(["unit", "area"])
        inn = d[d.dest.isin(ms)].groupby(["dest", "oa"]).flow.sum().rename_axis(["unit", "area"])
        link = out.add(inn, fill_value=0.0).reset_index()
        link = link[link.area.isin(targets)]
        if link.empty:
            break
        best = link.sort_values("flow", ascending=False).drop_duplicates("unit")
        moved = dict(zip(best.unit, best.area))
        if not moved:
            break
        assign.update(moved)
        if all(assign[u] == worst for u in members):
            break
    return assign
