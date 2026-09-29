"""Temporal signatures from presence counts, and whether the data support clusters at all."""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["CLASSES", "axes", "classify", "hopkins", "hdbscan_sweep", "kmeans_silhouette"]

CLASSES = ("office", "residential", "leisure", "mixed")


def axes(day_wd, night_wd, day_hol) -> pd.DataFrame:
    """x = log2(weekday day / weekday night), y = log2(holiday day / weekday day)."""
    day_wd, night_wd, day_hol = (np.asarray(v, dtype=float) for v in (day_wd, night_wd, day_hol))
    return pd.DataFrame({"x": np.log2(day_wd / night_wd), "y": np.log2(day_hol / day_wd)})


def classify(x, y, ratio: float = 1.5, precedence=("leisure", "office", "residential")) -> np.ndarray:
    """Declared thresholds on two named axes; ``precedence`` decides when two rules fire."""
    t = np.log2(ratio)
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    rules = {"office": x >= t, "residential": x <= -t, "leisure": y >= t}
    out = np.full(x.shape, "mixed", dtype=object)
    for cls in reversed(precedence):
        out[rules[cls]] = cls
    return out


def hopkins(X, m: int | None = None, seed: int = 0) -> float:
    """Hopkins statistic: about 0.5 for uniform data, towards 1 for concentrated data.

    A high value rejects spatial uniformity. It does not establish more than one mode.
    """
    from sklearn.neighbors import NearestNeighbors

    X = np.asarray(X, dtype=float)
    n, d = X.shape
    m = m or max(1, int(0.1 * n))
    rng = np.random.default_rng(seed)
    nn = NearestNeighbors(n_neighbors=2).fit(X)
    w = nn.kneighbors(X[rng.choice(n, m, replace=False)], 2)[0][:, 1]
    u = nn.kneighbors(rng.uniform(X.min(0), X.max(0), size=(m, d)), 1)[0][:, 0]
    return float((u**d).sum() / ((u**d).sum() + (w**d).sum()))


def hdbscan_sweep(X, min_cluster_sizes, min_samples_list) -> pd.DataFrame:
    """Noise share and number of clusters over a grid of HDBSCAN settings."""
    from sklearn.cluster import HDBSCAN

    X = np.asarray(X, dtype=float)
    rows = []
    for mcs in min_cluster_sizes:
        for ms in min_samples_list:
            lab = HDBSCAN(min_cluster_size=int(mcs), min_samples=int(ms)).fit_predict(X)
            k = len(set(lab)) - (1 if -1 in lab else 0)
            sizes = np.bincount(lab[lab >= 0]) if k else np.array([])
            rows.append(
                {
                    "min_cluster_size": mcs,
                    "min_samples": ms,
                    "n_clusters": k,
                    "noise_share": float((lab == -1).mean()),
                    "largest_cluster_share": float(sizes.max() / len(lab)) if k else 0.0,
                }
            )
    return pd.DataFrame(rows)


def kmeans_silhouette(X, ks=(2, 3, 4, 5, 6), seed: int = 0) -> pd.DataFrame:
    """k-means always returns k classes; the silhouette says how separated they are."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    X = np.asarray(X, dtype=float)
    rows = []
    for k in ks:
        lab = KMeans(n_clusters=k, n_init=10, random_state=seed).fit_predict(X)
        rows.append({"k": k, "silhouette": float(silhouette_score(X, lab))})
    return pd.DataFrame(rows)
