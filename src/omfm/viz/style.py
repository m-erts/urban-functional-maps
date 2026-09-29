"""Figure style: Swiss Civic Lab (see DESIGN.md).

Paper-white canvas, 1 px rules, no shadows, no gradients as decoration. Colour carries the
data source: Eurostat-type grid and presence statistics are blue, OpenStreetMap is green,
census and register counts are amber. Text is always ink; identity never rests on colour alone
(the OSM-green / census-amber pair separates at only dE 6.5 under protanopia, so every chart
that shows both also labels or shapes them).
"""

from __future__ import annotations

CANVAS, SURFACE, RULE, GRID = "#F8FAFC", "#F1F5F9", "#CBD5E1", "#E2E8F0"
INK, INK2, MUTED = "#0F172A", "#334155", "#64748B"

EUROSTAT, OSM, CENSUS = "#1D4ED8", "#15803D", "#D97706"
REFERENCE = "#475569"  # official boundaries, reference layers
ARTEFACT = "#B91C1C"  # things that are wrong: cut-off fragments, structural zeros
SOURCE = {"eurostat": EUROSTAT, "osm": OSM, "census": CENSUS, "reference": REFERENCE}

# one hue per source, light -> dark
RAMP = {
    "census": ["#FEF3C7", "#FDE68A", "#FBBF24", "#D97706", "#92400E", "#451A03"],
    "eurostat": ["#DBEAFE", "#BFDBFE", "#60A5FA", "#1D4ED8", "#1E3A8A", "#0B1B4D"],
    "osm": ["#DCFCE7", "#BBF7D0", "#4ADE80", "#15803D", "#14532D", "#052E16"],
}
# two poles and a neutral grey midpoint; blue / amber stays readable under deuteranopia
DIVERGING = ["#1E3A8A", "#1D4ED8", "#93C5FD", "#E2E8F0", "#FCD34D", "#D97706", "#78350F"]
AREA_TINTS = ["#FFFBEB", "#FEF3C7", "#FDE68A", "#FCD34D", "#FBBF24", "#F59E0B"]

SANS = ["Inter", "Helvetica Neue", "Arial", "Hiragino Sans", "DejaVu Sans"]
MONO = ["JetBrains Mono", "IBM Plex Mono", "Menlo", "DejaVu Sans Mono"]

ATTRIBUTION = {
    "osm": "© OpenStreetMap contributors (ODbL)",
    "overture": "Overture Maps Foundation, release 2026-07-22.0 (CDLA-Permissive-2.0 and source licences)",
    "ons": "Source: Office for National Statistics, Census 2011 and 2021; boundaries ONS Open Geography (OGL v3)",
    "sors": "Source: Statistical Office of the Republic of Serbia, Census 2022; boundaries GeoSrbija. "
    "The census does not cover Kosovo*",
    "cbs": "Source: CBS StatLine 81252NED (CC BY 4.0)",
    "mlit": "Source: MLIT nationwide people-flow open data (Agoop app-GPS panel, expanded to population)",
    "ghsl": "GHS-POP and GHS-SMOD R2023A, European Commission JRC (CC BY 4.0)",
}
KOSOVO_FOOTNOTE = (
    "* This designation is without prejudice to positions on status, and is in line with "
    "UNSCR 1244/1999 and the ICJ Opinion on the Kosovo declaration of independence."
)


def cmap(source: str):
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(f"scl_{source}", RAMP[source])


def diverging():
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list("scl_div", DIVERGING)


def apply() -> None:
    import matplotlib as mpl

    mpl.rcParams.update(
        {
            "figure.facecolor": CANVAS,
            "axes.facecolor": CANVAS,
            "savefig.facecolor": CANVAS,
            "axes.edgecolor": RULE,
            "axes.linewidth": 0.8,
            "axes.labelcolor": INK2,
            "axes.titlecolor": INK,
            "axes.titlesize": 10.5,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.titlepad": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.axisbelow": True,
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.7,
            "grid.linestyle": "-",
            "text.color": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelcolor": INK2,
            "ytick.labelcolor": INK2,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "xtick.major.width": 0.8,
            "ytick.major.width": 0.8,
            "xtick.major.size": 3,
            "ytick.major.size": 3,
            "font.family": SANS,
            "font.size": 9,
            "axes.labelsize": 9,
            "legend.frameon": False,
            "legend.fontsize": 8.5,
            "lines.linewidth": 2.0,
            "lines.solid_capstyle": "round",
            "hatch.linewidth": 0.6,
            "savefig.dpi": 200,
            "figure.dpi": 100,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
        }
    )
