"""Own functional-area heuristic (NOT the ONS algorithm). Spec: docs/03_METHODOLOGY.md §2.3.

Parameters (config/params.yaml → uk.delimitation): core_quantile_external_inflow=0.95,
core_merge_threshold=0.10, attach_threshold=0.15, iterative attachment, queen contiguity repair.
v1 targets: 235 areas, 26 non-contiguous, 3 islands after repair (tests/golden_values.yaml).
Open decisions marked [DECIDE] in the methodology must be resolved first (or taken from legacy code).
"""
from __future__ import annotations


def find_cores(od, quantile=0.95):
    raise NotImplementedError


def merge_cores(od, cores, threshold=0.10):
    raise NotImplementedError


def attach(od, cores, threshold=0.15, max_iter=100):
    raise NotImplementedError


def delimit(od, **params):
    """Return pd.Series unit→area."""
    raise NotImplementedError


def repair_contiguity(labels, polygons, od, contiguity="queen"):
    """Hand fragments not containing the core to the adjacent area with the strongest flow link."""
    raise NotImplementedError
