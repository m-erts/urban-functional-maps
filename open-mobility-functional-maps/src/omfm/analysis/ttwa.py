"""ONS TTWA validity rule (Trap 3).

Sliding scale from the v1 deck: 3,500 workers @ 75 % → 25,000 @ 66.7 % two-sided self-containment.
TODO(verify): the exact trade-off form in Coombes & Bond (2008) / ONS 2011 TTWA documentation.
"""
from __future__ import annotations

import numpy as np


def sc_threshold(workers, min_workers=3500, sc_at_min=0.75, max_workers=25000, sc_at_max=0.667):
    """Required two-sided self-containment for an area of ``workers`` size (NaN below min size)."""
    w = np.asarray(workers, dtype=float)
    t = sc_at_min + (np.clip(w, min_workers, max_workers) - min_workers) * (sc_at_max - sc_at_min) / (max_workers - min_workers)
    return np.where(w < min_workers, np.nan, t)


def is_valid(workers, sc_two_sided, **kw):
    thr = sc_threshold(workers, **kw)
    return np.where(np.isnan(thr), False, np.asarray(sc_two_sided) >= thr)


def enforce_rule_naive(od, labels, adjacency, **kw):
    """Merge least-valid area into the adjacent area with the strongest flow link until all valid.

    v1 result: 67 areas, London 6.1 M workers. TODO implement (see docs/03_METHODOLOGY.md §2.5).
    """
    raise NotImplementedError
