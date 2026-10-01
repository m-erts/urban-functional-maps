"""Entropy and Hill numbers of a categorical distribution (functions per cell, classes per city).

Richness grows with sample size, so it measures how much data a cell has. Hill numbers of
order 1 and 2 are effective numbers of categories and are far less sensitive to sample size
(Hill 1973; Jost 2006; Chao & Jost 2012).
"""

from __future__ import annotations

import numpy as np

__all__ = ["shares", "shannon", "hill", "evenness", "sample_coverage", "profile"]


def shares(counts) -> np.ndarray:
    c = np.asarray(counts, dtype=float)
    c = c[c > 0]
    return c / c.sum() if c.size else c


def shannon(counts) -> float:
    """Shannon entropy H = -sum p ln p, in nats."""
    p = shares(counts)
    return float(-(p * np.log(p)).sum()) if p.size else 0.0


def hill(counts, q: float) -> float:
    """Hill number of order q: q=0 richness, q=1 exp(H), q=2 inverse Simpson."""
    p = shares(counts)
    if not p.size:
        return 0.0
    if q == 1:
        return float(np.exp(shannon(counts)))
    return float((p**q).sum() ** (1.0 / (1.0 - q)))


def evenness(counts) -> float:
    """Pielou evenness H / ln(richness); 1.0 for a single category by convention."""
    p = shares(counts)
    return 1.0 if p.size <= 1 else shannon(counts) / float(np.log(p.size))


def sample_coverage(counts) -> float:
    """Chao-Jost estimate of the share of the distribution represented by observed categories."""
    c = np.asarray(counts, dtype=float)
    c = c[c > 0]
    n = c.sum()
    if n <= 1:
        return 0.0
    f1, f2 = float((c == 1).sum()), float((c == 2).sum())
    if f1 == 0:
        return 1.0
    a = (n - 1) * f1 / ((n - 1) * f1 + 2 * f2) if f2 > 0 else (n - 1) * (f1 - 1) / ((n - 1) * (f1 - 1) + 2)
    return float(1.0 - f1 / n * a)


def profile(counts) -> dict:
    """All measures for one distribution."""
    p = shares(counts)
    return {
        "n": float(np.sum(counts)),
        "richness": int(p.size),
        "shannon": shannon(counts),
        "hill_q1": hill(counts, 1),
        "hill_q2": hill(counts, 2),
        "evenness": evenness(counts),
        "top_share": float(p.max()) if p.size else 0.0,
        "coverage": sample_coverage(counts),
    }
