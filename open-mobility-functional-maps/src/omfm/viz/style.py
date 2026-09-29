"""Shared figure style — matches the v1 deck (dark purple theme) but colour-blind safe."""
DECK = {
    "bg": "#1B1233",      # TODO sample exact value from pptx theme
    "fg": "#FFFFFF",
    "muted": "#9A8FB8",
    "cyan": "#4FD8E0",
    "purple": "#B07CF0",
    "yellow": "#FFD166",
    "coral": "#FF6B6B",
    "green": "#3DD68C",
}
DIVERGING = "PuOr"   # replaces red/green on the Serbia gap map (deuteranopia-safe)
SEQUENTIAL = "magma"
ATTRIBUTION = {
    "osm": "© OpenStreetMap contributors (ODbL)",
    "overture": "Overture Maps Foundation (CDLA-Permissive-2.0 + source attributions)",
    "ons": "Source: ONS, Census 2021/2011 — OGL v3",
    "sors": "Source: SORS, Popis 2022 · Kosovo* not covered by the census",
    "cbs": "Source: CBS StatLine (CC BY 4.0)",
    "mlit": "Source: MLIT 全国の人流オープンデータ (Agoop) — 政府標準利用規約",
    "ghsl": "GHSL, European Commission JRC (CC BY 4.0)",
}
KOSOVO_FOOTNOTE = ("*This designation is without prejudice to positions on status, and is in line with "
                   "UNSCR 1244/1999 and the ICJ Opinion on the Kosovo declaration of independence.")


def apply():
    import matplotlib as mpl

    mpl.rcParams.update({"figure.facecolor": DECK["bg"], "axes.facecolor": DECK["bg"],
                         "text.color": DECK["fg"], "axes.labelcolor": DECK["fg"],
                         "xtick.color": DECK["muted"], "ytick.color": DECK["muted"],
                         "font.family": "Arial", "savefig.dpi": 200})
