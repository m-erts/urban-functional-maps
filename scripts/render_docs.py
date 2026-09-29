"""Fill the document templates with the numbers the pipeline produced.

    python scripts/render_docs.py            write README.md, the paper, the slides, the announcement
    python scripts/render_docs.py --check    fail if a rendered file is out of date

A placeholder is ``{{key}}``, ``{{key:.3f}}``, ``{{key/1e6:.1f}}`` or ``{{key*100:.0f}}``; ``key`` is an entry of
``outputs/tables/golden_actual.yaml`` or of ``register_counts.yaml``.
"""

import argparse
import re
import sys

import yaml

from omfm.config import ROOT, path

TARGETS = {
    "templates/README.md": "README.md",
    "templates/paper.md": "docs/paper/paper.src.md",
    "templates/slides.html": "docs/slides/index.html",
    "templates/linkedin.md": "docs/outreach/linkedin.md",
    "templates/response.md": "docs/paper/response_to_reviewers.md",
}
PLACEHOLDER = re.compile(r"\{\{\s*([a-z0-9_]+)\s*(?:([*/])\s*([0-9.e]+))?\s*(?::([^}]+))?\}\}")


def render(text: str, values: dict) -> str:
    def sub(m: re.Match) -> str:
        key, op, num, spec = m.groups()
        if key not in values:
            raise KeyError(f"{key} is not in golden_actual.yaml")
        v = values[key]
        if op:
            v = v * float(num) if op == "*" else v / float(num)
        return format(v, spec) if spec else str(v)

    out = PLACEHOLDER.sub(sub, text)
    left = re.findall(r"\{\{[^}]*\}\}", out)
    if left:
        raise ValueError(f"placeholders the renderer cannot read: {sorted(set(left))[:5]}")
    return out


def main(check: bool) -> int:
    values = yaml.safe_load(path("tables", "golden_actual.yaml").read_text(encoding="utf-8"))
    values.update(yaml.safe_load(path("tables", "register_counts.yaml").read_text(encoding="utf-8")))
    stale = []
    for src, dst in TARGETS.items():
        if not (ROOT / src).exists():
            continue
        out = render((ROOT / src).read_text(encoding="utf-8"), values)
        target = ROOT / dst
        if check:
            if not target.exists() or target.read_text(encoding="utf-8") != out:
                stale.append(dst)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(out, encoding="utf-8")
            print(f"[omfm] rendered {dst}")
    for s in stale:
        print(f"out of date: {s} (run python scripts/render_docs.py)")
    return 1 if stale else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    sys.exit(main(ap.parse_args().check))
