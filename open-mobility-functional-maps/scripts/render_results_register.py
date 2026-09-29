import yaml
rows = yaml.safe_load(open("tests/golden_values.yaml"))
out = ["# Results register", "", "Generated from `tests/golden_values.yaml`.", "",
       "| id | slide | value | tol | producing function | note | status |", "|---|---|---|---|---|---|---|"]
out += [f"| `{r['id']}` | {r['slide']} | {r['value']} | {r['tol']} | {r.get('fn','')} | {r.get('note','')} | {r['status']} |" for r in rows]
open("docs/04_RESULTS_REGISTER.md", "w").write("\n".join(out) + "\n")
