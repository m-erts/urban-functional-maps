.PHONY: env env-r fetch lma analysis figures register docs pdf test lint all dna
PY ?= python

env:       ; conda env create -f environment.yml || conda env update -f environment.yml
env-r:     ; conda env create -f r/environment-r.yml && conda run -n omfm-r Rscript -e 'install.packages("LabourMarketAreas", repos="https://cloud.r-project.org")'
fetch:     ; $(PY) scripts/fetch_data.py
# Coombes-Bond partitions; needs the omfm-r environment and the matrices written by 'analysis --only uk,nl23,es'
lma:       ; for m in uk_2011 nl_2023 es_2023; do conda run -n omfm-r Rscript r/run_lma.R data/interim/$${m%_*}_od_$${m#*_}.csv outputs/tables/$${m}_areas_lma.csv 3500 0.667 25000 0.75; done; \
             conda run -n omfm-r Rscript r/run_lma.R data/interim/uk_od_2011_ons.csv outputs/tables/uk_2011_areas_lma_ons.csv 3500 0.667 25000 0.75
analysis:  ; $(PY) scripts/run.py analysis
figures:   ; $(PY) scripts/run.py figures
register:  ; $(PY) scripts/run.py register
docs:      ; $(PY) scripts/render_docs.py
pdf:       ; bash scripts/build_pdf.sh
test:      ; pytest -q
lint:      ; ruff check src tests scripts
dna:       ; $(PY) scripts/neighborhood_dna.py 34.30 132.35 34.48 132.55 hiroshima
all: fetch analysis figures register docs test
