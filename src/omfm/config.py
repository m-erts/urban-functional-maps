"""Configuration: one YAML file, repo-relative paths, no machine-specific constants."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(os.environ.get("OMFM_ROOT", Path(__file__).resolve().parents[2]))


@lru_cache(maxsize=1)
def params() -> dict:
    """Parsed ``config/params.yaml``."""
    return yaml.safe_load((ROOT / "config" / "params.yaml").read_text(encoding="utf-8"))


def path(key: str, *parts: str, mkdir: bool = False) -> Path:
    """Resolve a path declared under ``paths:`` in params.yaml, relative to the repo root."""
    base = ROOT / params()["paths"][key]
    p = base.joinpath(*parts)
    if mkdir:
        (p if not p.suffix else p.parent).mkdir(parents=True, exist_ok=True)
    return p
