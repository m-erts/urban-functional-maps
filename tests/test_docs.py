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
