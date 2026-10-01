"""OSM public GPS traces: how large the sample really is and where it sits."""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = [
    "unique_minutes",
    "median_year",
    "h3_counts",
    "top_cell_share",
    "spearman_shared",
    "spearman_interval",
]


def _times(points: pd.DataFrame) -> pd.Series:
    return pd.to_datetime(points["time"], errors="coerce", utc=True).dropna()


def unique_minutes(points: pd.DataFrame) -> int:
    """Distinct timestamps truncated to the minute: the effective sample, not the point count."""
    return int(_times(points).dt.floor("min").nunique())


def median_year(points: pd.DataFrame) -> int:
    return int(_times(points).dt.year.median())


def h3_counts(lat, lon, resolution: int = 8) -> pd.Series:
    """Point counts per H3 cell."""
    import h3

    cells = [h3.latlng_to_cell(a, b, resolution) for a, b in zip(np.asarray(lat, float), np.asarray(lon, float))]
    return pd.Series(cells).value_counts()


def top_cell_share(cells: pd.Series) -> float:
    """Share of points in the single busiest cell; ``cells`` is one cell id per point."""
    vc = cells.value_counts()
    return float(vc.iloc[0] / vc.sum())


def spearman_shared(a: pd.Series, b: pd.Series) -> dict:
    """Spearman rank correlation on cells present in both series (both counts > 0)."""
    from scipy.stats import spearmanr

    j = pd.concat({"a": a, "b": b}, axis=1).dropna()
    j = j[(j.a > 0) & (j.b > 0)]
    if len(j) < 3:
        return {"rho": float("nan"), "p": float("nan"), "n": int(len(j))}
    r = spearmanr(j.a, j.b)
    return {"rho": float(r.statistic), "p": float(r.pvalue), "n": int(len(j))}


def spearman_interval(rho: float, n: int, z: float = 1.96) -> tuple[float, float]:
    """Approximate 95 % interval of a Spearman coefficient (Fisher transform, Fieller et al. 1957)."""
    if n < 5:
        return float("nan"), float("nan")
    centre, half = np.arctanh(rho), z * 1.03 / np.sqrt(n - 3)
    return float(np.tanh(centre - half)), float(np.tanh(centre + half))
