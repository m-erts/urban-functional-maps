"""Every figure of the paper and the slides, drawn from ``outputs/tables`` and ``data/interim``.

One function per figure. Charts are written as PNG and SVG, maps as PNG.
Run ``python scripts/run.py figures`` after ``analysis``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import yaml

from ..config import params, path
from . import style as st

__all__ = ["all_figures"]

AREA_TINTS = ["#FEF3C7", "#FCD34D", "#FDE68A", "#F59E0B", "#FFFBEB", "#FBBF24"]
AREA_TINTS_BLUE = ["#DBEAFE", "#93C5FD", "#BFDBFE", "#60A5FA", "#EFF6FF", "#3B82F6"]


# ------------------------------------------------------------------------------- helpers
def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    st.apply()
    return plt


def _golden() -> dict:
    return yaml.safe_load(path("tables", "golden_actual.yaml").read_text())


def _tab(name: str) -> pd.DataFrame:
    return pd.read_csv(path("tables", name))


def _head(fig, title: str, subtitle: str = "", x: float = 0.04, y: float = 0.965) -> None:
    import textwrap

    fig.text(x, y, title, fontsize=13, fontweight="bold", color=st.INK, ha="left", va="top", gid="chrome")
    if subtitle:
        lines = textwrap.wrap(subtitle, int(fig.get_figwidth() * 0.92 * 14.5))
        fig.text(
            x,
            y - 0.048,
            "\n".join(lines),
            fontsize=9.5,
            color=st.INK2,
            ha="left",
            va="top",
            linespacing=1.35,
            gid="chrome",
        )


def _foot(fig, text: str, x: float = 0.04, y: float = 0.018) -> None:
    import textwrap

    width = int(fig.get_figwidth() * 0.92 * 18.5)
    lines = [w for part in text.split("\n") for w in textwrap.wrap(part, width)]
    fig.text(
        x, y, "\n".join(lines), fontsize=7.5, color=st.MUTED, ha="left", va="bottom", linespacing=1.35, gid="chrome"
    )


def _save(fig, name: str, vector: bool = True, bare: bool = True) -> None:
    """Write the figure, and a second copy without title, subtitle and footer for the slides."""
    import matplotlib.pyplot as plt

    out = path("figures", f"{name}.png", mkdir=True)
    fig.savefig(out, dpi=200)
    if vector:
        fig.savefig(out.with_suffix(".svg"))
    if bare:
        for t in [t for t in fig.texts if t.get_gid() == "chrome"]:
            t.remove()
        fig.savefig(out.with_name(f"{name}_bare.png"), dpi=200, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print(f"[omfm] figure {out.name}", flush=True)


def _map_axes(ax) -> None:
    ax.set_axis_off()
    ax.set_aspect("equal")


def _value_labels(ax, bars, fmt="{:.3f}", dy=0.012) -> None:
    for b in bars:
        ax.text(
            b.get_x() + b.get_width() / 2,
            b.get_height() + dy,
            fmt.format(b.get_height()),
            ha="center",
            va="bottom",
            fontsize=8.5,
            color=st.INK,
            family=st.MONO,
        )


# ------------------------------------------------------------------ UK: trap 1, the code list
def uk_trap1() -> None:
    plt, g = _plt(), _golden()
    fig = plt.figure(figsize=(10.5, 5.2))
    _head(
        fig,
        "One category of the code list moves the national figure fivefold",
        "England and Wales, MSOA to MSOA. Left: share of commuters who work in the MSOA where they live. "
        "Right: who is in the table.",
    )
    ax = fig.add_axes([0.06, 0.24, 0.40, 0.55])
    vals = [g["uk_diag_2011"], g["uk_diag_2021_naive"], g["uk_diag_2021_clean"]]
    labs = ["2011\nspecial codes\nexcluded", "2021\nindicator 1 kept\n(file as published)", "2021\nindicator 3 only"]
    bars = ax.bar(range(3), vals, width=0.30, color=[st.CENSUS, st.ARTEFACT, st.CENSUS])
    _value_labels(ax, bars)
    ax.set_xticks(range(3), labs)
    ax.set_ylim(0, 0.6)
    ax.set_ylabel("unit diagonal share")
    ax.grid(axis="x", visible=False)
    ax.set_title("Self-containment of the unit")

    ax2 = fig.add_axes([0.56, 0.36, 0.40, 0.43])
    fixed = np.array([g["uk_fixed_2011"], g["uk_fixed_2021"]]) / 1e6
    home = np.array([g["uk_home_2011"], g["uk_home_2021"]]) / 1e6
    y = np.arange(2)
    ax2.barh(y, fixed, height=0.30, color=st.CENSUS, label="fixed workplace in England and Wales")
    ax2.barh(
        y,
        home,
        left=fixed + 0.12,
        height=0.30,
        color=st.RAMP["census"][1],
        hatch="////",
        edgecolor=st.RAMP["census"][4],
        linewidth=0,
        label="mainly at or from home, or no fixed place",
    )
    for i in range(2):
        ax2.text(
            fixed[i] / 2, y[i], f"{fixed[i]:.1f} M", ha="center", va="center", color="white", fontsize=9, family=st.MONO
        )
        ax2.text(
            fixed[i] + 0.12 + home[i] / 2,
            y[i],
            f"{home[i]:.1f} M",
            ha="center",
            va="center",
            color=st.INK,
            fontsize=9,
            family=st.MONO,
        )
    ax2.set_yticks(y, ["2011", "2021"])
    ax2.set_ylim(1.5, -0.5)
    ax2.set_xlabel("employed residents, millions")
    ax2.grid(axis="y", visible=False)
    ax2.set_title("Where the 2021 census puts people without a commute")
    ax2.legend(loc="upper left", bbox_to_anchor=(0.0, -0.22), ncol=1, handlelength=1.6)
    _foot(
        fig,
        "ONS ODWP01EW (2021, census day 21 March 2021) and WU01EW (2011). In 2021 indicator 1 is coded with "
        "workplace = residence; in 2011 the same people carry pseudo-codes OD0000001 and OD0000003.",
    )
    _save(fig, "uk_trap1_code_list")


# ------------------------------------------------------------------ UK: trap 2, the null model
def uk_null_model() -> None:
    plt = _plt()
    nm = _tab("uk_null_model.csv")
    rows = [
        ("MSOA", 2011, "flows_only", "MSOA 2011\nown rules"),
        ("MSOA", 2011, "official_ttwa_2011", "MSOA 2011\nofficial TTWA"),
        ("MSOA", 2021, "flows_only", "MSOA 2021\nown rules"),
        ("MSOA", 2021, "official_ttwa_2011", "MSOA 2021\nofficial TTWA"),
        ("LAD", 2021, "flows_only_fixed_q95", "District 2021\nown rules"),
        ("LAD", 2021, "flows_only_naive_q85", "District 2021\nindicator 1 kept"),
    ]
    d = pd.concat(
        [nm[(nm.scale == s) & (nm.year == y) & (nm.partition == p)].assign(label=lab) for s, y, p, lab in rows]
    )
    fig = plt.figure(figsize=(10.5, 5.4))
    _head(
        fig,
        "What random assignment already scores",
        "Self-containment of a partition (bar) against 1,000 random partitions with the same area sizes "
        "(grey). The difference is what the boundaries add.",
    )
    ax = fig.add_axes([0.07, 0.17, 0.90, 0.62])
    x = np.arange(len(d))
    cols = [st.ARTEFACT if "naive" in p else st.CENSUS for p in d.partition]
    ax.bar(x, d.null_mean, width=0.46, color=st.RULE, label="random partition, same sizes (mean)")
    ax.bar(x, d.observed - d.null_mean, bottom=d.null_mean + 0.004, width=0.46, color=cols, label="excess over random")
    ax.errorbar(
        x,
        d.null_mean,
        yerr=[d.null_mean - d.null_min, d.null_max - d.null_mean],
        fmt="none",
        ecolor=st.INK2,
        elinewidth=1,
        capsize=3,
    )
    for i, r in enumerate(d.itertuples()):
        ax.text(i, r.observed + 0.02, f"{r.observed:.3f}", ha="center", fontsize=9, family=st.MONO, color=st.INK)
        ax.text(
            i,
            r.null_mean / 2,
            f"{r.null_mean:.3f}",
            ha="center",
            va="center",
            fontsize=8.5,
            family=st.MONO,
            color=st.INK2,
        )
        ax.text(
            i + 0.27,
            (r.observed + r.null_mean) / 2,
            f"+{r.excess:.2f}",
            ha="left",
            va="center",
            fontsize=8.5,
            family=st.MONO,
            color=st.INK,
        )
        ax.text(
            i,
            -0.115,
            f"{int(r.areas)} areas\n{r.effective_areas:.1f} effective",
            ha="center",
            va="top",
            fontsize=7.8,
            color=st.MUTED,
            transform=ax.get_xaxis_transform(),
        )
    ax.set_xticks(x, d.label)
    ax.tick_params(axis="x", pad=2)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("self-containment")
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left", ncol=2)
    _foot(
        fig,
        "Whiskers: minimum and maximum of 1,000 permutations. Effective areas = inverse Simpson index of the "
        "area-size distribution. Red: matrix that still contains people coded at their residence.",
    )
    _save(fig, "uk_trap2_null_model")


def uk_decomposition() -> None:
    """Scale, contiguity and placement for every partition of the three countries with pairs."""
    plt = _plt()
    d = _tab("decomposition.csv")
    names = {
        "uk_2011_own": "England & Wales 2011, heuristic",
        "uk_2011_lma": "England & Wales 2011, Coombes-Bond",
        "uk_2011_lma_ons": "England & Wales 2011, Coombes-Bond, ONS coding",
        "uk_2011_official": "England & Wales 2011, official TTWA",
        "uk_2021_own": "England & Wales 2021, heuristic",
        "uk_2021_official": "England & Wales 2021, official TTWA",
        "nl_2023_own": "Netherlands 2023, heuristic",
        "nl_2023_lma": "Netherlands 2023, Coombes-Bond",
        "nl_2023_corop": "Netherlands 2023, COROP (1970)",
        "es_2023_own": "Spain 2023, heuristic",
        "es_2023_lma": "Spain 2023, Coombes-Bond",
    }
    d = d[d.partition.isin(names)].copy()
    d["order"] = d.partition.map({k: i for i, k in enumerate(names)})
    d = d.sort_values("order").reset_index(drop=True)
    d["label"] = [
        f"{names[p_]}\n{a} areas, {e:.0f} effective" for p_, a, e in zip(d.partition, d.areas, d.effective_areas)
    ]
    fig = plt.figure(figsize=(11.0, 1.9 + 0.62 * len(d)))
    _head(
        fig,
        "Most of the score is scale and contiguity",
        "Self-containment split into what the sizes of the areas give (random relabelling), what any contiguous "
        "zoning of those sizes adds (recombination chain) and what the position of the boundaries adds.",
    )
    top = 1 - 1.25 / fig.get_figheight()
    bottom = 1.15 / fig.get_figheight()
    ax = fig.add_axes([0.30, bottom, 0.66, top - bottom])
    y = np.arange(len(d))
    gap = 0.004
    parts = [
        ("from_scale", st.RULE, "scale", st.INK),
        ("from_contiguity", st.RAMP["census"][1], "contiguity", st.INK),
        ("from_placement", st.CENSUS, "placement", "white"),
    ]
    left = np.zeros(len(d))
    for col, colour, label, ink in parts:
        w = d[col].to_numpy()
        ax.barh(y, w - gap, left=left, height=0.56, color=colour, label=label)
        for i in range(len(d)):
            if w[i] > 0.045:
                ax.text(
                    left[i] + w[i] / 2,
                    y[i],
                    f"{w[i]:.2f}",
                    ha="center",
                    va="center",
                    fontsize=8.4,
                    family=st.MONO,
                    color=ink,
                )
        left += w
    for i, r in enumerate(d.itertuples()):
        ax.text(r.observed + 0.008, i, f"{r.observed:.3f}", va="center", fontsize=8.8, family=st.MONO, color=st.INK)
    country = d.partition.str[:2].to_numpy()
    for i in range(1, len(d)):
        if country[i] != country[i - 1]:
            ax.axhline(i - 0.5, color=st.RULE, linewidth=0.8)
    ax.set_yticks(y, d.label, fontsize=8.4)
    ax.set_ylim(len(d) - 0.5, -0.5)
    ax.set_xlim(0, 0.95)
    ax.set_xlabel("self-containment")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=3, handlelength=1.4, columnspacing=1.6)
    _foot(
        fig,
        f"Recombination chain: {int(d.samples.iloc[0])} samples after burn-in, area sizes within "
        f"{params()['recom']['tolerance'] * 100:.0f} % of the partition's. ONS coding: people who work at home, "
        "offshore or with no fixed place counted at their residence. Sources: ONS (OGL v3); CBS 85481NED "
        "(CC BY 4.0); Basado en datos abiertos Ministerio de Transportes y Movilidad Sostenible.",
    )
    _save(fig, "uk_decomposition")


def _uk_layers(year: int):
    from ..sources import uk_census as src

    g = src.load_boundaries(year)
    parts = {
        k: pd.read_csv(path("tables", f"uk_{year}_areas_{k}.csv")).dropna(subset=["area"]).set_index("unit").area
        for k in ("flows_only", "contiguous", "ttwa_greedy", "ttwa_dissolution")
    }
    return g, parts


def _tints(dis, palette) -> list:
    """Greedy colouring of touching areas, so that neighbours never share a tint."""
    from libpysal.weights import Queen

    w = Queen.from_dataframe(dis.reset_index(drop=True), use_index=False, silence_warnings=True)
    order = sorted(w.neighbors, key=lambda i: -len(w.neighbors[i]))
    col: dict = {}
    for i in order:
        used = {col[j] for j in w.neighbors[i] if j in col}
        col[i] = next(c for c in range(len(palette)) if c not in used) if len(used) < len(palette) else 0
    return [palette[col[i]] for i in range(len(dis))]


def _outline(ax, g, labels: pd.Series, fill=None, lw=0.45, color=None, tint=None) -> None:
    """Areas of ``labels`` dissolved from the unit polygons ``g``. ``tint``: a list of colours for
    neighbouring areas (greedy colouring); otherwise one fill colour."""
    d = g.merge(labels.rename("area"), left_on="unit", right_index=True, how="inner")
    dis = d.dissolve("area")
    face = _tints(dis, tint) if tint else (fill or st.RAMP["census"][0])
    dis.plot(ax=ax, facecolor=face, edgecolor=color or st.INK2, linewidth=lw)


def uk_areas_map() -> None:
    from ..analysis import contiguity as C

    plt, gold = _plt(), _golden()
    g, parts = _uk_layers(2021)
    e = (
        pd.read_parquet(path("interim", "uk_msoa_adj_2021.parquet"))
        if path("interim", "uk_msoa_adj_2021.parquet").exists()
        else None
    )
    adj = C.queen_adjacency(g, "unit") if e is None else _adj(e)
    fig = plt.figure(figsize=(11.5, 7.4))
    _head(
        fig,
        "Areas built from flows alone are not contiguous",
        "England and Wales, Census 2021, commuters with a fixed workplace. Red: units cut off from the body "
        "of their area.",
    )
    for i, (key, title) in enumerate(
        [
            (
                "flows_only",
                f"Flows only: {gold['uk_areas_flows_only_2021']} areas, "
                f"{gold['uk_noncontig_2021']} non-contiguous, {gold['uk_cut_units_2021']} units cut off",
            ),
            (
                "contiguous",
                f"After contiguity repair: {gold['uk_islands_2021']} areas keep an island, "
                f"{gold['uk_island_units_2021']} units",
            ),
        ]
    ):
        ax = fig.add_axes([0.02 + 0.49 * i, 0.06, 0.47, 0.76])
        _map_axes(ax)
        _outline(ax, g, parts[key])
        cut = set()
        for _, units in parts[key].groupby(parts[key]).groups.items():
            for comp in C.components(list(units), adj)[1:]:
                cut |= comp
        if cut:
            g[g.unit.isin(cut)].plot(ax=ax, facecolor=st.ARTEFACT, edgecolor=st.ARTEFACT, linewidth=0.9)
        ax.set_title(title, fontsize=10)
    _foot(
        fig,
        st.ATTRIBUTION["ons"] + ". ODWP01EW, MSOA 2021 BGC, EPSG:27700. Rules: cores at the 0.95 quantile of "
        "external inflow, core merge 0.10, attachment 0.15.",
    )
    _save(fig, "uk_areas_contiguity", vector=False)


def _adj(edges: pd.DataFrame) -> dict:
    from collections import defaultdict

    adj = defaultdict(set)
    for a, b in edges.itertuples(index=False):
        adj[a].add(b)
        adj[b].add(a)
    return dict(adj)


def uk_ttwa_triptych() -> None:
    import geopandas as gpd

    from ..sources import uk_census as src

    plt, gold = _plt(), _golden()
    g, parts = _uk_layers(2011)
    for key, name in [("lma", "uk_2011_areas_lma.csv"), ("lma_ons", "uk_2011_areas_lma_ons.csv")]:
        if path("tables", name).exists():
            d = pd.read_csv(path("tables", name), dtype=str)
            parts[key] = pd.Series(d.area.to_numpy(), index=d.unit.to_numpy())
    ref = src.msoa_to_ttwa(2011).set_index("unit").ttwa
    tt = gpd.read_file(path("raw", params()["uk"]["ttwa_2011"])).to_crs(params()["uk"]["crs"])
    code = next(c for c in tt.columns if c.upper().startswith("TTWA11CD"))
    tt = tt[tt[code].isin(set(ref))]
    panels = [("contiguous", "Two-rule heuristic", "contiguous")]
    if "lma" in parts:
        panels.append(("lma", "Coombes-Bond, commuters only", "lma"))
    else:
        panels.append(("ttwa_greedy", "Validity rule, greedy merge", "ttwa_greedy"))
    if "lma_ons" in parts:
        panels.append(("lma_ons", "Coombes-Bond, home workers at home", "lma_ons"))
    panels.append((None, "Official Travel to Work Areas 2011", None))
    n = len(panels)
    fig = plt.figure(figsize=(3.3 * n + 0.6, 6.6))
    _head(
        fig,
        f"One criterion, {({3: 'three', 4: 'four', 5: 'five'}).get(n, n)} maps",
        "England and Wales, Census 2011, MSOA units. The two Coombes-Bond maps differ only in where people who work "
        "at home are counted. Agreement with the official areas is counted in employed residents.",
    )
    w = 0.98 / n
    for i, (key, title, gk) in enumerate(panels):
        ax = fig.add_axes([0.01 + w * i, 0.08, w - 0.01, 0.70])
        _map_axes(ax)
        if key:
            _outline(ax, g, parts[key], fill=st.RAMP["census"][0])
            sub = (
                f"{parts[key].nunique()} areas   ARI {gold[f'uk_ari_{gk}_2011']:.2f}\n"
                f"mean IoU {gold[f'uk_iou_{gk}_2011']:.2f}"
            )
        else:
            tt.plot(ax=ax, facecolor=st.SURFACE, edgecolor=st.REFERENCE, linewidth=0.45)
            sub = f"{len(tt)} areas touch England or Wales\n(built from smaller units)"
        bb = g.total_bounds
        ax.set_xlim(bb[0] - 5_000, bb[2] + 5_000)
        ax.set_ylim(bb[1] - 5_000, bb[3] + 5_000)
        ax.set_title(title, fontsize=10, pad=30)
        ax.text(0.0, 1.005, sub, transform=ax.transAxes, fontsize=8.3, color=st.INK2, family=st.MONO, va="bottom")
    _foot(
        fig,
        st.ATTRIBUTION["ons"] + ". WU01EW; MSOA 2011 BGC; TTWA 2011 super-generalised boundaries. Coombes-Bond: R "
        "package LabourMarketAreas 3.4 with the parameters of the official areas (3,500 and 66.7 %, 25,000 and 75 %); "
        "'home workers at home' counts people working at or from home, offshore or with no fixed place at their "
        "residence, as ONS did for the official areas. ARI = adjusted Rand index; IoU = intersection over union with "
        "the best-matching official area.",
    )
    _save(fig, "uk_trap3_three_maps", vector=False)


def uk_iou() -> None:
    plt, gold = _plt(), _golden()
    fig = plt.figure(figsize=(10.5, 5.0))
    _head(
        fig,
        "A similar number of areas is not a similar map",
        "Intersection over union between each official TTWA and its best-matching delimited area, weighted by "
        "employed residents.",
    )
    rep = _tab("uk_2011_match_report.csv")
    ag = _tab("uk_agreement.csv")
    ax = fig.add_axes([0.07, 0.14, 0.36, 0.64])
    r = rep.sort_values("iou")
    ax.step(r.iou, np.cumsum(r.weight) / r.weight.sum(), where="post", color=st.CENSUS)
    ax.axvline(0.5, color=st.RULE, linewidth=1)
    below = float(r.weight[r.iou < 0.5].sum() / r.weight.sum())
    ax.text(
        0.49,
        0.93,
        f"{below:.0%} of employed residents live in an\nofficial area matched at IoU < 0.5",
        ha="right",
        va="top",
        fontsize=8.5,
        color=st.INK2,
        transform=ax.transAxes,
    )
    ax.set_xlabel("IoU of official area with its best match")
    ax.set_ylabel("cumulative share of employed residents")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("2011, two-rule heuristic")

    ax2 = fig.add_axes([0.69, 0.26, 0.28, 0.52])
    a = ag[ag.partition.isin(["contiguous", "ttwa_greedy", "ttwa_dissolution"])].copy()
    lma_file = path("tables", "uk_lma_agreement.csv")
    if lma_file.exists():
        lm = pd.read_csv(lma_file)
        lm = lm[lm.comparison.isin(["lma", "lma_ons"])].assign(partition=lambda x: x.comparison, year=2011)
        a = pd.concat([a, lm[["partition", "year", "n_candidate", "ari_weighted", "mean_iou_weighted"]]])
    names = {
        "contiguous": "heuristic",
        "ttwa_greedy": "rule + greedy merge",
        "ttwa_dissolution": "rule + dissolution",
        "lma": "Coombes-Bond",
        "lma_ons": "Coombes-Bond, ONS coding",
    }
    order = {k: i for i, k in enumerate(names)}
    a["label"] = a.partition.map(names) + " " + a.year.astype(str)
    a = a.assign(o=a.partition.map(order)).sort_values(["year", "o"]).reset_index(drop=True)
    y = np.arange(len(a))
    ax2.hlines(
        y,
        a.ari_weighted.clip(upper=a.mean_iou_weighted),
        a[["ari_weighted", "mean_iou_weighted"]].max(axis=1),
        color=st.RULE,
        linewidth=1,
    )
    ax2.plot(
        a.ari_weighted,
        y,
        "o",
        color=st.CENSUS,
        markersize=7,
        label="adjusted Rand index",
        markeredgecolor=st.CANVAS,
        markeredgewidth=1.2,
    )
    ax2.plot(
        a.mean_iou_weighted,
        y,
        "s",
        color=st.REFERENCE,
        markersize=7,
        label="mean IoU",
        markeredgecolor=st.CANVAS,
        markeredgewidth=1.2,
    )
    ax2.set_yticks(y, [f"{lab}   ({n} areas)" for lab, n in zip(a.label, a.n_candidate)])
    ax2.invert_yaxis()
    ax2.set_xlim(0.1, 0.8)
    ax2.grid(axis="y", visible=False)
    ax2.set_title(f"Agreement with {gold['uk_ttwa_official_touching_ew_2011']} official areas")
    ax2.legend(loc="upper left", bbox_to_anchor=(-0.75, -0.16), ncol=2)
    _foot(
        fig,
        "Official areas are assigned to MSOAs by plurality of LSOAs; "
        f"{gold['uk_msoa_cut_by_ttwa_2011'] / gold['uk_msoa_n_2011'] * 100:.1f} % of MSOAs are cut. ONS coding: home "
        "workers counted at their residence.",
    )
    _save(fig, "uk_trap3_agreement")


def uk_sweep() -> None:
    plt, gold = _plt(), _golden()
    grid, sw, pw = _tab("uk_sweep_counts.csv"), _tab("uk_sweep.csv"), _tab("uk_sweep_pairwise_ari.csv")
    cfg = params()["uk"]["sweep"]
    lo, hi = cfg["target_areas"] - cfg["target_tolerance"], cfg["target_areas"] + cfg["target_tolerance"]
    fig = plt.figure(figsize=(11.5, 5.2))
    _head(
        fig,
        "The same count of areas is reached by different rules, and the maps differ",
        f"England and Wales 2021. {gold['uk_sweep_near_core_settings']} core settings give {lo} to {hi} areas; "
        f"with three attachment thresholds each, {gold['uk_sweep_near_maps']} maps.",
    )
    ax = fig.add_axes([0.07, 0.15, 0.40, 0.62])
    ax.axhspan(lo, hi, color=st.RAMP["census"][1], zorder=0)
    qs = sorted(grid.core_quantile.unique())
    for i, q in enumerate(qs):
        g = grid[grid.core_quantile == q]
        ax.plot(g.merge_threshold, g.areas, color=st.INK2, linewidth=1.1, alpha=0.35 + 0.65 * i / (len(qs) - 1))
        ax.text(
            g.merge_threshold.iloc[-1] + 0.004,
            g.areas.iloc[-1],
            f"{q:g}",
            fontsize=7.8,
            family=st.MONO,
            color=st.INK2,
            va="center",
        )
    near = grid[(grid.areas >= lo) & (grid.areas <= hi)]
    ax.plot(
        near.merge_threshold,
        near.areas,
        "o",
        color=st.CENSUS,
        markersize=8,
        markeredgecolor=st.CANVAS,
        markeredgewidth=1.4,
        zorder=5,
    )
    ax.set_yscale("log")
    ax.set_yticks([60, 100, 235, 500, 1000], ["60", "100", "235", "500", "1,000"])
    ax.set_xlim(0.02, 0.335)
    ax.set_xlabel("core-merge threshold")
    ax.set_ylabel("number of areas (log scale)")
    ax.set_title("Areas by core quantile (line label) and merge threshold", fontsize=9.5)

    ax2 = fig.add_axes([0.57, 0.15, 0.40, 0.62])
    bins = np.linspace(0.40, 1.0, 13)
    same, other = pw[pw.same_cores].ari_weighted, pw[~pw.same_cores].ari_weighted
    ax2.hist(
        [other, same],
        bins=bins,
        stacked=True,
        color=[st.CENSUS, st.RAMP["census"][1]],
        rwidth=0.9,
        label=["different core setting", "same cores, different attachment"],
    )
    ax2.axvline(float(sw.ari_official.max()), color=st.REFERENCE, linewidth=1.2)
    ax2.text(
        float(sw.ari_official.max()) + 0.006,
        ax2.get_ylim()[1] * 0.97,
        f"best agreement with\nofficial areas {sw.ari_official.max():.2f}",
        fontsize=8.2,
        color=st.INK2,
        va="top",
    )
    ax2.set_xlabel("adjusted Rand index between two maps")
    ax2.set_ylabel("pairs of maps")
    ax2.grid(axis="x", visible=False)
    ax2.set_title(
        f"Agreement between the {gold['uk_sweep_near_maps']} maps, median {gold['uk_sweep_near_ari_median']:.2f}",
        fontsize=9.5,
        pad=26,
    )
    ax2.legend(loc="lower left", bbox_to_anchor=(-0.01, 0.995), ncol=2, columnspacing=1.2)
    _foot(
        fig,
        "Number of areas = number of core groups; the attachment threshold moves units between areas without "
        "changing the count. Agreement weighted by employed residents.",
    )
    _save(fig, "uk_trap3_sweep")


def _window(bounds, aspect: float, pad: float):
    """Expand a bounding box to the panel aspect (width / height) with padding in metres."""
    x0, y0, x1, y1 = bounds
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad
    if w / h < aspect:
        w = h * aspect
    else:
        h = w / aspect
    return cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


def uk_edge_cases() -> None:
    """Six cases of boundary divergence (selected by `pipeline.uk_cases`): one combined figure
    and one file per case for the slides."""
    import json
    import textwrap

    import geopandas as gpd

    from ..sources import uk_census as src

    plt, gold = _plt(), _golden()
    g, parts = _uk_layers(2021)
    lut = src.msoa_to_ttwa(2021).set_index("unit")
    tt = gpd.read_file(path("raw", params()["uk"]["ttwa_2011"])).to_crs(params()["uk"]["crs"])
    code = next(c for c in tt.columns if c.upper().startswith("TTWA11CD"))
    flows, fixed = parts["flows_only"], parts["contiguous"]
    geo = g.set_index("unit")
    cs = json.loads(path("tables", "uk_edge_cases.json").read_text(encoding="utf-8"))
    aspect = 1.45

    def draw(ax, win, labels, parent=None, hot=(), official=None, unit_outline=None, show_units=False):
        x0, x1, y0, y1 = win
        sub = g.cx[x0:x1, y0:y1]
        lab = labels[labels.index.isin(sub.unit)]
        _outline(ax, sub, lab, lw=0.6)
        if show_units:
            sub.boundary.plot(ax=ax, color=st.RULE, linewidth=0.3)
        if parent is not None:
            sel = sub[sub.unit.isin(lab[lab == parent].index)]
            if len(sel):
                sel.dissolve().plot(ax=ax, facecolor=st.RAMP["census"][2], edgecolor=st.INK2, linewidth=0.8)
        if len(hot):
            geo.loc[list(hot)].plot(ax=ax, facecolor=st.ARTEFACT, edgecolor=st.ARTEFACT, linewidth=0.8)
        if official is not None:
            tt.cx[x0:x1, y0:y1].boundary.plot(ax=ax, color=st.REFERENCE, linewidth=0.9)
            tt[tt[code].isin(official)].boundary.plot(ax=ax, color=st.INK, linewidth=2.0)
        if unit_outline is not None:
            geo.loc[[unit_outline]].plot(ax=ax, facecolor="none", edgecolor=st.ARTEFACT, linewidth=2.0, hatch="////")
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        for sp in ax.spines.values():
            sp.set_visible(True)

    at, isl = cs["attachment"], cs["island"]
    win12 = _window(geo.loc[at["units"] + [at["area"]]].total_bounds, aspect, 9_000)
    win3 = _window(geo.loc[isl["units"]].total_bounds, aspect, 14_000)
    u4 = list(lut[lut.ttwa == cs["swallowed"]["official"]].index)
    win4 = _window(geo.loc[u4].total_bounds, aspect, 12_000)
    u5 = list(lut[lut.ttwa == cs["split"]["official"]].index)
    win5 = _window(geo.loc[u5].total_bounds, aspect, 8_000)
    win6 = _window(geo.loc[[cs["cut_unit"]["unit"]]].total_bounds, aspect, 3_500)

    cases = [
        dict(
            key="1_attachment",
            title="1  Attachment without adjacency",
            note=f"{gold['uk_case_attach_units']} units with {gold['uk_case_attach_workers']:,.0f} employed "
            f"residents join the {gold['uk_case_attach_area']} area by flow. The nearest unit of that area is "
            f"{gold['uk_case_attach_distance_km']:.1f} km away, across water.",
            draw=lambda ax: draw(ax, win12, flows, parent=at["area"], hot=at["units"]),
        ),
        dict(
            key="2_repair",
            title="2  The same window after contiguity repair",
            note="The fragment goes to the adjacent area with the strongest flow across the shared border "
            f"(here the area around {gold['uk_case_attach_new_area']}).",
            draw=lambda ax: draw(ax, win12, fixed, parent=at["new_area"]),
        ),
        dict(
            key="3_island",
            title="3  An island the repair cannot place",
            note=f"{gold['uk_case_island_units']} units of {gold['uk_case_island_name']} touch no unit of another "
            "area. Polygons end at the shore; bridges are not adjacency.",
            draw=lambda ax: draw(ax, win3, fixed, parent=isl["area"], hot=isl["units"]),
        ),
        dict(
            key="4_swallowed",
            title=f"4  Official area inside a larger one: {gold['uk_case_swallowed_name']}",
            note="Black: official boundary. The matching delimited area (darker) holds "
            f"{1 - gold['uk_case_swallowed_omission']:.0%} of its employed residents and "
            f"{gold['uk_case_swallowed_commission']:.0%} of the match lies outside. "
            f"IoU {gold['uk_case_swallowed_iou']:.2f}.",
            draw=lambda ax: draw(
                ax, win4, fixed, parent=cs["swallowed"]["match"], official=[cs["swallowed"]["official"]]
            ),
        ),
        dict(
            key="5_split",
            title=f"5  Official area cut into {gold['uk_case_split_parts']}: {gold['uk_case_split_name']}",
            note="The best-matching delimited area (darker) holds "
            f"{1 - gold['uk_case_split_omission']:.0%} of its employed residents. "
            f"IoU {gold['uk_case_split_iou']:.2f}.",
            draw=lambda ax: draw(ax, win5, fixed, parent=cs["split"]["match"], official=[cs["split"]["official"]]),
        ),
        dict(
            key="6_cut_unit",
            title=f"6  A unit the official boundary cuts: {gold['uk_case_cut_name']}",
            note=f"Official areas are built from smaller blocks. {gold['uk_case_cut_share']:.0%} of this unit's "
            f"blocks lie in its plurality area; {gold['uk_msoa_cut_by_ttwa_2021']} of {gold['uk_msoa_n']:,} units "
            "are cut this way.",
            draw=lambda ax: draw(
                ax,
                win6,
                fixed,
                official=[cs["cut_unit"]["official"]],
                unit_outline=cs["cut_unit"]["unit"],
                show_units=True,
            ),
        ),
    ]

    fig = plt.figure(figsize=(13.0, 8.4))
    _head(
        fig,
        "Where the boundaries diverge: six cases",
        "England and Wales 2021. Light amber: delimited areas. Darker: the area in question. Red: the units in "
        "question. Black and grey lines: official TTWA 2011.",
    )
    for i, c in enumerate(cases):
        col, row = i % 3, i // 3
        ax = fig.add_axes([0.03 + 0.325 * col, 0.535 - 0.415 * row, 0.30, 0.30])
        c["draw"](ax)
        ax.set_title(c["title"], fontsize=9.5)
        ax.text(
            0.0,
            -0.03,
            "\n".join(textwrap.wrap(c["note"], 74)),
            transform=ax.transAxes,
            fontsize=8,
            color=st.INK2,
            va="top",
            linespacing=1.3,
        )
    _foot(fig, st.ATTRIBUTION["ons"] + ". MSOA 2021 BGC; TTWA 2011 super-generalised boundaries; EPSG:27700.")
    _save(fig, "uk_edge_cases", vector=False)

    for c in cases:
        f = plt.figure(figsize=(7.4, 5.1))
        ax = f.add_axes([0.0, 0.0, 1.0, 1.0])
        c["draw"](ax)
        for sp in ax.spines.values():
            sp.set_visible(False)
        _save(f, f"uk_edge_case_{c['key']}", vector=False, bare=False)


# ------------------------------------------------------------------ Serbia
def rs_maps() -> None:
    import geopandas as gpd
    from matplotlib.colors import Normalize, TwoSlopeNorm

    plt, gold = _plt(), _golden()
    j = gpd.read_parquet(path("interim", "rs_municipalities.parquet")).to_crs(params()["serbia"]["crs"])
    single = j.single_settlement.astype(bool)
    fig = plt.figure(figsize=(11.5, 7.2))
    _head(
        fig,
        "Bands instead of pairs: self-containment is computable, delimitation is not",
        f"Serbia, Census 2022, {gold['rs_municipalities']} municipalities, "
        f"{gold['rs_workers']:,.0f} daily migrant workers.",
    )
    ax = fig.add_axes([0.02, 0.11, 0.42, 0.70])
    _map_axes(ax)
    cm = st.cmap("census")
    j[~single].plot(ax=ax, column="sc", cmap=cm, vmin=0, vmax=1, edgecolor=st.CANVAS, linewidth=0.3)
    j[single].plot(ax=ax, facecolor=st.CANVAS, edgecolor=st.ARTEFACT, linewidth=1.0, hatch="//////")
    ax.set_title("Work: share of daily migrants staying in their municipality", fontsize=10)
    cax = fig.add_axes([0.445, 0.25, 0.010, 0.42])
    fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(0, 1), cmap=cm), cax=cax).outline.set_edgecolor(st.RULE)

    ax2 = fig.add_axes([0.52, 0.11, 0.42, 0.70])
    _map_axes(ax2)
    lim = float(j.loc[~single, "gap"].abs().quantile(0.97))
    norm = TwoSlopeNorm(vmin=-lim, vcenter=0.0, vmax=lim)
    j[~single].plot(ax=ax2, column="gap", cmap=st.diverging(), norm=norm, edgecolor=st.CANVAS, linewidth=0.3)
    j[single].plot(ax=ax2, facecolor=st.CANVAS, edgecolor=st.ARTEFACT, linewidth=1.0, hatch="//////")
    ax2.set_title("Education minus work: amber = education is more local", fontsize=10)
    cax2 = fig.add_axes([0.945, 0.25, 0.010, 0.42])
    fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=st.diverging()), cax=cax2).outline.set_edgecolor(st.RULE)
    fig.text(
        0.04,
        0.075,
        f"Hatched, red outline: {gold['rs_single_settlement']} municipalities made of one settlement. "
        "A daily migrant leaves the settlement, so their value is 0 by definition.",
        fontsize=8.5,
        color=st.INK2,
    )
    _foot(
        fig,
        st.ATTRIBUTION["sors"]
        + ". EPSG:32634. Pupils and students are published as one number.\n"
        + st.KOSOVO_FOOTNOTE,
    )
    _save(fig, "rs_self_containment", vector=False)


def rs_urbanisation() -> None:
    plt, gold = _plt(), _golden()
    d = _tab("rs_municipalities.csv")
    d = d[(~d.single_settlement.astype(bool)) & (~d.clipped.astype(bool)) & (d.pop_ghsl > 0)]
    fig = plt.figure(figsize=(10.5, 5.0))
    _head(
        fig,
        "Weight urbanisation by people, not by pixels",
        f"Work self-containment of {len(d)} Serbian municipalities against two measures of the same thing.",
    )
    for i, (col, title, r, rho, c) in enumerate(
        [
            (
                "area_urb",
                "Share of AREA in urban classes",
                gold["rs_r_sc_urb_area"],
                gold["rs_rho_sc_urb_area"],
                st.ARTEFACT,
            ),
            (
                "deg_urb",
                "Share of POPULATION in urban classes",
                gold["rs_r_sc_urb_pop"],
                gold["rs_rho_sc_urb_pop"],
                st.EUROSTAT,
            ),
        ]
    ):
        ax = fig.add_axes([0.07 + 0.49 * i, 0.14, 0.41, 0.64])
        ax.plot(d[col], d.sc, "o", color=c, markersize=5.5, alpha=0.75, markeredgecolor=st.CANVAS, markeredgewidth=0.8)
        ax.set_xlim(-0.03, 1.03)
        ax.set_ylim(0, 1)
        ax.set_xlabel(title.lower())
        ax.set_ylabel("work self-containment")
        ax.set_title(title)
        ax.text(
            0.97,
            0.95,
            f"Pearson r = {r:+.2f}\nSpearman rho = {rho:+.2f}\nmedian x = {d[col].median():.3f}",
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=8.8,
            family=st.MONO,
            color=st.INK,
        )
    _foot(fig, st.ATTRIBUTION["ghsl"] + ", epoch 2030 projection, classes 21 to 30. " + st.ATTRIBUTION["sors"] + ".")
    _save(fig, "rs_urbanisation_weighting")


# ------------------------------------------------------------------ Netherlands
def nl_corop() -> None:
    plt, gold = _plt(), _golden()
    d = _tab("nl_corop.csv").sort_values("sc_supply").reset_index(drop=True)
    d["label"] = d.name.str.replace(" (CR)", "", regex=False)
    fig = plt.figure(figsize=(10.5, 7.6))
    _head(
        fig,
        "Pairs exist, aggregated to the answer",
        f"Netherlands, register jobs December 2014, {len(d)} COROP regions designed in 1970 as nodal regions. "
        f"{int((d.sc_supply >= 0.75).sum())} of {len(d)} still hold 75 % of their employed residents.",
    )
    ax = fig.add_axes([0.30, 0.08, 0.66, 0.78])
    y = np.arange(len(d))
    ok = d.sc_supply >= params()["netherlands"]["pass_threshold"]
    ax.hlines(y, 0, d.sc_supply, color=np.where(ok, st.CENSUS, st.RAMP["census"][2]), linewidth=5)
    ax.plot(d.sc_demand, y, "|", color=st.INK2, markersize=7, markeredgewidth=1.4, label="demand side (jobs)")
    ax.axvline(0.75, color=st.INK2, linewidth=1)
    ax.text(0.752, len(d) - 0.2, "0.75", fontsize=8.5, family=st.MONO, color=st.INK2, va="bottom")
    ax.set_yticks(y, d.label, fontsize=8)
    ax.set_ylim(-0.8, len(d) + 0.6)
    ax.set_xlim(0, 1)
    ax.set_xlabel("self-containment (bar: employed residents working in their own region)")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right")
    for i in (0, len(d) - 1):
        ax.text(d.sc_supply[i] + 0.012, i, f"{d.sc_supply[i]:.2f}", va="center", fontsize=8.5, family=st.MONO)
    _foot(
        fig,
        st.ATTRIBUTION["cbs"] + f". {gold['nl_jobs_2014'] / 1e6:.2f} M jobs. Delimitation on these 40 nodes returns "
        f"{gold['nl_areas']} areas: an effect of the resolution, not a finding.",
    )
    _save(fig, "nl_corop_self_containment")


def nl_2023_maps() -> None:
    from ..sources import nl_cbs as src

    plt, gold = _plt(), _golden()
    g = src.load_boundaries("gemeente_gegeneraliseerd", params()["netherlands"]["municipal"]["year"])
    cp = src.load_boundaries("coropgebied_gegeneraliseerd", params()["netherlands"]["municipal"]["year"])
    own = pd.read_csv(path("tables", "nl_2023_areas_contiguous.csv"), dtype=str).set_index("unit").area
    d = pd.read_csv(path("tables", "nl_2023_areas_lma.csv"), dtype=str)
    lma = pd.Series(d.area.to_numpy(), index=d.unit.to_numpy())
    fig = plt.figure(figsize=(12.0, 6.4))
    _head(
        fig,
        "Do the regions of 1970 still hold their commuters?",
        "Netherlands, employee jobs by municipality of residence and of work, December 2023. Shades: delimited "
        "areas. Dark lines: the 40 COROP regions.",
    )
    panels = [
        (lma, f"Coombes-Bond: {gold['nl23_lma_areas']} areas, ARI with COROP {gold['nl23_ari_lma_corop']:.2f}"),
        (own, f"Two-rule heuristic: {gold['nl23_own_areas']} areas, ARI {gold['nl23_ari_own_corop']:.2f}"),
        (None, f"COROP regions: {gold['nl23_corop_pass'] * 100:.0f} % hold 75 % of residents' jobs"),
    ]
    for i, (lab, title) in enumerate(panels):
        ax = fig.add_axes([0.01 + 0.33 * i, 0.10, 0.32, 0.70])
        _map_axes(ax)
        if lab is not None:
            _outline(ax, g, lab, lw=0.5, color=st.CANVAS, tint=AREA_TINTS)
            cp.boundary.plot(ax=ax, color=st.INK, linewidth=0.9)
        else:
            cp.plot(ax=ax, facecolor=st.SURFACE, edgecolor=st.REFERENCE, linewidth=0.6)
        ax.set_title(title, fontsize=9.5)
    _foot(
        fig,
        st.ATTRIBUTION["cbs"].replace("81252NED", "85481NED") + "; boundaries CBS/PDOK 2023. Jobs are rounded to "
        "the nearest 100 per pair; the place of work is modelled by CBS.",
    )
    _save(fig, "nl_2023_maps", vector=False)


def es_maps() -> None:
    from ..sources import es_mitma as src

    plt, gold = _plt(), _golden()
    g = src.load_districts()
    own = pd.read_csv(path("tables", "es_2023_areas_contiguous.csv"), dtype=str).set_index("unit").area
    d = pd.read_csv(path("tables", "es_2023_areas_lma.csv"), dtype=str)
    lma = pd.Series(d.area.to_numpy(), index=d.unit.to_numpy())
    spain = g[g.unit.str.match(r"^[0-9]")]  # the NUTS-3 regions of France and Portugal are not drawn
    mainland = spain.cx[-50_000:1_200_000, 3_900_000:4_900_000]
    fig = plt.figure(figsize=(12.0, 6.2))
    _head(
        fig,
        "Spain: the same two methods on operator data",
        f"Trips from home to work or study, mean of {gold['es_days']} weekdays, October 2023, "
        f"{gold['es_zones_spain']:,} districts. Grey: districts in no area.",
    )
    for i, (lab, title) in enumerate(
        [
            (lma, f"Coombes-Bond: {gold['es_lma_areas']} areas"),
            (own, f"Two-rule heuristic: {gold['es_own_areas']} areas"),
        ]
    ):
        ax = fig.add_axes([0.02 + 0.49 * i, 0.09, 0.47, 0.72])
        _map_axes(ax)
        mainland.plot(ax=ax, facecolor=st.RULE, edgecolor=st.RULE, linewidth=0.15)
        _outline(ax, mainland, lab, lw=0.3, color=st.CANVAS, tint=AREA_TINTS_BLUE)
        ax.set_title(title, fontsize=10)
    _foot(
        fig,
        "Basado en datos abiertos Ministerio de Transportes y Movilidad Sostenible (transportes.gob.es); mobile "
        f"network data of Orange España. Mainland and Balearic Islands. Agreement of the two maps: ARI "
        f"{gold['es_ari_own_lma']:.2f}.",
    )
    _save(fig, "es_maps", vector=False)


def es_hourly() -> None:
    plt, gold = _plt(), _golden()
    h = _tab("es_hourly.csv").set_index("periodo")
    pairs = [
        ("casa > trabajo_estudio", "home to work or study", st.RAMP["eurostat"][3], "-"),
        ("trabajo_estudio > casa", "work or study to home", st.RAMP["eurostat"][4], "--"),
        ("casa > frecuente", "home to other frequent place", st.RAMP["eurostat"][2], "-"),
        ("frecuente > casa", "other frequent place to home", st.RAMP["eurostat"][2], "--"),
    ]
    fig = plt.figure(figsize=(10.5, 4.8))
    _head(
        fig,
        "Pairs, purpose and the hour in one open file",
        f"Spain, trips by hour of departure and activity at both ends, mean of {gold['es_days']} weekdays, "
        "October 2023, millions.",
    )
    ax = fig.add_axes([0.08, 0.14, 0.62, 0.64])
    for col, label, colour, ls in pairs:
        if col in h:
            ax.plot(h.index, h[col] / 1e6, color=colour, linestyle=ls, label=label)
    ax.set_xticks(range(0, 24, 3), [f"{x:02d}:00" for x in range(0, 24, 3)])
    ax.set_xlim(0, 23)
    ax.set_ylabel("trips per hour, millions")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0))
    fig.text(
        0.73,
        0.40,
        f"{gold['es_commute_share_6_9'] * 100:.0f} % of trips from home to work\nor study start between "
        f"06:00 and 09:59;\npeak at {gold['es_commute_peak_hour']:02d}:00",
        fontsize=9,
        color=st.INK2,
    )
    _foot(fig, "Basado en datos abiertos Ministerio de Transportes y Movilidad Sostenible (transportes.gob.es).")
    _save(fig, "es_hourly")


# ------------------------------------------------------------------ Japan
def jp_daynight() -> None:
    from matplotlib.colors import LogNorm, TwoSlopeNorm

    plt, gold = _plt(), _golden()
    p = _tab("jp_daynight_cells.csv")
    w = params()["japan"]["map_window"]
    v = p[p.lon_center.between(w[0], w[1]) & p.lat_center.between(w[2], w[3])]
    fig = plt.figure(figsize=(12.0, 6.6))
    _head(
        fig,
        "The axis no census has: time of day",
        "Hiroshima agglomeration, weekday, October 2019, 1 km mesh. Presence, not trips.",
    )
    asp = 1 / np.cos(np.radians(34.4))
    ax = fig.add_axes([0.03, 0.12, 0.42, 0.70])
    ax2 = fig.add_axes([0.52, 0.12, 0.42, 0.70])
    for a in (ax, ax2):
        a.set_aspect(asp)
        a.set_xticks([])
        a.set_yticks([])
        a.grid(False)
        for s in a.spines.values():
            s.set_visible(True)
    s1 = ax.scatter(
        v.lon_center,
        v.lat_center,
        c=v.night,
        cmap=st.cmap("eurostat"),
        norm=LogNorm(10, float(v.night.max())),
        s=13,
        marker="s",
        linewidths=0,
    )
    ax.set_title("Night presence, people per cell", fontsize=10)
    fig.colorbar(s1, cax=fig.add_axes([0.455, 0.22, 0.010, 0.50])).outline.set_edgecolor(st.RULE)
    lim = np.log2(gold["jp_ratio_max"])
    s2 = ax2.scatter(
        v.lon_center,
        v.lat_center,
        c=np.log2(v.ratio),
        cmap=st.diverging(),
        norm=TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim),
        s=13,
        marker="s",
        linewidths=0,
    )
    ax2.set_title("Day / night ratio: amber = more people by day", fontsize=10)
    cb = fig.colorbar(s2, cax=fig.add_axes([0.945, 0.22, 0.010, 0.50]), ticks=[-lim, -1, 0, 1, lim])
    cb.ax.set_yticklabels([f"x{2**-lim:.2f}", "x0.5", "x1", "x2", f"x{2**lim:.1f}"])
    cb.outline.set_edgecolor(st.RULE)
    ax2.annotate(
        "Naka-ku",
        xy=(132.455, 34.390),
        xytext=(132.60, 34.30),
        fontsize=9,
        color=st.INK,
        arrowprops=dict(arrowstyle="-", color=st.INK2, lw=0.8),
    )
    fig.text(
        0.04,
        0.075,
        f"Naka-ku, weekday daytime: {gold['jp_local_share_ward']:.0%} of presence is by residents "
        f"of the ward; at night {gold['jp_local_share_ward_night']:.0%}.",
        fontsize=9,
        color=st.INK2,
    )
    _foot(
        fig,
        st.ATTRIBUTION["mlit"] + ". JIS X 0410 mesh. Cells under 10 people are not published. Volumes are "
        "normalised: compare composition, not totals. Colour scale clipped at the 97th percentile.",
    )
    _save(fig, "jp_day_night", vector=False)


def jp_signatures() -> None:
    from matplotlib.lines import Line2D

    plt, gold = _plt(), _golden()
    sg = params()["japan"]["signatures"]
    m = _tab("jp_signatures.csv")
    t = np.log2(sg["threshold_ratio"])
    shade = {
        "mixed": st.RULE,
        "residential": st.RAMP["eurostat"][4],
        "office": st.RAMP["eurostat"][3],
        "leisure": st.RAMP["eurostat"][2],
    }
    mark = {"mixed": "o", "residential": "v", "office": "s", "leisure": "^"}
    names = {
        "mixed": "mixed",
        "residential": "residential (night dominant)",
        "office": "office (weekday day dominant)",
        "leisure": "leisure (holiday day dominant)",
    }
    fig = plt.figure(figsize=(12.0, 6.4))
    _head(
        fig,
        "One cloud, four declared classes",
        f"Hiroshima prefecture, 2019 monthly mean, {gold['jp_profile_cells']:,} cells with a full profile. "
        "The thresholds are stated, not found.",
    )
    ax = fig.add_axes([0.06, 0.21, 0.40, 0.60])
    for k in ("mixed", "residential", "office", "leisure"):
        s = m[m.signature == k]
        ax.scatter(s.x, s.y, s=9, c=shade[k], marker=mark[k], linewidths=0, alpha=0.75)
    for x in (-t, t):
        ax.axvline(x, color=st.INK2, linewidth=0.9)
    ax.axhline(t, color=st.INK2, linewidth=0.9)
    ax.set_xlim(-3.4, 3.4)
    ax.set_ylim(-2.4, 3.0)
    ax.set_xlabel("log2 (weekday day / weekday night)")
    ax.set_ylabel("log2 (holiday day / weekday day)")
    ax.set_title("The continuum, with the 1.5x thresholds")
    for x, y, lab in [(2.35, -2.1, "office"), (-2.35, -2.1, "residential"), (0, 2.7, "leisure"), (0, -2.1, "mixed")]:
        ax.text(x, y, lab, ha="center", fontsize=9, color=st.INK2)

    ax2 = fig.add_axes([0.52, 0.27, 0.46, 0.54])
    w = params()["japan"]["city_window"]
    v = m[m.in_window & (m.volume >= sg["min_people_per_cell"])]
    ax2.set_aspect(1 / np.cos(np.radians(34.4)))
    for k in ("mixed", "residential", "office", "leisure"):
        s = v[v.signature == k]
        ax2.scatter(s.lon_center, s.lat_center, c=shade[k], marker="s", s=58, linewidths=0)
    ax2.set_xlim(w[0], w[1])
    ax2.set_ylim(w[2], w[3])
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.grid(False)
    ax2.set_title(f"Central Hiroshima window, {gold['jp_sig_cells']} cells with profile volume of 100 or more")
    handles = [
        Line2D(
            [],
            [],
            marker=mark[k],
            linestyle="",
            color=shade[k],
            markersize=7,
            label=f"{names[k]}: {gold[f'jp_sig_{k}']}",
        )
        for k in ("office", "residential", "leisure", "mixed")
    ]
    ax2.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, -0.03), ncol=2, columnspacing=1.5)
    fig.text(
        0.06,
        0.085,
        f"HDBSCAN on composition profiles: all noise at "
        f"{gold['jp_hdbscan_comp_all_noise_settings']} of {gold['jp_hdbscan_settings']} settings. "
        f"k-means with k = 4: silhouette {gold['jp_kmeans4_silhouette']:.2f}.",
        fontsize=9,
        color=st.INK2,
    )
    _foot(fig, st.ATTRIBUTION["mlit"] + ". First rule that fires wins, in the order office, leisure, residential.")
    _save(fig, "jp_signatures", vector=False)


def jp_clusterability() -> None:
    plt = _plt()
    hs, hc, th = _tab("jp_hdbscan_sweep.csv"), _tab("jp_hdbscan_sweep_composition.csv"), _tab("jp_threshold_sweep.csv")
    fig = plt.figure(figsize=(11.5, 4.8))
    _head(
        fig,
        "Clustering does not return classes; thresholds return whatever share you ask for",
        "Left and centre: share of cells HDBSCAN labels as noise. Right: class shares under four threshold ratios.",
    )
    for i, (d, title) in enumerate([(hc, "HDBSCAN, 4-slot composition"), (hs, "HDBSCAN, two log-ratio axes")]):
        ax = fig.add_axes([0.06 + 0.29 * i, 0.16, 0.22, 0.60])
        pv = d.pivot(index="min_samples", columns="min_cluster_size", values="noise_share")
        k = d.pivot(index="min_samples", columns="min_cluster_size", values="n_clusters")
        ax.imshow(pv.to_numpy(), cmap=st.cmap("eurostat"), vmin=0, vmax=1, aspect="auto", origin="lower")
        for a in range(pv.shape[0]):
            for b in range(pv.shape[1]):
                val = pv.to_numpy()[a, b]
                ax.text(
                    b,
                    a,
                    f"{val:.2f}\n{int(k.to_numpy()[a, b])} cl.",
                    ha="center",
                    va="center",
                    fontsize=7.8,
                    family=st.MONO,
                    color="white" if val > 0.45 else st.INK,
                )
        ax.set_xticks(range(pv.shape[1]), pv.columns)
        ax.set_yticks(range(pv.shape[0]), pv.index)
        ax.set_xlabel("min_cluster_size")
        ax.set_ylabel("min_samples")
        ax.grid(False)
        ax.set_title(title, fontsize=9.5)
    ax = fig.add_axes([0.68, 0.16, 0.29, 0.60])
    tot = th[["office", "residential", "leisure", "mixed"]].sum(axis=1)
    left = np.zeros(len(th))
    tone = {
        "office": st.RAMP["eurostat"][3],
        "residential": st.RAMP["eurostat"][4],
        "leisure": st.RAMP["eurostat"][2],
        "mixed": st.RULE,
    }
    for k in ("office", "residential", "leisure", "mixed"):
        w = (th[k] / tot).to_numpy()
        ax.barh(range(len(th)), w - 0.006, left=left, height=0.5, color=tone[k], label=k)
        for j, (l0, ww) in enumerate(zip(left, w)):
            if ww > 0.09:
                ax.text(
                    l0 + ww / 2,
                    j,
                    f"{ww:.0%}",
                    ha="center",
                    va="center",
                    fontsize=8,
                    family=st.MONO,
                    color="white" if k in ("office", "residential") else st.INK,
                )
        left += w
    ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=4, handlelength=1.0, columnspacing=1.0, fontsize=8)
    ax.set_yticks(range(len(th)), [f"{r:g}x" for r in th.threshold_ratio])
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, len(th) - 0.5)
    ax.set_xlabel("share of cells")
    ax.set_ylabel("threshold ratio")
    ax.grid(False)
    ax.set_title("Class shares by threshold", fontsize=9.5, pad=24)
    _foot(fig, st.ATTRIBUTION["mlit"] + ". scikit-learn HDBSCAN, Euclidean distance.")
    _save(fig, "jp_clusterability")


# ------------------------------------------------------------------ OSM traces
def osm_traces() -> None:
    """Sample size of the trace windows. The rank comparison of version 1 is not drawn (11 shared cells)."""
    plt = _plt()
    d = _tab("osm_summary.csv")
    names = {"hiroshima_centre": "Hiroshima", "belgrade_centre": "Belgrade", "london_soho": "London (Soho)"}
    fig = plt.figure(figsize=(10.5, 4.6))
    _head(
        fig,
        "200,000 points, a few thousand minutes",
        "OSM public GPS traces in three city-centre windows. The point count is the download cap; the sample "
        "is the number of distinct minutes.",
    )
    ax = fig.add_axes([0.13, 0.17, 0.40, 0.58])
    y = np.arange(len(d))
    ax.barh(y, d.points, height=0.26, color=st.RAMP["osm"][1])
    ax.barh(y, d.unique_minutes, height=0.26, color=st.OSM)
    for i, r in enumerate(d.itertuples()):
        ax.text(
            0,
            i - 0.30,
            f"{r.unique_minutes:,} minutes in {r.points:,} points",
            va="center",
            fontsize=8.3,
            family=st.MONO,
            color=st.INK,
        )
    ax.set_yticks(y, [names[w] for w in d.window])
    ax.set_ylim(len(d) - 0.5, -0.6)
    ax.set_xlim(0, 215_000)
    ax.set_xticks([0, 100_000, 200_000], ["0", "100k", "200k"])
    ax.grid(axis="y", visible=False)
    ax.set_title("Distinct minutes (dark) inside the points (light)", fontsize=9.5)

    ax2 = fig.add_axes([0.62, 0.17, 0.33, 0.58])
    ax2.barh(y, d.top_cell_share, height=0.26, color=st.OSM)
    for i, r in enumerate(d.itertuples()):
        ax2.text(
            0,
            i - 0.30,
            f"{r.top_cell_share:.0%}, median year {r.median_year}",
            va="center",
            fontsize=8.3,
            family=st.MONO,
        )
    ax2.set_yticks(y, [])
    ax2.set_ylim(len(d) - 0.5, -0.6)
    ax2.set_xlim(0, 1.0)
    ax2.set_xticks([0, 0.5, 1.0], ["0", "50 %", "100 %"])
    ax2.grid(axis="y", visible=False)
    ax2.set_title("Share of points in the busiest H3 cell", fontsize=9.5)
    _foot(fig, st.ATTRIBUTION["osm"] + ". H3 resolution 8.")
    _save(fig, "osm_traces")


FIGURES = [
    uk_trap1,
    uk_null_model,
    uk_decomposition,
    uk_areas_map,
    uk_ttwa_triptych,
    uk_iou,
    uk_sweep,
    uk_edge_cases,
    rs_maps,
    rs_urbanisation,
    nl_corop,
    nl_2023_maps,
    es_maps,
    es_hourly,
    jp_daynight,
    jp_signatures,
    jp_clusterability,
    osm_traces,
]


def all_figures(only: list[str] | None = None) -> None:
    for f in FIGURES:
        if only is None or f.__name__ in only:
            f()
