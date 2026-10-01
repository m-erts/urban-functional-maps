"""Spain: open mobility study of the Ministry of Transport (MITMA), 2022 onward, by district.

Daily files of trips between 3,909 zones: in Spain, municipalities, groups of small
municipalities (codes ending in ``_AM``) and census districts of large cities; abroad, the
NUTS-3 regions of France and Portugal (codes beginning with ``FR`` or ``PT``). Each row is an origin, a
destination, an hour of departure (``periodo``), the activity at both ends (``casa`` home,
``trabajo_estudio`` work or study, ``frecuente`` frequent place, ``no_frecuente`` other), a flag
for destinations that may be a place of study, and the number of trips expanded to the
population (``viajes``).

This is the only source in this study that publishes origin-destination pairs, a purpose and
the hour together. The pairs are trips on one day, not persons.
"""

from __future__ import annotations

import pandas as pd

from ..config import params, path

__all__ = ["read_trips", "home_to_work", "hourly", "load_districts", "district_names"]

_COLS = [
    "periodo",
    "origen",
    "destino",
    "actividad_origen",
    "actividad_destino",
    "estudio_destino_posible",
    "viajes",
]


def _files() -> list:
    cfg = params()["spain"]
    return [path("raw", "ES", f"{d}_Viajes_distritos.csv.gz") for d in cfg["days"]]


def read_trips() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aggregate the configured days.

    Returns (od, hours): ``od`` is the mean daily number of trips from home to work or study, by
    origin, destination and study flag; ``hours`` is the mean daily number of all trips by hour of
    departure and activity pair.
    """
    days = _files()
    od_days, h_days = [], []
    for f in days:
        parts_od, parts_h = [], []
        for ch in pd.read_csv(
            f, sep="|", usecols=_COLS, chunksize=4_000_000, dtype={"origen": str, "destino": str, "periodo": int}
        ):
            parts_h.append(ch.groupby(["periodo", "actividad_origen", "actividad_destino"]).viajes.sum())
            w = ch[(ch.actividad_origen == "casa") & (ch.actividad_destino == "trabajo_estudio")]
            parts_od.append(w.groupby(["origen", "destino", "estudio_destino_posible"]).viajes.sum())
        od_days.append(pd.concat(parts_od).groupby(level=[0, 1, 2]).sum())
        h_days.append(pd.concat(parts_h).groupby(level=[0, 1, 2]).sum())
    n = len(days)
    od = (pd.concat(od_days).groupby(level=[0, 1, 2]).sum() / n).rename("trips").reset_index()
    hours = (pd.concat(h_days).groupby(level=[0, 1, 2]).sum() / n).rename("trips").reset_index()
    return od, hours


def home_to_work(od: pd.DataFrame, study: str = "no") -> pd.DataFrame:
    """Trips from home to work or study, as ``origin, dest, flow``.

    ``study="no"`` keeps destinations that are not a possible place of study, the nearest this
    source comes to work alone; ``study="all"`` keeps both.
    """
    m = od
    if study != "all":
        m = m[m.estudio_destino_posible == study]
    m = m.groupby(["origen", "destino"], as_index=False).trips.sum()
    return pd.DataFrame({"origin": m.origen, "dest": m.destino, "flow": m.trips})


def hourly(hours: pd.DataFrame) -> pd.DataFrame:
    """Trips by hour of departure for the four main activity pairs."""
    pair = hours.actividad_origen + " > " + hours.actividad_destino
    return hours.assign(pair=pair).pivot_table(index="periodo", columns="pair", values="trips", aggfunc="sum")


def load_districts():
    """District polygons, projected to the analysis CRS, with column ``unit``."""
    import geopandas as gpd

    cfg = params()["spain"]
    g = gpd.read_file(path("raw", cfg["districts"]))
    g = g.rename(columns={"ID": "unit"})[["unit", "geometry"]]
    g = g.dissolve("unit").reset_index()
    return g.to_crs(cfg["crs"])


def district_names() -> pd.Series:
    cfg = params()["spain"]
    return pd.read_csv(path("raw", cfg["names"]), sep="|", dtype=str).set_index("ID").name
