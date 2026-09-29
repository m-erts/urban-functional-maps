Run the reproducibility check:
1. `pytest -q` and summarise which golden values are reproduced / differ / skipped (tests/golden_values.yaml).
2. For every value that differs, show expected vs actual, the producing function, and the most likely cause
   (parameter, cleaning rule, data vintage). Do NOT change parameters to force agreement.
3. Update the `status` fields and regenerate docs/04_RESULTS_REGISTER.md via scripts/render_results_register.py.
$ARGUMENTS
