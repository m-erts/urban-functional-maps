"""Unit tests of the analysis functions. No data files needed."""

import numpy as np
import pandas as pd
import pytest

from omfm.analysis import agreement as A
from omfm.analysis import contiguity as C
from omfm.analysis import delimitation as D
from omfm.analysis import diversity as V
from omfm.analysis import nullmodel as N
from omfm.analysis import osm, signatures, ttwa
from omfm.analysis import selfcontainment as sc


@pytest.fixture
def od():
    # four units, two obvious basins {A, B} and {C, D}
    rows = [
        ("A", "A", 10),
        ("A", "B", 30),
        ("B", "B", 20),
        ("B", "A", 10),
        ("A", "C", 2),
        ("C", "C", 10),
        ("C", "D", 30),
        ("D", "D", 20),
        ("D", "C", 10),
        ("D", "B", 2),
    ]
    return pd.DataFrame(rows, columns=["origin", "dest", "flow"])


@pytest.fixture
def labels():
    return pd.Series({"A": 1, "B": 1, "C": 2, "D": 2})


def test_diagonal(od):
    assert sc.unit_diagonal_share(od) == pytest.approx(60 / 144)


def test_partition_and_two_sided(od, labels):
    assert sc.partition_sc(od, labels) == pytest.approx(140 / 144)
    t = sc.two_sided_sc(od, labels)
    assert (t.sc_two_sided == t[["sc_supply", "sc_demand"]].min(axis=1)).all()
    assert t.loc[1, "sc_supply"] == pytest.approx(70 / 72)
    assert t.loc[1, "sc_demand"] == pytest.approx(70 / 72)


def test_a_person_coded_at_home_inflates_the_diagonal(od):
    home = pd.concat([od, pd.DataFrame([("A", "A", 100)], columns=od.columns)])
    home = D.prepare_od(home, "origin", "dest", "flow")
    assert sc.unit_diagonal_share(home) == pytest.approx(160 / 244)
    assert sc.unit_diagonal_share(home) > 1.5 * sc.unit_diagonal_share(od)


def test_null_model_preserves_sizes(labels):
    rng = np.random.default_rng(1)
    assert sorted(N.shuffle_labels(labels, rng).value_counts()) == [2, 2]


def test_null_closed_form_matches_permutations():
    rng = np.random.default_rng(3)
    units = [f"u{i:03d}" for i in range(60)]
    m = pd.DataFrame(
        [(a, b, rng.integers(1, 50)) for a in units for b in rng.choice(units, 12, replace=False)],
        columns=["origin", "dest", "flow"],
    )
    m = D.prepare_od(m, "origin", "dest", "flow")
    lab = pd.Series(rng.choice([1, 2, 3, 4], size=60, p=[0.5, 0.25, 0.15, 0.10]), index=units)
    r = N.shuffle_sc(m, lab, runs=4000, seed=0)
    e = N.expected_sc(m, lab)
    assert r["null_mean"] == pytest.approx(e["expected"], abs=3 * r["null_sd"] / np.sqrt(4000) + 1e-3)
    assert e["expected"] == pytest.approx(e["diagonal_share"] + (1 - e["diagonal_share"]) * e["h"])


def test_effective_areas():
    assert N.effective_areas(pd.Series([1] * 5 + [2] * 5)) == pytest.approx(2.0)
    assert N.effective_areas(pd.Series([1] * 9 + [2] * 1)) == pytest.approx(1 / (0.81 + 0.01))


def test_ttwa_threshold():
    thr = ttwa.sc_threshold([1000, 3500, 14250, 25000, 100000])
    assert np.isnan(thr[0])
    assert thr[1] == pytest.approx(0.75)
    assert thr[2] == pytest.approx((0.75 + 2 / 3) / 2)
    assert thr[3] == pytest.approx(2 / 3) and thr[4] == pytest.approx(2 / 3)


def test_greedy_merge_keeps_every_unit_and_all_flow(od):
    assign = {u: u for u in "ABCD"}  # four areas of one unit, all far too small
    out = ttwa.enforce_greedy_merge(od, assign)
    assert set(out) == set(assign)
    assert sc.two_sided_sc(od, pd.Series(out)).residents.sum() == pytest.approx(od.flow.sum())
    assert len(set(out.values())) < 4


def test_delimit_finds_two_basins():
    rows = []
    for core, subs in (("X", ["x1", "x2", "x3"]), ("Y", ["y1", "y2", "y3"])):
        rows.append((core, core, 50))
        for s_ in subs:
            rows += [(s_, core, 40), (s_, s_, 10), (core, s_, 3)]
    rows += [("x1", "Y", 2), ("y1", "X", 2)]
    m = D.prepare_od(pd.DataFrame(rows, columns=["o", "d", "w"]), "o", "d", "w")
    asg = D.delimit(m, core_quantile=0.75, merge_thr=0.5, attach_thr=0.15)
    lab = asg.set_index("unit").area
    assert set(asg[asg.is_core].unit) == {"X", "Y"}
    assert lab.nunique() == 2
    assert (lab[["x1", "x2", "x3"]] == "X").all() and (lab[["y1", "y2", "y3"]] == "Y").all()


def test_contiguity_repair_moves_fragment_and_keeps_island(od):
    # chain A - B - C, D is an island; D and C are labelled with A's area without touching it
    adj = {"A": {"B"}, "B": {"A", "C"}, "C": {"B"}, "D": set()}
    assign = {"A": "a", "B": "b", "C": "a", "D": "a"}
    rep = C.fragmentation_report(assign, adj)
    assert rep.set_index("area").loc["a", "n_components"] == 3
    fixed = C.repair(od, assign, adj, cores={"A"})
    assert fixed["C"] == "b"  # handed to the adjacent area
    assert fixed["D"] == "a"  # nothing adjacent: stays, reported as island


def test_agreement_identity_and_split(labels):
    w = pd.Series({"A": 10.0, "B": 30.0, "C": 20.0, "D": 40.0})
    s = A.summary(labels, labels, w)
    assert s["ari_weighted"] == pytest.approx(1.0)
    assert s["mean_iou_weighted"] == pytest.approx(1.0)
    assert s["v_measure"] == pytest.approx(1.0)
    split = pd.Series({"A": 1, "B": 9, "C": 2, "D": 2})  # reference area 1 cut in two
    c = A.contingency(split, labels, w)
    rep = A.match_report(c)
    assert rep.loc[1, "iou"] == pytest.approx(30 / 40)  # best match is B alone
    assert rep.loc[1, "omission"] == pytest.approx(10 / 40)
    assert rep.loc[1, "commission"] == pytest.approx(0.0)
    assert A.adjusted_rand(c) < 1.0


def test_ari_matches_sklearn_on_unit_counts():
    from sklearn.metrics import adjusted_rand_score

    rng = np.random.default_rng(0)
    a, b = pd.Series(rng.integers(0, 5, 300)), pd.Series(rng.integers(0, 4, 300))
    assert A.adjusted_rand(A.contingency(a, b)) == pytest.approx(adjusted_rand_score(b, a))


def test_signatures_and_precedence():
    x = np.log2([2, 0.5, 1, 1, 2])
    y = np.log2([1, 1, 2, 1, 2])
    assert list(signatures.classify(x, y)) == ["office", "residential", "leisure", "mixed", "leisure"]
    first = signatures.classify(x, y, precedence=("office", "leisure", "residential"))
    assert first[-1] == "office"


def test_hopkins_uniform_is_about_half():
    X = np.random.default_rng(12345).uniform(size=(2000, 2))
    assert 0.40 < signatures.hopkins(X, seed=1) < 0.60


def test_diversity():
    assert V.hill([5, 5, 5, 5], 1) == pytest.approx(4.0)
    assert V.hill([5, 5, 5, 5], 2) == pytest.approx(4.0)
    assert V.hill([97, 1, 1, 1], 0) == pytest.approx(4.0)
    assert V.hill([97, 1, 1, 1], 2) < 1.1
    assert V.shannon([1]) == 0.0
    assert V.evenness([3, 3, 3]) == pytest.approx(1.0)


def test_osm_helpers():
    pts = pd.DataFrame({"time": ["2014-05-01T10:00:10Z", "2014-05-01T10:00:50Z", "2019-01-01T00:00:00Z", None]})
    assert osm.unique_minutes(pts) == 2
    assert osm.top_cell_share(pd.Series(["a", "a", "b"])) == pytest.approx(2 / 3)
    r = osm.spearman_shared(pd.Series({"a": 1, "b": 2, "c": 3, "d": 9}), pd.Series({"a": 2, "b": 4, "c": 8}))
    assert r["n"] == 3 and r["rho"] == pytest.approx(1.0)


def _grid(n):
    """Rook adjacency of an n x n grid, plus one unit with no neighbour."""
    adj = {f"{i:02d}-{j:02d}": set() for i in range(n) for j in range(n)}
    for i in range(n):
        for j in range(n):
            for a, b in ((i + 1, j), (i, j + 1)):
                if a < n and b < n:
                    adj[f"{i:02d}-{j:02d}"].add(f"{a:02d}-{b:02d}")
                    adj[f"{a:02d}-{b:02d}"].add(f"{i:02d}-{j:02d}")
    adj["island"] = set()
    return adj


def test_random_contiguous_partition_covers_and_is_contiguous():
    adj = _grid(12)
    part = N.random_contiguous_partition(adj, [60, 40, 25, 15, 5], np.random.default_rng(4))
    assert set(part.index) == set(adj) and part.notna().all()
    assert part.nunique() == 5
    land = part.drop("island")
    rep = C.fragmentation_report(dict(land), adj)
    assert (rep.n_components == 1).all()


def test_random_contiguous_partition_does_not_depend_on_set_order():
    adj = _grid(10)
    shuffled = {u: set(sorted(v, reverse=True)) for u, v in reversed(list(adj.items()))}
    a = N.random_contiguous_partition(adj, [50, 30, 21], np.random.default_rng(9))
    b = N.random_contiguous_partition(shuffled, [50, 30, 21], np.random.default_rng(9))
    assert a.equals(b)


def test_recom_chain_keeps_contiguity_and_sizes():
    from omfm.analysis import recom as R

    adj = _grid(12)
    del adj["island"]
    for v in adj.values():
        v.discard("island")
    lab = pd.Series({u: ("W" if int(u[:2]) < 4 else "M" if int(u[:2]) < 8 else "E") for u in adj})
    chain = R.RecomChain(adj, lab, tol=0.10, seed=3)
    for _ in range(300):
        chain.step()
    cur = chain.labels()
    rep = C.fragmentation_report(dict(cur), adj)
    assert (rep.n_components == 1).all()
    assert (np.abs(chain.size - chain.target) <= np.floor(0.10 * chain.target)).all()
    assert chain.accepted > 0
    assert not cur.equals(lab)


def test_recom_connect_graph_joins_islands():
    from omfm.analysis import recom as R

    adj = {"a": {"b"}, "b": {"a"}, "c": set()}
    lab = pd.Series({"a": 1, "b": 1, "c": 1})
    g = R.connect_graph(adj, lab)
    assert C.components(["a", "b", "c"], g) == [{"a", "b", "c"}]


def test_recom_null_is_reproducible():
    from omfm.analysis import recom as R

    adj = _grid(8)
    del adj["island"]
    for v in adj.values():
        v.discard("island")
    lab = pd.Series({u: int(u[:2]) // 2 for u in adj})
    rng = np.random.default_rng(0)
    od = pd.DataFrame(
        [(a, b, int(rng.integers(1, 9))) for a in adj for b in rng.choice(list(adj), 5)],
        columns=["origin", "dest", "flow"],
    )
    od = D.prepare_od(od, "origin", "dest", "flow")
    r1 = R.recom_null(od, lab, adj, steps=400, burn_in=200, every=20, seed=5)
    r2 = R.recom_null(od, lab, adj, steps=400, burn_in=200, every=20, seed=5)
    assert r1["recom_mean"] == r2["recom_mean"]
    assert abs(r1["effective_areas_null"] - N.effective_areas(lab)) < 0.5
