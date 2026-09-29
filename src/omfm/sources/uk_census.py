"""England & Wales census origin-destination tables, MSOA level.

2021  ODWP01EW  residence MSOA x workplace MSOA x place-of-work indicator
2011  WU01EW    residence MSOA x workplace MSOA (special workplaces as pseudo-codes)

The two censuses encode people without a commute differently. In 2021 they are rows whose
workplace equals the residence (indicator 1), so they sit on the diagonal of the matrix. In
2011 they have their own destination codes (OD0000001, OD0000003), so they sit outside it.
`read_od_2021(..., mode="naive")` keeps the 2021 rows to show what that does.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd

from ..analysis.delimitation import prepare_od
from ..config import params, path

__all__ = [
    "read_od_2021",
    "indicator_totals_2021",
    "read_od_2011",
    "special_totals_2011",
    "read_od_2011_ons",
    "load_boundaries",
    "msoa_to_ttwa",
]

_COLS21 = ["origin", "origin_label", "dest", "dest_label", "indicator", "indicator_label", "flow"]


def _raw(rel: str) -> Path:
    return path("raw", rel)


def _chunks_2021(member: str, chunksize: int = 2_000_000):
    cfg = params()["uk"]["od_2021"]
    with zipfile.ZipFile(_raw(cfg["file"])) as zf, zf.open(member) as fh:
        yield from pd.read_csv(fh, names=_COLS21, header=0, chunksize=chunksize, dtype={"origin": str, "dest": str})


def _restrict(od: pd.DataFrame, prefixes) -> pd.DataFrame:
    ok = tuple(prefixes)
    keep = {u for u in set(od.origin) & set(od.dest) if u.startswith(ok)}
    return od[od.origin.isin(keep) & od.dest.isin(keep)].reset_index(drop=True)


def read_od_2021(mode: str = "fixed", level: str = "msoa") -> pd.DataFrame:
    """Census 2021 OD. ``mode``: "fixed" keeps indicator 3 only; "naive" keeps 1 and 3."""
    cfg = params()["uk"]
    keep = cfg["od_2021"]["keep_indicator" if mode == "fixed" else "naive_indicator"]
    member = cfg["od_2021"]["member" if level == "msoa" else "member_lad"]
    parts = [c.loc[c.indicator.isin(keep) & (c.flow > 0), ["origin", "dest", "flow"]] for c in _chunks_2021(member)]
    od = prepare_od(pd.concat(parts, ignore_index=True), "origin", "dest", "flow")
    prefixes = cfg["unit_prefixes"] if level == "msoa" else ["E0", "W0"]
    return _restrict(od, prefixes)


def indicator_totals_2021() -> pd.Series:
    """People per place-of-work indicator (all of England & Wales)."""
    member = params()["uk"]["od_2021"]["member"]
    tot = pd.concat([c.groupby(["indicator", "indicator_label"]).flow.sum() for c in _chunks_2021(member)])
    return tot.groupby(level=[0, 1]).sum()


def _read_2011() -> pd.DataFrame:
    cfg = params()["uk"]["od_2011"]
    with zipfile.ZipFile(_raw(cfg["file"])) as zf:
        raw = zf.read(cfg["member"])
    return pd.read_csv(
        io.BytesIO(raw),
        names=["origin", "dest", "flow", "male", "female"],
        header=0,
        dtype={"origin": str, "dest": str},
    )


def read_od_2011() -> pd.DataFrame:
    """Census 2011 OD between MSOAs of England & Wales; pseudo-codes and other nations dropped."""
    od = prepare_od(_read_2011(), "origin", "dest", "flow")
    return _restrict(od, params()["uk"]["unit_prefixes"])


def read_od_2011_ons() -> pd.DataFrame:
    """The 2011 matrix as ONS coded it for the 2011 TTWAs: people who work mainly at or from home, at
    an offshore installation or with no fixed place are counted at their residence; workplaces
    outside the UK are dropped (ONS methodology note on 2011 TTWAs, August 2015)."""
    d = _read_2011()
    codes = params()["uk"]["od_2011"]["special_codes"]
    at_home = [c for c, label in codes.items() if label != "outside the UK"]
    moved = d[d.dest.isin(at_home)].assign(dest=lambda x: x.origin)
    od = prepare_od(pd.concat([d[~d.dest.isin(codes)], moved]), "origin", "dest", "flow")
    return _restrict(od, params()["uk"]["unit_prefixes"])


def special_totals_2011() -> pd.Series:
    """People per special destination code, residents of England & Wales."""
    d = _read_2011()
    codes = params()["uk"]["od_2011"]["special_codes"]
    ew = d[d.origin.str.startswith(tuple(params()["uk"]["unit_prefixes"]))]
    return ew[ew.dest.isin(codes)].groupby("dest").flow.sum().rename(index=codes)


def load_boundaries(year: int):
    """MSOA polygons (BGC) in British National Grid with column ``unit``."""
    import geopandas as gpd

    cfg = params()["uk"]
    g = gpd.read_file(_raw(cfg[f"boundaries_{year}"]))
    code = next(c for c in g.columns if c.upper() in (f"MSOA{str(year)[2:]}CD",))
    return g.rename(columns={code: "unit"})[["unit", "geometry"]].to_crs(cfg["crs"])


def _records(rel: str) -> pd.DataFrame:
    return pd.read_json(_raw(rel))


def _plurality(j: pd.DataFrame, unit: str) -> pd.DataFrame:
    n = j.groupby([unit, "TTWA11CD", "TTWA11NM"]).size().rename("n").reset_index()
    n["share"] = n.n / n.groupby(unit).n.transform("sum")
    best = n.sort_values([unit, "n", "TTWA11CD"], ascending=[True, False, True]).drop_duplicates(unit)
    out = best.rename(columns={unit: "unit", "TTWA11CD": "ttwa", "TTWA11NM": "ttwa_name"})
    return out[["unit", "ttwa", "ttwa_name", "share"]].reset_index(drop=True)


def msoa_to_ttwa(year: int = 2011) -> pd.DataFrame:
    """Best-fit MSOA -> official TTWA 2011.

    TTWAs are built from smaller blocks than MSOAs (LSOAs in 2011; ONS publishes an OA 2021
    best fit). An MSOA goes to the TTWA that holds the plurality of its blocks; ``share`` is
    that plurality's share, so ``share < 1`` marks an MSOA the official boundary cuts.
    """
    cfg = params()["uk"]
    if year == 2011:
        blocks = _records(cfg["lookup_lsoa11_ttwa11"])[["LSOA11CD", "TTWA11CD", "TTWA11NM"]]
        up = _records(cfg["lookup_oa11_msoa11"])[["LSOA11CD", "MSOA11CD"]].drop_duplicates()
        return _plurality(up.merge(blocks, on="LSOA11CD", how="inner"), "MSOA11CD")
    blocks = _records(cfg["lookup_oa21_ttwa11"])[["OA21CD", "TTWA11CD", "TTWA11NM"]]
    up = _records(cfg["lookup_oa21_msoa21"])[["OA21CD", "MSOA21CD"]].drop_duplicates()
    return _plurality(up.merge(blocks, on="OA21CD", how="inner"), "MSOA21CD")
