.PHONY: env fetch analysis figures register docs pdf test lint all dna
PY ?= python

env:       ; conda env create -f environment.yml || conda env update -f environment.yml
fetch:     ; $(PY) scripts/fetch_data.py
analysis:  ; $(PY) scripts/run.py analysis
figures:   ; $(PY) scripts/run.py figures
register:  ; $(PY) scripts/run.py register
docs:      ; $(PY) scripts/render_docs.py
pdf:       ; bash scripts/build_pdf.sh
test:      ; pytest -q
lint:      ; ruff check src tests scripts
dna:       ; $(PY) scripts/neighborhood_dna.py 34.30 132.35 34.48 132.55 hiroshima
all: fetch analysis figures register docs test
