"""Random contiguous partitions with (nearly) fixed area sizes: a recombination Markov chain.

The chain of DeFord, Duchin and Solomon (2021), with sizes anchored to the partition it starts
from. One step:

1. pick an area at random, then one of its neighbouring areas at random;
2. merge the two and draw a uniform spanning tree of the merged units (Wilson's algorithm);
3. among the tree edges whose removal leaves two pieces with the two target sizes (each within
   a tolerance), cut one at random; if there is none, try another tree, and after
   ``max_tries`` keep the state.

Every state is a partition into contiguous areas whose sizes stay within ``tol`` of the sizes
of the starting partition, so the effective number of areas is preserved by construction.
The stationary distribution is not uniform over partitions: it weights a partition by the
number of spanning trees of its areas, which favours compact areas. That is the standard
ensemble of the redistricting literature, and it is stated as such wherever it is used.

Units that no polygon edge connects to the rest (islands) get one extra edge to the nearest
unit of the same area, so that every area of the starting partition is connected.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["connect_graph", "RecomChain", "recom_null", "trace_diagnostics"]


def connect_graph(adj: dict, labels: pd.Series, centroids: pd.DataFrame | None = None) -> dict:
    """Return a copy of ``adj`` in which every area of ``labels`` is connected.

    Components of an area that the polygons leave apart are joined through the closest pair of
    units (by centroid distance when ``centroids`` with columns x, y is given, else by the first
    unit of each component in sorted order).
    """
    import networkx as nx

    adj = {u: set(v) for u, v in adj.items()}
    for u in labels.index:
        adj.setdefault(u, set())
    for _, units in labels.groupby(labels).groups.items():
        g = nx.Graph()
        units = sorted(units)
        g.add_nodes_from(units)
        us = set(units)
        g.add_edges_from((u, v) for u in units for v in adj[u] if v in us)
        comps = sorted((sorted(c) for c in nx.connected_components(g)), key=lambda c: (-len(c), c[0]))
        main = comps[0]
        for comp in comps[1:]:
            if centroids is not None:
                a = centroids.loc[comp, ["x", "y"]].to_numpy()
                b = centroids.loc[main, ["x", "y"]].to_numpy()
                d = ((a[:, None, :] - b[None, :, :]) ** 2).sum(axis=2)
                i, j = np.unravel_index(int(np.argmin(d)), d.shape)
                u, v = comp[i], main[j]
            else:
                u, v = comp[0], main[0]
            adj[u].add(v)
            adj[v].add(u)
            main = sorted(set(main) | set(comp))
    return adj


class RecomChain:
    """Recombination chain on integer-coded units. See the module docstring."""

    def __init__(self, adj: dict, labels: pd.Series, tol: float = 0.05, max_tries: int = 20, seed: int = 0):
        labels = labels.dropna()
        self.units = pd.Index(sorted(labels.index))
        idx = {u: i for i, u in enumerate(self.units)}
        codes, self.area_names = pd.factorize(labels.reindex(self.units).to_numpy(), sort=True)
        self.lab = codes.astype(np.int64)
        self.nbr = [np.array(sorted(idx[v] for v in adj.get(u, ()) if v in idx), dtype=np.int64) for u in self.units]
        self.k = int(self.lab.max()) + 1
        self.target = np.bincount(self.lab, minlength=self.k)
        self.size = self.target.copy()
        self.tol = np.maximum(0, np.floor(tol * self.target)).astype(np.int64)
        self.max_tries = max_tries
        self.rng = np.random.default_rng(seed)
        self.accepted = 0
        self.steps = 0
        self._local = np.full(len(self.units), -1, dtype=np.int64)
        self._check_contiguous()

    # ------------------------------------------------------------------ helpers
    def _check_contiguous(self) -> None:
        for a in range(self.k):
            members = np.flatnonzero(self.lab == a)
            seen = {int(members[0])}
            stack = [int(members[0])]
            inside = set(members.tolist())
            while stack:
                u = stack.pop()
                for v in self.nbr[u]:
                    v = int(v)
                    if v in inside and v not in seen:
                        seen.add(v)
                        stack.append(v)
            if len(seen) != len(members):
                raise ValueError(f"area {self.area_names[a]} is not connected; use connect_graph first")

    def _neighbour_areas(self, a: int) -> np.ndarray:
        members = np.flatnonzero(self.lab == a)
        nb = np.concatenate([self.nbr[u] for u in members]) if len(members) else np.array([], dtype=np.int64)
        other = np.unique(self.lab[nb])
        return other[other != a]

    def _spanning_tree(self, nodes: np.ndarray) -> np.ndarray:
        """Uniform spanning tree of the subgraph on ``nodes`` (Wilson). Returns local parent array."""
        m = len(nodes)
        local = self._local
        local[nodes] = np.arange(m)
        nbrs = []
        for u in nodes:
            ln = local[self.nbr[u]]
            nbrs.append(ln[ln >= 0])
        rng = self.rng
        in_tree = np.zeros(m, dtype=bool)
        parent = np.full(m, -1, dtype=np.int64)
        order = rng.permutation(m)
        in_tree[order[0]] = True
        # pre-draw uniform numbers in blocks to avoid one Generator call per move
        buf = rng.random(4096)
        pos = 0
        for start in order[1:]:
            u = int(start)
            while not in_tree[u]:
                nb = nbrs[u]
                if pos == len(buf):
                    buf = rng.random(4096)
                    pos = 0
                parent[u] = nb[int(buf[pos] * len(nb))]
                pos += 1
                u = int(parent[u])
            u = int(start)
            while not in_tree[u]:
                in_tree[u] = True
                u = int(parent[u])
        local[nodes] = -1
        return parent

    @staticmethod
    def _subtree_sizes(parent: np.ndarray) -> np.ndarray:
        m = len(parent)
        children = [[] for _ in range(m)]
        root = -1
        for u in range(m):
            p = parent[u]
            if p < 0:
                root = u
            else:
                children[p].append(u)
        order = [root]
        for u in order:
            order.extend(children[u])
        size = np.ones(m, dtype=np.int64)
        for u in reversed(order):
            p = parent[u]
            if p >= 0:
                size[p] += size[u]
        return size

    # --------------------------------------------------------------------- step
    def step(self) -> bool:
        self.steps += 1
        rng = self.rng
        a = int(rng.integers(self.k))
        nb = self._neighbour_areas(a)
        if not len(nb):
            return False
        b = int(nb[int(rng.integers(len(nb)))])
        nodes = np.flatnonzero((self.lab == a) | (self.lab == b))
        m = len(nodes)
        ta, tb = self.target[a], self.target[b]
        lo_a, hi_a = ta - self.tol[a], ta + self.tol[a]
        lo_b, hi_b = tb - self.tol[b], tb + self.tol[b]
        for _ in range(self.max_tries):
            parent = self._spanning_tree(nodes)
            size = self._subtree_sizes(parent)
            s = size[parent >= 0]
            cand = np.flatnonzero(parent >= 0)
            ok_a = (s >= lo_a) & (s <= hi_a) & (m - s >= lo_b) & (m - s <= hi_b)  # subtree becomes a
            ok_b = (s >= lo_b) & (s <= hi_b) & (m - s >= lo_a) & (m - s <= hi_a)  # subtree becomes b
            choices = np.concatenate(
                [
                    np.stack([cand[ok_a], np.zeros(ok_a.sum(), int)], 1),
                    np.stack([cand[ok_b], np.ones(ok_b.sum(), int)], 1),
                ]
            )
            if not len(choices):
                continue
            u, side = choices[int(rng.integers(len(choices)))]
            # collect the subtree of local node u
            children = [[] for _ in range(m)]
            for v in range(m):
                if parent[v] >= 0:
                    children[parent[v]].append(v)
            sub, stack = [], [int(u)]
            while stack:
                v = stack.pop()
                sub.append(v)
                stack.extend(children[v])
            in_sub = np.zeros(m, dtype=bool)
            in_sub[sub] = True
            first, second = (a, b) if side == 0 else (b, a)
            self.lab[nodes[in_sub]] = first
            self.lab[nodes[~in_sub]] = second
            self.size[a] = int((self.lab[nodes] == a).sum())
            self.size[b] = m - self.size[a]
            self.accepted += 1
            return True
        return False

    def labels(self) -> pd.Series:
        return pd.Series(self.area_names[self.lab], index=self.units, name="area")


def recom_null(
    od: pd.DataFrame,
    labels: pd.Series,
    adj: dict,
    steps: int = 20_000,
    burn_in: int = 10_000,
    every: int = 100,
    tol: float = 0.05,
    seed: int = 0,
    centroids: pd.DataFrame | None = None,
) -> dict:
    """Self-containment of partitions drawn from the recombination chain started at ``labels``.

    Returns the samples, their mean, sd, range, effective number of areas and acceptance rate, and
    two mixing diagnostics: the adjusted Rand index of each sample with the starting partition, and
    between samples half the run apart. When the two are equal the chain has forgotten its start.
    """
    from .agreement import adjusted_rand, contingency
    from .nullmodel import effective_areas
    from .selfcontainment import partition_sc

    labels = labels.dropna()
    graph = connect_graph(adj, labels, centroids)
    chain = RecomChain(graph, labels, tol=tol, seed=seed)

    flows = od[od.origin.isin(chain.units)]
    oi = chain.units.get_indexer(flows.origin.to_numpy())
    di = chain.units.get_indexer(flows.dest.to_numpy())
    w = flows.flow.to_numpy(dtype=float)
    total = w.sum()

    def sc(lab: np.ndarray) -> float:
        ol = lab[oi]
        dl = np.where(di >= 0, lab[np.maximum(di, 0)], -1)
        return float(w[(di >= 0) & (ol == dl)].sum() / total)

    def ari_codes(a: np.ndarray, b: np.ndarray) -> float:
        return adjusted_rand(contingency(pd.Series(a), pd.Series(b)))

    start_codes = chain.lab.copy()
    vals, eff, ari, trace, kept = [], [], [], [], []
    for t in range(1, steps + 1):
        chain.step()
        if t % every == 0:
            trace.append((t, sc(chain.lab)))
            if t > burn_in:
                vals.append(trace[-1][1])
                eff.append(effective_areas(pd.Series(chain.lab)))
                ari.append(ari_codes(chain.lab, start_codes))
                kept.append(chain.lab.copy())
    vals = np.array(vals)
    half = len(kept) // 2
    # structure shared by samples far apart in the chain: if it equals the structure shared with the
    # start, the start is not special and the resemblance comes from the sizes and the geography
    within = [ari_codes(kept[i], kept[i + half]) for i in range(half)]
    observed = partition_sc(od, labels)
    return {
        "observed": observed,
        "recom_mean": float(vals.mean()),
        "recom_sd": float(vals.std(ddof=1)),
        "recom_min": float(vals.min()),
        "recom_max": float(vals.max()),
        "share_below_observed": float((vals < observed).mean()),
        "effective_areas_null": float(np.mean(eff)),
        "effective_areas_observed": effective_areas(labels),
        "ari_with_start_mean": float(np.mean(ari)),
        "ari_with_start_last": float(ari[-1]),
        "ari_between_samples_mean": float(np.mean(within)),
        "acceptance": chain.accepted / chain.steps,
        "samples": len(vals),
        "trace": pd.DataFrame(trace, columns=["step", "sc"]),
        "runs": vals,
    }


def trace_diagnostics(trace: pd.DataFrame, burn_in: int) -> dict:
    """Convergence checks on the self-containment trace of one chain.

    ``steps_to_range``: first recorded step at which the trace falls inside the range of the kept
    states, i.e. how long the chain takes to leave the start. ``lag1``: autocorrelation of
    consecutive kept states. ``geweke_z``: difference between the mean of the first 10 % and the last
    50 % of the kept states, in standard errors inflated for the lag-1 autocorrelation [Geweke 1992].
    """
    kept = trace.loc[trace.step > burn_in, "sc"].to_numpy(dtype=float)
    lag1 = float(np.corrcoef(kept[:-1], kept[1:])[0, 1])
    k = max(2, len(kept) // 10)
    a, b = kept[:k], kept[len(kept) // 2 :]
    infl = (1 + lag1) / (1 - lag1)
    se = np.sqrt(a.var(ddof=1) / len(a) * infl + b.var(ddof=1) / len(b) * infl)
    return {
        "steps_to_range": int(trace.step[trace.sc <= kept.max()].iloc[0]),
        "lag1": lag1,
        "geweke_z": float((a.mean() - b.mean()) / se),
    }
