"""Reconciliation against the raw files: totals, code lists, bijections.

Skipped when the raw data are not on disk (as in continuous integration).
"""

import pandas as pd
import pytest

from omfm.config import params, path

RAW = path("raw")


def need(rel):
    if not (RAW / rel).exists():
        pytest.skip(f"raw file missing: {rel}")


def test_uk_2021_indicator_code_list():
    need(params()["uk"]["od_2021"]["file"])
    from omfm.sources import uk_census as uk

    ind = uk.indicator_totals_2021()
    assert set(ind.index.get_level_values(0)) == {-8, 1, 2, 3}
    od = uk.read_od_2021("fixed")
    # flows between MSOAs of England and Wales: indicator 3 minus workplaces in Scotland or Northern Ireland
    assert 0 <= ind.xs(3, level=0).sum() - od.flow.sum() < 20_000
    assert od.origin.str.startswith(("E02", "W02")).all() and od.dest.str.startswith(("E02", "W02")).all()


def test_uk_2011_pseudo_codes_are_gone():
    need(params()["uk"]["od_2011"]["file"])
    from omfm.sources import uk_census as uk

    od = uk.read_od_2011()
    assert not od.dest.str.startswith("OD").any()
    assert set(uk.special_totals_2011().index) == set(params()["uk"]["od_2011"]["special_codes"].values())


def test_serbia_sums_to_the_republic_total():
    cfg = params()["serbia"]
    need(cfg["work"])
    from omfm.sources import serbia_census as rc

    allrows = rc.read_daily_migration(path("raw", cfg["work"]), level="all")
    mun = allrows[allrows.level == "municipality"]
    republic = allrows[allrows.name == "РЕПУБЛИКА СРБИЈА"].total.iloc[0]
    assert len(mun) == cfg["n_municipalities"]
    assert mun.total.sum() == republic == cfg["republic_total_work"]
    w = rc.add_self_containment(mun)
    assert set(w[w.sc == 0].name) == set(w[w.single_settlement].name)


def test_serbia_join_is_a_bijection_and_no_large_polygon_is_urban():
    cfg = params()["serbia"]
    need(cfg["boundaries"])
    from omfm.sources import serbia_census as rc
    from omfm.sources import serbia_geo as rg

    w = rc.add_self_containment(rc.read_daily_migration(path("raw", cfg["work"])))
    g = rg.load_municipalities(f"zip://{path('raw', cfg['boundaries'])}!{cfg['boundaries_member']}")
    j = rg.join_census(g, w)
    assert len(j) == j.matched.nunique() == cfg["n_municipalities"]
    assert not j.opstina_ma.astype(str).str.startswith(rg.NOT_COVERED_PREFIX).any()
    km2 = j.to_crs(cfg["crs"]).area / 1e6
    assert km2[j.single_settlement.astype(bool)].max() < cfg["max_polygon_km2_for_urban_municipality"]


def test_japan_code_lists_and_normalisation():
    cfg = params()["japan"]
    need(cfg["fromto"])
    from omfm.sources import jp_mlit as jp

    f = jp.read_fromto()
    assert set(f.from_area) == {0, 1, 2, 3}
    assert set(f.dayflag) == {0, 1, 2} and set(f.timezone) == {0, 1, 2}
    assert f.population.min() >= cfg["suppression_below"]
    t = f[(f.dayflag == 2) & (f.timezone == 2)].groupby("year").population.sum()
    assert ((t / t.mean() - 1).abs() < 0.005).all()


def test_netherlands_regions_sum_to_the_national_row():
    cache = path("interim", params()["netherlands"]["cache"])
    if not cache.exists():
        pytest.skip("CBS table not fetched")
    from omfm.sources import nl_cbs as nl

    df = pd.read_csv(cache)
    od = nl.corop_matrix(df)
    assert od.origin.nunique() == od.dest.nunique() == 40
    national = df[(df.origin == "NL10") & (df.dest == "NL10")].jobs_thousands.iloc[0] * 1000
    assert abs(od.flow.sum() - national) / national < 0.005
