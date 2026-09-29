import numpy as np
import pandas as pd
import pytest

from omfm.analysis import nullmodel, osm, selfcontainment as sc, signatures, ttwa


@pytest.fixture
def od():
    # 4 units, two obvious basins {A,B} and {C,D}
    rows = [("A", "A", 10), ("A", "B", 30), ("B", "B", 20), ("B", "A", 10), ("A", "C", 2),
            ("C", "C", 10), ("C", "D", 30), ("D", "D", 20), ("D", "C", 10), ("D", "B", 2)]
    return pd.DataFrame(rows, columns=["origin", "dest", "flow"])


def test_diagonal(od):
    assert sc.unit_diagonal_share(od) == pytest.approx(60 / 144)


def test_partition_and_two_sided(od):
    lab = pd.Series({"A": 1, "B": 1, "C": 2, "D": 2})
    assert sc.partition_sc(od, lab) == pytest.approx(140 / 144)
    t = sc.two_sided_sc(od, lab)
    assert (t["sc_two_sided"] <= t[["sc_supply", "sc_demand"]].max(axis=1)).all()


def test_null_model_preserves_sizes(od):
    lab = pd.Series({"A": 1, "B": 1, "C": 2, "D": 2})
    rng = np.random.default_rng(1)
    assert nullmodel.shuffle_labels(lab, rng).value_counts().sort_index().tolist() == [2, 2]
    r = nullmodel.shuffle_sc(od, lab, runs=20, seed=1)
    assert r["observed"] >= r["random_mean"]


def test_ttwa_threshold():
    thr = ttwa.sc_threshold([1000, 3500, 25000, 100000])
    assert np.isnan(thr[0]) and thr[1] == pytest.approx(0.75) and thr[2] == pytest.approx(0.667) and thr[3] == pytest.approx(0.667)


def test_signatures():
    x = np.log2([2, 0.5, 1, 1])
    y = np.log2([1, 1, 2, 1])
    assert list(signatures.classify(x, y)) == ["office", "residential", "leisure", "mixed"]


def test_hopkins_uniform_is_about_half():
    X = np.random.default_rng(12345).uniform(size=(2000, 2))  # data seed must differ from hopkins seed
    assert 0.35 < signatures.hopkins(X) < 0.65


def test_osm_helpers():
    pts = pd.DataFrame({"time": ["2014-05-01T10:00:10Z", "2014-05-01T10:00:50Z", "2019-01-01T00:00:00Z", None]})
    assert osm.unique_minutes(pts) == 2
    assert osm.top_cell_share(pd.Series(["a", "a", "b"])) == pytest.approx(2 / 3)
