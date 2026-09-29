#!/usr/bin/env bash
# Create milestones, labels and issues from docs/backlog.yaml. Requires: gh (authenticated), python3 + pyyaml.
# Usage: scripts/create_github_issues.sh [--dry-run]
set -euo pipefail
DRY=${1:-}
python3 - "$DRY" <<'PY'
import sys, yaml, subprocess, json
dry = sys.argv[1] == "--dry-run"
b = yaml.safe_load(open("docs/backlog.yaml"))
def run(args):
    print(" ".join(repr(a) if " " in a else a for a in args))
    if not dry: subprocess.run(args, check=False)
for m, name in b["milestones"].items():
    run(["gh", "api", "repos/{owner}/{repo}/milestones", "-f", f"title={m} {name}"])
labels = sorted({l for i in b["issues"] for l in i["l"]} | {"P0", "P1", "P2"})
for l in labels:
    run(["gh", "label", "create", l, "--force"])
for i in b["issues"]:
    body = f"Milestone {i['m']} · priority {i['p']}\n\nSee docs/03_METHODOLOGY.md and docs/internal/05_REVIEW_FINDINGS.md."
    args = ["gh", "issue", "create", "--title", i["t"], "--body", body,
            "--milestone", f"{i['m']} {b['milestones'][i['m']]}", "--label", ",".join(i["l"] + [i["p"]])]
    run(args)
PY
