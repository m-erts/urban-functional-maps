# data

| Folder | Content | In git |
|---|---|---|
| `raw/` | inputs as published, one folder per source | no |
| `interim/` | matrices and layers written by the pipeline | no |
| `derived/` | small aggregates whose source can no longer be queried | yes |

`manifest.yaml` lists every input with address, licence, size and SHA-256.
`python scripts/fetch_data.py` downloads what has a public address and checks the rest.
