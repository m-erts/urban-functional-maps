"""The rendered documents must carry the numbers of the last run."""

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_documents_are_up_to_date():
    if not (ROOT / "outputs" / "tables" / "register_counts.yaml").exists():
        pytest.skip("register not written")
    spec = importlib.util.spec_from_file_location("render_docs", ROOT / "scripts" / "render_docs.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.main(check=True) == 0


def test_no_placeholder_is_left():
    for rel in ("README.md", "docs/slides/index.html", "docs/outreach/linkedin.md", "docs/paper/paper.src.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "{{" not in text, rel


def _golden() -> dict:
    import yaml

    f = ROOT / "outputs" / "tables" / "golden_actual.yaml"
    if not f.exists():
        pytest.skip("pipeline not run")
    return yaml.safe_load(f.read_text(encoding="utf-8"))


def test_statements_in_the_text_hold():
    """Sentences of the paper that state an order or a property, not a number."""
    g = _golden()
    tail = "_from_placement"
    rows = [k[len("dec_") : -len(tail)] for k in g if k.startswith("dec_") and k.endswith(tail)]
    if not rows:
        pytest.skip("decomposition not run")
    # 4.2: every partition beats all kept states of its chain; placement is never the largest part
    assert g["dec_share_below_min"] == 1.0
    for r in rows:
        assert g[f"dec_{r}_from_placement"] < max(g[f"dec_{r}_from_scale"], g[f"dec_{r}_from_contiguity"]), r
    # 4.2: contiguity is the largest part in every British row, scale in every Dutch row
    for r in rows:
        parts = {p: g[f"dec_{r}_from_{p}"] for p in ("scale", "contiguity", "placement")}
        if r.startswith("uk_"):
            assert max(parts, key=parts.get) == "contiguity", r
        if r.startswith("nl_"):
            assert max(parts, key=parts.get) == "scale", r
    # 4.2: the Dutch heuristic's raw score is the highest; one of its areas holds the four Randstad cities
    assert g["dec_nl_2023_own_observed"] == max(g[f"dec_{r}_observed"] for r in rows)
    assert g["nl23_own_largest_holds_randstad"] == 1
    # 4.3 and 5: COROP regions sit below both constructions on the same pairs, and more than half fail the rule
    assert g["dec_nl_2023_corop_from_placement"] < min(
        g["dec_nl_2023_lma_from_placement"], g["dec_nl_2023_own_from_placement"]
    )
    assert g["nl23_corop_valid_share"] < 0.5
    # 4.3: the Coombes-Bond output leaves unassigned only the foreign zones that receive trips
    assert g["es_lma_unassigned"] == g["es_units_foreign"]
    # 4.3: weighting by area lowers the mean IoU of the heuristic and the naive repairs; not of Coombes-Bond (ONS)
    for name in ("contiguous", "ttwa_greedy", "ttwa_dissolution"):
        assert g[f"uk_iou_area_{name}_2011"] < g[f"uk_iou_{name}_2011"], name
    if "uk_iou_lma_ons_2011" in g:
        assert g["uk_iou_area_lma_ons_2011"] > g["uk_iou_lma_ons_2011"]
        # 4.3 and 5: the ONS coding gives more areas and closer agreement; the heuristic still agrees best
        assert g["uk_lma_ons_areas_2011"] > g["uk_lma_areas_2011"]
        assert g["uk_ari_lma_2011"] < g["uk_ari_lma_ons_2011"] < g["uk_ari_contiguous_2011"]
        # 4.2: in England and Wales Coombes-Bond places boundaries worse than the heuristic; official best
        uk = {k: g[f"dec_uk_2011_{k}_from_placement"] for k in ("own", "lma", "lma_ons", "official")}
        assert max(uk["lma"], uk["lma_ons"]) < uk["own"] < uk["official"]
        assert g["dec_es_2023_lma_from_placement"] == max(g[k] for k in g if k.endswith("_from_placement"))
    # 4.3: the naive repairs move the map away from the official one
    assert max(g["uk_ari_ttwa_greedy_2011"], g["uk_ari_ttwa_dissolution_2011"]) < g["uk_ari_contiguous_2011"]
