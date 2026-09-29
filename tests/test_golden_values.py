"""Regression: a run of the pipeline must reproduce the frozen snapshot.

``tests/golden_values.yaml`` is the snapshot (``python scripts/run.py register --freeze``);
``outputs/tables/golden_actual.yaml`` is what the last run wrote. A difference is reported,
never tuned away.
"""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = yaml.safe_load((ROOT / "tests" / "golden_values.yaml").read_text(encoding="utf-8"))
ACTUAL_PATH = ROOT / "outputs" / "tables" / "golden_actual.yaml"
ACTUAL = yaml.safe_load(ACTUAL_PATH.read_text(encoding="utf-8")) if ACTUAL_PATH.exists() else {}


@pytest.mark.parametrize("g", GOLDEN, ids=[g["id"] for g in GOLDEN])
def test_golden(g):
    if g["id"] not in ACTUAL:
        pytest.skip("not produced by the last run")
    if isinstance(g["value"], (str, bool)):
        assert ACTUAL[g["id"]] == g["value"]
    else:
        assert ACTUAL[g["id"]] == pytest.approx(g["value"], abs=g["tol"])


def test_stage_register_is_complete():
    stage = yaml.safe_load((ROOT / "tests" / "stage_values.yaml").read_text(encoding="utf-8"))
    missing = [r["key"] for r in stage if r["key"] not in ACTUAL]
    assert not missing, f"stage numbers without a pipeline value: {missing}"
