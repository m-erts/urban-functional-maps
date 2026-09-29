"""Join the Serbian census to GeoSrbija municipal polygons whose attribute encoding is broken.

In ``Op_tina.shp`` the Cyrillic name field is all question marks and the Latin field has every
non-ASCII letter replaced by one: ``ARAN?ELOVAC``, ``VRA?AR``, ``?AKOVICA``. The join therefore
treats "?" as a one-character wildcard, and that is dangerous: ``.AKOVICA`` matches both
ĐAKOVICA and RAKOVICA. In the first version of the map a polygon of 587 km2 outside the census
territory carried the values of the Belgrade municipality Rakovica.

Rules enforced here:
  1. exact matches are resolved first; wildcards see only the remainder;
  2. a wildcard match is accepted only if it is unique;
  3. polygons outside the census territory (register codes starting with 9) are dropped before
     matching. The 2022 census does not cover Kosovo*;
  4. the result must be a bijection: one municipality, one polygon.

* This designation is without prejudice to positions on status, and is in line with
  UNSCR 1244/1999 and the ICJ Opinion on the Kosovo declaration of independence.
"""

from __future__ import annotations

import re

import pandas as pd

__all__ = ["cyr_to_ascii", "load_municipalities", "join_census", "NOT_COVERED_PREFIX"]

NOT_COVERED_PREFIX = "9"

# Serbian Cyrillic -> ASCII. The digraphs Љ, Њ, Џ give TWO letters.
_CYR = {
    "А": "A",
    "Б": "B",
    "В": "V",
    "Г": "G",
    "Д": "D",
    "Ђ": "D",
    "Е": "E",
    "Ж": "Z",
    "З": "Z",
    "И": "I",
    "Ј": "J",
    "К": "K",
    "Л": "L",
    "Љ": "LJ",
    "М": "M",
    "Н": "N",
    "Њ": "NJ",
    "О": "O",
    "П": "P",
    "Р": "R",
    "С": "S",
    "Т": "T",
    "Ћ": "C",
    "У": "U",
    "Ф": "F",
    "Х": "H",
    "Ц": "C",
    "Ч": "C",
    "Џ": "DZ",
    "Ш": "S",
}


def cyr_to_ascii(s: str) -> str:
    """Cyrillic -> bare upper-case ASCII letters."""
    return re.sub(r"[^A-Z]", "", "".join(_CYR.get(c, c) for c in str(s).upper()))


def _split_qualifier(s: str) -> tuple[str, str]:
    """``PALILULA (BEOGRAD)`` -> (``PALILULA``, ``BEOGRAD``)."""
    s = str(s).upper()
    q = re.search(r"\(([^)]*)\)", s)
    base = re.sub(r"\([^)]*\)", "", s)
    return re.sub(r"[^A-Z?]", "", base), re.sub(r"[^A-Z?]", "", q.group(1)) if q else ""


def load_municipalities(shp_path, drop_not_covered: bool = True):
    """Read the polygons; add ``key_lat`` (name with wildcards) and ``qual`` (qualifier)."""
    import geopandas as gpd

    g = gpd.read_file(shp_path)
    g[["key_lat", "qual"]] = g.opstina__1.apply(lambda s: pd.Series(_split_qualifier(s)))
    if drop_not_covered:
        g = g[~g.opstina_ma.astype(str).str.startswith(NOT_COVERED_PREFIX)]
    return g.reset_index(drop=True)


def join_census(g, census: pd.DataFrame, strict: bool = True):
    """Attach census rows to polygons. Raises if the join is not a bijection (``strict``)."""
    c = census.copy()
    c["base"] = c["name"].map(cyr_to_ascii)
    c["area_ascii"] = c["area"].map(cyr_to_ascii)
    dup = c.base.duplicated(keep=False)
    c["key_lat"] = c.base.where(~dup, c.base + "@" + c.area_ascii)

    def qual_fits(qual: str, area_ascii: str) -> bool:
        return bool(qual) and re.match("^" + qual.replace("?", ".") + "$", area_ascii[: len(qual)]) is not None

    taken: dict[int, str] = {}
    used: set[str] = set()
    unique_exact = set(c.loc[~dup, "key_lat"])

    for i, row in g.iterrows():  # 1. exact, no homonyms, no wildcards
        if "?" not in row.key_lat and row.key_lat in unique_exact and row.key_lat not in used:
            taken[i] = row.key_lat
            used.add(row.key_lat)

    homonyms = c[dup]
    for i, row in g.iterrows():  # 2. homonyms, split by qualifier
        if i in taken:
            continue
        rx = re.compile("^" + row.key_lat.replace("?", ".") + "$")
        hits = [
            r.key_lat
            for r in homonyms.itertuples()
            if rx.match(r.base) and qual_fits(row.qual, r.area_ascii) and r.key_lat not in used
        ]
        if len(hits) == 1:
            taken[i] = hits[0]
            used.add(hits[0])
        elif len(hits) > 1 and strict:
            raise ValueError(f"{row.opstina__1!r}: qualifier does not separate homonyms {hits}")

    free = [k for k in c.key_lat if k not in used]
    for i, row in g.iterrows():  # 3. wildcard, only if unique
        if i in taken or "?" not in row.key_lat:
            continue
        rx = re.compile("^" + row.key_lat.replace("?", ".") + "$")
        hits = [k for k in free if rx.match(k.split("@")[0])]
        if len(hits) == 1:
            taken[i] = hits[0]
            free.remove(hits[0])
        elif len(hits) > 1 and strict:
            raise ValueError(f"pattern {row.opstina__1!r} matches several municipalities: {hits}")

    g = g.copy()
    g["matched"] = pd.Series(taken)
    out = g.dropna(subset=["matched"]).merge(
        c, left_on="matched", right_on="key_lat", how="left", suffixes=("", "_census")
    )
    if strict:
        if out.matched.duplicated().any():
            raise ValueError("a municipality received more than one polygon")
        missing = set(c.key_lat) - set(out.matched)
        if missing:
            raise ValueError(f"municipalities without a polygon: {sorted(missing)}")
    return out
