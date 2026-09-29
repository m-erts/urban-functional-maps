"""Unpack a pptx: text+notes (markitdown), embedded media, slide renders (LibreOffice + pdftoppm).

Usage: python scripts/extract_deck.py talk/FOSS4G2026_talk2_v1.pptx
"""
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

deck = Path(sys.argv[1])
out = deck.parent
with zipfile.ZipFile(deck) as z:
    for n in z.namelist():
        if n.startswith("ppt/media/"):
            (out / "figures_from_deck").mkdir(exist_ok=True)
            (out / "figures_from_deck" / Path(n).name).write_bytes(z.read(n))
    rels = [n for n in z.namelist() if n.startswith("ppt/slides/_rels/")]
    with open(out / "figures_from_deck" / "slide_media_map.txt", "w") as f:
        for r in sorted(rels):
            media = re.findall(r'media/[^"]+', z.read(r).decode())
            f.write(f"{r}: {media}\n")
if shutil.which("markitdown"):
    (out / f"{deck.stem}.md").write_text(subprocess.run(["markitdown", str(deck)], capture_output=True, text=True).stdout)
if shutil.which("soffice") and shutil.which("pdftoppm"):
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out), str(deck)], check=False)
    subprocess.run(["pdftoppm", "-jpeg", "-r", "110", str(out / f"{deck.stem}.pdf"), str(out / "slides_png" / "slide")], check=False)
print("done:", out)
