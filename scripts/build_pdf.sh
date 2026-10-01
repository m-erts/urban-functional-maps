#!/usr/bin/env bash
# Paper (HTML, PDF, DOCX) and slides (PDF) from the rendered documents.
# Needs pandoc and a Chromium-based browser. Set CHROME to its binary if it is not found.
set -euo pipefail
cd "$(dirname "$0")/.."

CHROME="${CHROME:-}"
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" google-chrome chromium chromium-browser; do
  if [ -z "$CHROME" ] && { [ -x "$c" ] || command -v "$c" >/dev/null 2>&1; }; then CHROME="$c"; fi
done
[ -n "$CHROME" ] || { echo "no Chromium-based browser found; set CHROME"; exit 1; }

python scripts/render_docs.py

cd docs/paper
pandoc paper.src.md --from markdown --citeproc --bibliography references.bib \
  --to gfm+tex_math_dollars --wrap=none --output paper.body.md
{
  printf '# %s\n\n' "$(sed -n 's/^title: "\(.*\)"$/\1/p' paper.src.md)"
  printf '%s. Version %s. %s.\n\n' \
    "$(sed -n 's/^author: "\(.*\)"$/\1/p' paper.src.md)" \
    "$(sed -n 's/^version: "\(.*\)"$/\1/p' paper.src.md)" \
    "$(sed -n 's/^license: \(.*\)$/\1/p' paper.src.md)"
  cat paper.body.md
} > paper.md
rm paper.body.md
pandoc paper.src.md --from markdown --citeproc --bibliography references.bib \
  --standalone --mathjax --css paper.css --metadata pagetitle="Open mobility data for functional-area maps" \
  --output index.html
pandoc paper.src.md --from markdown --citeproc --bibliography references.bib --output paper.docx
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=20000 \
  --print-to-pdf=paper.pdf "file://$PWD/index.html" 2>/dev/null
cd ../slides
"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=10000 \
  --print-to-pdf=slides.pdf "file://$PWD/index.html" 2>/dev/null
cd ../..
ls -la docs/paper/paper.pdf docs/paper/paper.docx docs/slides/slides.pdf
