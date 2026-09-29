"""Agreement between two partitions of the same units (candidate vs reference).

Everything derives from one object, the weighted contingency table

    C[a, b] = sum of w(u) over units u with candidate label a and reference label b

which is the spatial error matrix of the delimitation: rows are candidate areas, columns are
reference areas, off-diagonal mass is weight placed in the wrong area. ``w`` is employed
residents by default, so errors are counted in people, not in polygons.

From C:
    IoU(a, b)        = C[a,b] / (C[a,.] + C[.,b] - C[a,b])
    omission(b)      = 1 - C[a*,b] / C[.,b]     share of reference area b missed by its match a*
    commission(b)    = 1 - C[a*,b] / C[a*,.]    share of the match lying outside b
    adjusted Rand    = pair-counting agreement corrected for chance (Hubert & Arabie 1985)
    V-measure        = harmonic mean of homogeneity and completeness (Rosenberg & Hirschberg 2007)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["contingency", "iou_matrix", "match_report", "adjusted_rand", "v_measure", "summary", "polygon_iou"]


def contingency(candidate: pd.Series, reference: pd.Series, weights: pd.Series | None = None) -> pd.DataFrame:
    """Weighted contingency table over units labelled in both partitions."""
    df = pd.concat({"a": candidate, "b": reference}, axis=1).dropna()
    df["w"] = 1.0 if weights is None else weights.reindex(df.index).fillna(0.0)
    return df.pivot_table(index="a", columns="b", values="w", aggfunc="sum", fill_value=0.0)


def iou_matrix(c: pd.DataFrame) -> pd.DataFrame:
    """Intersection over union for every candidate x reference pair."""
    m = c.to_numpy(dtype=float)
    union = m.sum(axis=1, keepdims=True) + m.sum(axis=0, keepdims=True) - m
    with np.errstate(divide="ignore", invalid="ignore"):
        return pd.DataFrame(np.where(union > 0, m / union, 0.0), index=c.index, columns=c.columns)


def match_report(c: pd.DataFrame) -> pd.DataFrame:
    """For every reference area: best-IoU candidate, IoU, omission and commission error."""
    iou = iou_matrix(c)
    m = c.to_numpy(dtype=float)
    best = iou.to_numpy().argmax(axis=0)
    cols = np.arange(m.shape[1])
    inter = m[best, cols]
    ref_w, cand_w = m.sum(axis=0), m.sum(axis=1)[best]
    return pd.DataFrame(
        {
            "match": c.index[best],
            "weight": ref_w,
            "iou": iou.to_numpy()[best, cols],
            "omission": 1 - inter / ref_w,
            "commission": 1 - inter / cand_w,
            "n_candidates": (m > 0).sum(axis=0),
        },
        index=c.columns,
    ).rename_axis("reference")


def _comb2(x):
    x = np.asarray(x, dtype=float)
    return x * (x - 1.0) / 2.0


def adjusted_rand(c: pd.DataFrame) -> float:
    """Adjusted Rand index from a contingency table (weights act as counts)."""
    m = c.to_numpy(dtype=float)
    sum_ij = _comb2(m).sum()
    sum_a, sum_b = _comb2(m.sum(axis=1)).sum(), _comb2(m.sum(axis=0)).sum()
    expected = sum_a * sum_b / _comb2(m.sum())
    max_index = 0.5 * (sum_a + sum_b)
    return float((sum_ij - expected) / (max_index - expected)) if max_index != expected else 1.0


def _entropy(p: np.ndarray) -> float:
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def v_measure(c: pd.DataFrame) -> dict:
    """Homogeneity, completeness and V-measure, reference = columns."""
    m = c.to_numpy(dtype=float)
    n = m.sum()
    h_ref, h_cand = _entropy(m.sum(axis=0) / n), _entropy(m.sum(axis=1) / n)
    h_joint = _entropy((m / n).ravel())
    hom = 1.0 if h_ref == 0 else 1.0 - (h_joint - h_cand) / h_ref
    com = 1.0 if h_cand == 0 else 1.0 - (h_joint - h_ref) / h_cand
    v = 0.0 if hom + com == 0 else 2 * hom * com / (hom + com)
    return {"homogeneity": hom, "completeness": com, "v_measure": v}


def summary(candidate: pd.Series, reference: pd.Series, weights: pd.Series | None = None) -> dict:
    """One-row agreement summary, weighted and unweighted."""
    c = contingency(candidate, reference, weights)
    rep = match_report(c)
    cu = contingency(candidate, reference)
    out = {
        "n_candidate": int(c.shape[0]),
        "n_reference": int(c.shape[1]),
        "units_compared": int(cu.to_numpy().sum()),
        "ari_weighted": adjusted_rand(c),
        "ari_units": adjusted_rand(cu),
        "mean_iou_weighted": float(np.average(rep.iou, weights=rep.weight)),
        "median_iou": float(rep.iou.median()),
        "share_ref_iou_ge_0.5": float((rep.iou >= 0.5).mean()),
        "weight_in_matched_area": float((c.to_numpy().max(axis=0)).sum() / c.to_numpy().sum()),
    }
    out.update(v_measure(c))
    return out


def polygon_iou(cand, ref, cand_col: str, ref_col: str) -> pd.DataFrame:
    """Area-based IoU between two dissolved polygon layers in the same projected CRS.

    Returns the best candidate per reference polygon. Use next to the weighted IoU: a sparsely
    populated upland can dominate area IoU and vanish from the weighted one.
    """
    import geopandas as gpd

    a = cand[[cand_col, "geometry"]].dissolve(cand_col).reset_index()
    b = ref[[ref_col, "geometry"]].dissolve(ref_col).reset_index()
    a["area_a"], b["area_b"] = a.area, b.area
    x = gpd.overlay(a, b, how="intersection", keep_geom_type=True)
    x["inter"] = x.area
    x["iou"] = x.inter / (x.area_a + x.area_b - x.inter)
    best = x.sort_values("iou", ascending=False).drop_duplicates(ref_col)
    return best[[ref_col, cand_col, "iou", "inter", "area_a", "area_b"]].set_index(ref_col)
