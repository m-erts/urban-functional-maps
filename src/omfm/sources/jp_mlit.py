"""Japan: MLIT 全国の人流オープンデータ (nationwide people-flow open data), 2019-2021.

Provider of the underlying data: Agoop Corp. (smartphone-application GPS panel, expanded to
population with Agoop's own factors). It is not mobile-network-operator data.

Two products per prefecture, both monthly:
  monthly_mdp_mesh1km    presence per 1 km mesh (JIS X 0410 third level)
  monthly_fromto_city    presence per municipality by residence ring ``from_area``

Codes (データ定義書, p. 6):
  dayflag    0 holiday, 1 weekday, 2 all days
  timezone   0 daytime, 1 night, 2 all day
  from_area  0 same municipality, 1 same prefecture, 2 same regional block, 3 other block
  population mean presence; cells under 10 people are not published

Three properties that the file names do not announce:
  1. "From-To" is not an origin-destination matrix: ``from_area`` is four nested rings.
  2. The values are presence, not trips.
  3. Volumes are normalised: prefecture totals of 2019, 2020 and 2021 agree within a fraction
     of a percent. Compare composition across years, never volume.
"""

from __future__ import annotations

import io
import zipfile

import pandas as pd

from ..config import params, path

__all__ = ["read_mesh", "read_fromto", "read_mesh_coords", "presence_shares", "FROM_AREA", "CITYCODE_FIXES"]

FROM_AREA = {0: "same_city", 1: "same_pref", 2: "same_region", 3: "other_region"}
CITYCODE_FIXES = {40305: 40231}  # Nakagawa (Fukuoka): pre-merger code in the 2019 files


def _nested_csvs(archive, suffix: str) -> pd.DataFrame:
    frames = []
    with zipfile.ZipFile(archive) as outer:
        for name in sorted(n for n in outer.namelist() if n.endswith(suffix)):
            with zipfile.ZipFile(io.BytesIO(outer.read(name))) as inner:
                member = next(m for m in inner.namelist() if m.endswith(".csv"))
                frames.append(pd.read_csv(io.BytesIO(inner.read(member))))
    if not frames:
        raise FileNotFoundError(f"no *{suffix} inside {archive}")
    df = pd.concat(frames, ignore_index=True)
    df["citycode"] = df["citycode"].replace(CITYCODE_FIXES)
    return df


def read_mesh() -> pd.DataFrame:
    """All months of the 1 km mesh product for the configured prefecture."""
    return _nested_csvs(path("raw", params()["japan"]["mesh"]), "monthly_mdp_mesh1km.csv.zip")


def read_fromto() -> pd.DataFrame:
    """All months of the municipality x residence-ring product."""
    return _nested_csvs(path("raw", params()["japan"]["fromto"]), "monthly_fromto_city.csv.zip")


def read_mesh_coords() -> pd.DataFrame:
    """Mesh id -> centre longitude / latitude, from the attribute file."""
    cfg = params()["japan"]
    with zipfile.ZipFile(path("raw", cfg["attribute"])) as outer:
        with zipfile.ZipFile(io.BytesIO(outer.read(cfg["attribute_member"]))) as inner:
            member = next(m for m in inner.namelist() if m.endswith(".csv"))
            a = pd.read_csv(io.BytesIO(inner.read(member)))
    return a[a.prefcode == cfg["prefecture"]].set_index("mesh1kmid")[["lon_center", "lat_center", "citycode"]]


def presence_shares(fromto: pd.DataFrame) -> pd.DataFrame:
    """Per (year, month, dayflag, timezone, citycode): presence by ring, total, local share."""
    p = (
        fromto.pivot_table(
            index=["year", "month", "dayflag", "timezone", "citycode"],
            columns="from_area",
            values="population",
            aggfunc="sum",
        )
        .reindex(columns=list(FROM_AREA))
        .fillna(0.0)
        .rename(columns=FROM_AREA)
    )
    p["total"] = p.sum(axis=1)
    p["local_share"] = (p.same_city / p.total).where(p.total > 0)
    return p.reset_index()
