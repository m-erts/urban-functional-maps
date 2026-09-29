"""Null model for Trap 2: same units, same area sizes, random assignment."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .selfcontainment import partition_sc


def shuffle_labels(labels: pd.Series, rng: np.random.Generator) -> pd.Series:
    """Permute unit→area labels. Preserves the number of units per area exactly."""
    return pd.Series(rng.permutation(labels.to_numpy()), index=labels.index)


def shuffle_sc(od: pd.DataFrame, labels: pd.Series, runs: int = 60, seed: int = 0) -> dict:
    """Observed vs random partition self-containment.

    Returns observed, random mean/sd, excess and all run values (report sd on slides!).
    """
    rng = np.random.default_rng(seed)
    obs = partition_sc(od, labels)
    vals = np.array([partition_sc(od, shuffle_labels(labels, rng)) for _ in range(runs)])
    return {"observed": obs, "random_mean": float(vals.mean()), "random_sd": float(vals.std(ddof=1)),
            "excess": obs - float(vals.mean()), "ratio": float(vals.mean()) / obs, "runs": vals}
