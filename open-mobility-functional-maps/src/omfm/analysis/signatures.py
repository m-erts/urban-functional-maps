"""Temporal signatures from MLIT presence (slide 13) + clusterability diagnostics."""
from __future__ import annotations

import numpy as np
import pandas as pd

CLASSES = ("office", "residential", "leisure", "mixed")


def axes(day_wd, night_wd, day_hol) -> pd.DataFrame:
    """x = log2(weekday day / weekday night), y = log2(holiday day / weekday day)."""
    return pd.DataFrame({"x": np.log2(np.asarray(day_wd) / np.asarray(night_wd)),
                         "y": np.log2(np.asarray(day_hol) / np.asarray(day_wd))})


def classify(x, y, ratio=1.5, precedence=("leisure", "office", "residential")) -> np.ndarray:
    """Declared thresholds on two named axes. ``precedence`` = which rule wins when several fire.

    TODO: confirm the precedence used for the v1 counts 155/102/50/115.
    """
    t = np.log2(ratio)
    x, y = np.asarray(x), np.asarray(y)
    rules = {"office": x >= t, "residential": x <= -t, "leisure": y >= t}
    out = np.full(x.shape, "mixed", dtype=object)
    for cls in reversed(precedence):  # last assignment = highest precedence
        out[rules[cls]] = cls
    return out


def hopkins(X, m=None, seed=0) -> float:
    """Hopkins statistic H ∈ [0,1]; ≈0.5 uniform/no structure, →1 clustered."""
    from sklearn.neighbors import NearestNeighbors

    X = np.asarray(X, dtype=float)
    n, d = X.shape
    m = m or max(1, int(0.1 * n))
    rng = np.random.default_rng(seed)
    nn = NearestNeighbors(n_neighbors=2).fit(X)
    idx = rng.choice(n, m, replace=False)
    w = nn.kneighbors(X[idx], 2)[0][:, 1]
    U = rng.uniform(X.min(0), X.max(0), size=(m, d))
    u = nn.kneighbors(U, 1)[0][:, 0]
    return float((u ** d).sum() / ((u ** d).sum() + (w ** d).sum()))
