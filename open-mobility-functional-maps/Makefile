.PHONY: env fetch interim analysis figures test all deck lint issues
PY ?= python
env:      ; conda env create -f environment.yml || conda env update -f environment.yml
fetch:    ; $(PY) scripts/run.py fetch
interim:  ; $(PY) scripts/run.py interim
analysis: ; $(PY) scripts/run.py analysis
figures:  ; $(PY) scripts/run.py figures
test:     ; pytest -q
lint:     ; ruff check src tests scripts
deck:     ; $(PY) scripts/extract_deck.py talk/FOSS4G2026_talk2_v1.pptx
issues:   ; scripts/create_github_issues.sh
all: fetch interim analysis figures test
