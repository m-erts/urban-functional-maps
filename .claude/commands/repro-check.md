Run the reproducibility check:
1. `python scripts/run.py analysis` (or `--only <case>`), then `pytest -q`.
2. For every value that differs from tests/golden_values.yaml show expected and actual, the producing
   function and the most likely cause (parameter, cleaning rule, data vintage). Do NOT change parameters to
   force agreement.
3. If the new value is the right one, say why, then `python scripts/run.py register --freeze` and
   `python scripts/render_docs.py`.
$ARGUMENTS
