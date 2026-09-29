"""Contiguity of flow-built areas: diagnosis and repair.

A flow-only delimitation can attach a unit to an area it does not touch. The repair keeps the
component that holds the core (else the largest) and hands every other component to the adjacent
area with the strongest two-way flow across the shared border. Components with no labelled
neighbour are islands: they stay and are reported.
"""

from __future__ import annotations

from collections import defaultdict

import pandas as pd

__all__ = ["queen_adjacency", "components", "fragmentation_report", "repair"]


def queen_adjacency(gdf, id_col: str) -> dict[str, set]:
    """Queen adjacency (shared point suffices) from polygons, via libpysal."""
    from libpysal.weights import Queen

    g = gdf[[id_col, "geometry"]].reset_index(drop=True)
    w = Queen.from_dataframe(g, use_index=False, silence_warnings=True)
    ids = g[id_col].to_numpy()
    return {ids[i]: {ids[j] for j in nb} for i, nb in w.neighbors.items()}


def components(units, adj: dict[str, set]) -> list[set]:
    """Connected components of ``units`` under ``adj``, largest first (networkx)."""
    import networkx as nx

    us = set(units)
    g = nx.Graph()
    g.add_nodes_from(us)
    g.add_edges_from((u, v) for u in us for v in adj.get(u, ()) if v in us)
    return sorted((set(c) for c in nx.connected_components(g)), key=lambda c: (-len(c), min(c)))


def fragmentation_report(assign: dict, adj: dict[str, set]) -> pd.DataFrame:
    """Per area: number of units, components, and units cut off from the main component."""
    groups = defaultdict(list)
    for u, a in assign.items():
        groups[a].append(u)
    rows = []
    for a, units in groups.items():
        comps = components(units, adj)
        rows.append(
            {"area": a, "n_units": len(units), "n_components": len(comps), "cut_units": len(units) - len(comps[0])}
        )
    return pd.DataFrame(rows).sort_values(["n_components", "area"], ascending=[False, True]).reset_index(drop=True)


def repair(od: pd.DataFrame, assign: dict, adj: dict[str, set], cores: set | None = None, max_rounds: int = 10) -> dict:
    """Reassign cut-off components to the adjacent area with the strongest border flow."""
    assign = dict(assign)
    cores = cores or set()
    ext = od[od.origin != od.dest]
    flow_uu = dict(zip(zip(ext.origin, ext.dest), ext.flow))

    def link(comp: set, members: set) -> float:
        return sum(
            flow_uu.get((u, v), 0.0) + flow_uu.get((v, u), 0.0) for u in comp for v in adj.get(u, ()) if v in members
        )

    for _ in range(max_rounds):
        groups = defaultdict(set)
        for u, a in assign.items():
            groups[a].add(u)
        moved = 0
        for a in sorted(groups):
            comps = components(groups[a], adj)
            if len(comps) == 1:
                continue
            main = next((i for i, c in enumerate(comps) if c & cores), 0)
            for i, comp in enumerate(comps):
                if i == main:
                    continue
                nb = {assign[v] for u in comp for v in adj.get(u, ()) if v in assign and assign[v] != a}
                if not nb:
                    continue  # island
                best = max(sorted(nb), key=lambda x: link(comp, groups[x]))
                for u in comp:
                    assign[u] = best
                moved += len(comp)
        if moved == 0:
            break
    return assign
