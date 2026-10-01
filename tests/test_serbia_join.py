"""The join that once put one municipality's values on another polygon."""

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from omfm.sources import serbia_geo as rg


def _polygons(rows):
    g = gpd.GeoDataFrame(
        rows,
        columns=["opstina__1", "opstina_ma"],
        geometry=[box(i, 0, i + 1, 1) for i in range(len(rows))],
        crs="EPSG:32634",
    )
    g[["key_lat", "qual"]] = g.opstina__1.apply(lambda s: pd.Series(rg._split_qualifier(s)))
    return g


def test_digraphs_are_two_letters():
    assert rg.cyr_to_ascii("Ариље") == "ARILJE"
    assert rg.cyr_to_ascii("Књажевац") == "KNJAZEVAC"
    assert rg.cyr_to_ascii("Оџаци") == "ODZACI"


def test_wildcard_is_refused_when_ambiguous():
    census = pd.DataFrame({"name": ["Раковица", "Баковица"], "area": ["Београдска област", "Нека област"]})
    g = _polygons([("?AKOVICA", "70181")])
    with pytest.raises(ValueError, match="matches several"):
        rg.join_census(g, census)


def test_exact_match_takes_the_name_before_a_wildcard_can():
    census = pd.DataFrame({"name": ["Раковица"], "area": ["Београдска област"]})
    g = _polygons([("RAKOVICA", "70181"), ("?AKOVICA", "90123")])
    g = g[~g.opstina_ma.str.startswith(rg.NOT_COVERED_PREFIX)]
    j = rg.join_census(g, census)
    assert len(j) == 1 and j.opstina_ma.iloc[0] == "70181"


def test_homonyms_are_split_by_qualifier():
    census = pd.DataFrame({"name": ["Палилула", "Палилула"], "area": ["Београдска област", "Нишавска област"]})
    g = _polygons([("PALILULA (BEOGRAD)", "70200"), ("PALILULA (NI?)", "71200")])
    j = rg.join_census(g, census).set_index("opstina_ma")
    assert j.loc["70200", "area"] == "Београдска област"
    assert j.loc["71200", "area"] == "Нишавска област"


def test_join_must_be_a_bijection():
    census = pd.DataFrame({"name": ["Ариље", "Ада"], "area": ["Златиборска област", "Севернобанатска област"]})
    with pytest.raises(ValueError, match="without a polygon"):
        rg.join_census(_polygons([("ARILJE", "70041")]), census)
