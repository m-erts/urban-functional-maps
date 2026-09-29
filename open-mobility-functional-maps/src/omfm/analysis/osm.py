"""OSM trace sample diagnostics (slide 3). Input: DataFrame lat, lon, time (UTC, may be NaT)."""
from __future__ import annotations

import pandas as pd


def unique_minutes(pts: pd.DataFrame) -> int:
    """Effective sample size: distinct timestamps truncated to the minute (untimed points excluded)."""
    return int(pd.to_datetime(pts["time"], utc=True).dropna().dt.floor("min").nunique())


def median_year(pts: pd.DataFrame) -> float:
    return float(pd.to_datetime(pts["time"], utc=True).dropna().dt.year.median())


def top_cell_share(cells: pd.Series) -> float:
    """Share of points in the single most populated H3 cell."""
    vc = cells.value_counts()
    return float(vc.iloc[0] / vc.sum())


def spearman_vs_places(trace_counts: pd.Series, place_counts: pd.Series, shared_only=True) -> float:
    df = pd.concat({"t": trace_counts, "p": place_counts}, axis=1).fillna(0)
    if shared_only:
        df = df[(df.t > 0) & (df.p > 0)]
    return float(df["t"].corr(df["p"], method="spearman"))
