"""Size-preserving permutation null model for the self-containment of a partition.

The partition's size distribution (units per area) is kept exactly; unit-to-area labels are
permuted among the labelled units. Whatever self-containment survives the permutation is
produced by the number and size of the areas alone - the scale effect of the modifiable
areal unit problem - and not by where the boundaries run.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = [
    "shuffle_labels",
    "shuffle_sc",
    "expected_sc",
    "effective_areas",
    "modularity",
    "random_contiguous_partition",
    "contiguous_null",
]


def shuffle_labels(labels: pd.Series, rng: np.random.Generator) -> pd.Series:
    """Permute unit -> area labels; the number of units per area is unchanged."""
    return pd.Series(rng.permutation(labels.to_numpy()), index=labels.index)


def shuffle_sc(od: pd.DataFrame, labels: pd.Series, runs: int = 60, seed: int = 0) -> dict:
    """Observed vs permuted self-containment.

    Integer-coded implementation: one permutation of 7,264 units over 1.8 M pairs takes
    about 20 ms. Returns observed value, null mean, sd, excess, the share of the observed value
    that the null reproduces, and the run values.
    """
    labels = labels.dropna()
    units = pd.Index(sorted(set(od.origin) | set(od.dest)))
    oi, di = units.get_indexer(od.origin.values), units.get_indexer(od.dest.values)
    flow = od.flow.to_numpy(dtype=float)

    codes, _ = pd.factorize(labels.to_numpy())
    pos = units.get_indexer(labels.index)
    if (pos < 0).any():
        raise ValueError("labelled units missing from the OD table")

    def sc(lab_codes: np.ndarray) -> float:
        lab = np.full(len(units), -1, dtype=np.int64)
        lab[pos] = lab_codes
        ol, dl = lab[oi], lab[di]
        m = ol >= 0
        return float(flow[m & (ol == dl)].sum() / flow[m].sum())

    rng = np.random.default_rng(seed)
    observed = sc(codes)
    vals = np.array([sc(rng.permutation(codes)) for _ in range(runs)])
    mean = float(vals.mean())
    return {
        "observed": observed,
        "null_mean": mean,
        "null_sd": float(vals.std(ddof=1)),
        "excess": observed - mean,
        "null_share": mean / observed,
        "runs": vals,
    }


def effective_areas(labels: pd.Series) -> float:
    """Effective number of areas: inverse Simpson index of the size distribution (Hill q=2).

    235 areas of which one holds 18 % of the units behave, under permutation, like about
    25 equal areas.
    """
    n = labels.dropna().value_counts().to_numpy(dtype=float)
    p = n / n.sum()
    return float(1.0 / (p**2).sum())


def expected_sc(od: pd.DataFrame, labels: pd.Series) -> dict:
    """Closed-form expectation of the permutation null.

    Two distinct labelled units share an area with probability
        h = sum_a n_a (n_a - 1) / (n (n - 1)),
    so with D = flow staying in its unit, B = flow between distinct labelled units and
    T = all flow leaving labelled units,
        E[SC_null] = (D + h B) / T.
    With every unit labelled this is d + (1 - d) h, d being the unit diagonal share: the null
    depends on the zoning system (d) and on the size distribution of the partition (h), and on
    nothing else.
    """
    labels = labels.dropna()
    lab = set(labels.index)
    n = labels.value_counts().to_numpy(dtype=float)
    h = float((n * (n - 1)).sum() / (n.sum() * (n.sum() - 1)))
    o_in, d_in = od.origin.isin(lab), od.dest.isin(lab)
    same = od.origin == od.dest
    total = od.flow[o_in].sum()
    diag = od.flow[o_in & same].sum()
    between = od.flow[o_in & d_in & ~same].sum()
    return {"h": h, "diagonal_share": float(diag / total), "expected": float((diag + h * between) / total)}


def modularity(od: pd.DataFrame, labels: pd.Series) -> float:
    """Directed modularity (Leicht & Newman 2008) of the partition on the flow matrix.

    Its null keeps every unit's outflow and inflow, so it discounts strong attractors; the
    permutation null above keeps the partition's size distribution, so it discounts scale.
    """
    d = od.assign(a_o=od.origin.map(labels), a_d=od.dest.map(labels)).dropna(subset=["a_o", "a_d"])
    t = d.flow.sum()
    inside = d[d.a_o == d.a_d].groupby("a_o").flow.sum()
    out_a, in_a = d.groupby("a_o").flow.sum(), d.groupby("a_d").flow.sum()
    q = inside.reindex(out_a.index, fill_value=0.0) / t - (out_a / t) * (in_a.reindex(out_a.index, fill_value=0.0) / t)
    return float(q.sum())


def random_contiguous_partition(adj: dict, sizes, rng: np.random.Generator) -> pd.Series:
    """One random partition into contiguous regions with (about) the given sizes.

    Seeds are drawn at random, the target sizes are dealt to them at random, and every region
    grows by taking a random unit of its frontier until it reaches its target. A region that is
    walled in stops early; units left over join a random neighbouring region, and units with no
    neighbour at all (islands) join a random region. Sizes therefore match the targets only
    approximately: report the effective number of areas next to the result.
    """
    units = sorted(adj)
    index = {u: i for i, u in enumerate(units)}
    # neighbours sorted: the iteration order of a set of strings changes between processes
    nbr = [np.array(sorted(index[v] for v in adj[u] if v in index), dtype=np.int64) for u in units]
    n, k = len(units), len(sizes)
    target = rng.permutation(np.asarray(sizes, dtype=np.int64))
    label = np.full(n, -1, dtype=np.int64)
    count = np.zeros(k, dtype=np.int64)
    frontier: list[list[int]] = [[] for _ in range(k)]
    for r, s0 in enumerate(rng.choice(n, size=k, replace=False)):
        label[s0], count[r] = r, 1
        frontier[r] = list(nbr[s0])
    active = [r for r in range(k) if count[r] < target[r] and frontier[r]]
    while active:
        deficit = np.array([target[r] - count[r] for r in active], dtype=float)
        r = active[int(rng.choice(len(active), p=deficit / deficit.sum()))]
        f = frontier[r]
        grown = False
        while f:
            j = int(rng.integers(len(f)))
            f[j], f[-1] = f[-1], f[j]
            u = f.pop()
            if label[u] < 0:
                label[u] = r
                count[r] += 1
                f.extend(int(v) for v in nbr[u] if label[v] < 0)
                grown = True
                break
        if not grown or count[r] >= target[r]:
            active.remove(r)
    left = np.flatnonzero(label < 0)
    while len(left):
        rng.shuffle(left)
        moved = False
        for u in left:
            done = nbr[u][label[nbr[u]] >= 0] if len(nbr[u]) else nbr[u]
            if len(done):
                label[u] = label[int(rng.choice(done))]
                moved = True
        left = np.flatnonzero(label < 0)
        if not moved:
            label[left] = rng.integers(0, k, size=len(left))
            break
    return pd.Series(label, index=units, name="area")


def contiguous_null(od: pd.DataFrame, labels: pd.Series, adj: dict, runs: int = 200, seed: int = 0) -> dict:
    """Self-containment of random contiguous partitions with the size distribution of ``labels``.

    The permutation null answers "what does this many areas of these sizes score?". This one
    answers "what does any contiguous zoning of these sizes score?": it keeps the short
    trips that every compact region holds, and leaves to the observed partition only what
    the position of its boundaries adds.
    """
    labels = labels.dropna()
    sub = {u: {v for v in adj.get(u, ()) if v in labels.index} for u in labels.index}
    sizes = labels.value_counts().to_numpy()
    rng = np.random.default_rng(seed)
    vals, eff = [], []
    from .selfcontainment import partition_sc

    flows = od[od.origin.isin(labels.index)]
    units = pd.Index(sorted(set(flows.origin) | set(flows.dest)))
    oi, di = units.get_indexer(flows.origin.values), units.get_indexer(flows.dest.values)
    w = flows.flow.to_numpy(dtype=float)
    total = w.sum()
    for _ in range(runs):
        part = random_contiguous_partition(sub, sizes, rng)
        lab = np.full(len(units), -1, dtype=np.int64)
        lab[units.get_indexer(part.index)] = part.to_numpy()
        ol, dl = lab[oi], lab[di]
        vals.append(float(w[(ol >= 0) & (ol == dl)].sum() / total))
        eff.append(effective_areas(part))
    vals = np.array(vals)
    observed = partition_sc(od, labels)
    return {
        "observed": observed,
        "contiguous_mean": float(vals.mean()),
        "contiguous_sd": float(vals.std(ddof=1)),
        "contiguous_min": float(vals.min()),
        "contiguous_max": float(vals.max()),
        "share_below_observed": float((vals < observed).mean()),
        "effective_areas_null": float(np.mean(eff)),
        "runs": vals,
    }
