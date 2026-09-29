"""Regression targets = every number shown on stage (tests/golden_values.yaml).

Each value is skipped until its producing pipeline exists and outputs/tables/golden_actual.yaml
contains it (written by `make analysis`). Differences must be reported, never tuned away.
"""
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = yaml.safe_load((ROOT / "tests" / "golden_values.yaml").read_text())
ACTUAL_PATH = ROOT / "outputs" / "tables" / "golden_actual.yaml"
ACTUAL = yaml.safe_load(ACTUAL_PATH.read_text()) if ACTUAL_PATH.exists() else {}


@pytest.mark.parametrize("g", GOLDEN, ids=[g["id"] for g in GOLDEN])
def test_golden(g):
    if g["id"] not in ACTUAL:
        pytest.skip("not reproduced yet")
    assert ACTUAL[g["id"]] == pytest.approx(g["value"], abs=g["tol"]), g.get("note", "")
