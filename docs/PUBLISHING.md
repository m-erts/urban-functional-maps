# Publishing checklist

Three uses of the same material. Nothing in this file has been done for you: each step is an action under your name.

## Before anything is sent

- [ ] Read `docs/paper/paper.md` from start to end. It is a draft in your name.
- [x] Affiliation. The documents say "independent researcher" (`CITATION.cff`, `.zenodo.json`, `templates/paper.md`, `templates/slides.html`). Name an organisation only if the work was done there and it agrees in writing. `docs/TALK.md` and `talk/deck_v1_text.md` quote the biography and the title slide as submitted; they name the employer of that time.
- [x] ORCID iD 0009-0008-3040-5515 is in `CITATION.cff`, `.zenodo.json`, the paper and the slides.
- [ ] Decide on the statement "Use of AI tools" at the end of the paper. Most journals require such a statement; its wording is yours.
- [ ] Read `docs/ERRATA.md`. It states in public which numbers of the first version of the slides were wrong.
- [x] Status of the talk. README, paper, slides and announcement say that the talk was prepared for FOSS4G 2026 and accepted, and that the author was unable to present it.

## A. Conference organisers

Send:

| File | What it is |
|---|---|
| `docs/slides/slides.pdf` | slides, version 2, 16:9 |
| `docs/paper/paper.pdf` | text of the paper |
| `docs/TALK.md` | abstract as submitted, and what changed since |
| link to the repository | code, data manifest, results |

The contribution is licensed CC BY 4.0, as declared at submission. If the organisers publish slides on the programme page, send version 2 with the list of corrections.

## B. A DOI

**Software and preprint through Zenodo** (free, no review, a DOI in minutes):

1. Log in at zenodo.org with GitHub. Under *GitHub* in the account menu switch on `m-erts/urban-functional-maps`.
2. Only then create the release on GitHub: tag `v1.0.0`, title "v1.0.0: FOSS4G 2026 paper and slides". Zenodo archives releases created after the switch is on.
3. Zenodo reads `.zenodo.json`. It mints two DOIs: one for the version, one for all versions (the concept DOI).
4. Put the concept DOI into `CITATION.cff` (field `doi`), the README badge and the paper. Commit.

To give the paper its own DOI, upload `docs/paper/paper.pdf` to Zenodo as a separate record of type *Publication / Preprint* and link it to the software record (`isSupplementedBy`).

**Journals.** Read the current author guidelines before choosing; scope and fees change.

| Venue | Why it fits | To check |
|---|---|---|
| Environment and Planning B: Urban Analytics and City Science | urban analytics; publishes short papers on open data and code | word limit of the chosen article type; open access fee |
| Transactions in GIS | GIScience methods; the two nulls and the error matrix are the core | length; novelty is judged against the regionalisation literature |
| Computers, Environment and Urban Systems | methods applied to urban data | three countries with pairs; check that the scope of the empirical part is enough |
| Journal of Geographical Systems | spatial analysis methods | same |
| Regional Studies, Regional Science | open access, short articles on regional data and methods | fee |
| Journal of Open Source Software | a DOI for the software itself, reviewed in the open | requires a record of public development and research use; a repository created this month may be asked to wait |
| AGILE: GIScience Series or the FOSS4G academic track | conference papers with DOI | next deadlines |

What reviewers will ask first, and where the paper stands:

| Question | State |
|---|---|
| Is the closed form of the permutation null new? | It follows from linearity of expectation. Search the literature on modularity and on functional regions for an earlier statement before claiming priority; the paper claims use, not discovery |
| Why not run the official algorithm? | The standard Coombes-Bond algorithm (R package LabourMarketAreas) is run with the official parameters. The production code of the official areas (Fortran, Newcastle University) was not run, and the official map was cleaned by a secondary process; both are stated |
| One country | Three countries with pairs: England and Wales, the Netherlands (municipal pairs 2023), Spain (operator trips 2023) |
| Does the contiguous null sample uniformly? | No. The recombination chain samples the spanning-tree distribution; stated, with convergence diagnostics |
| Were the reviews of the first version answered? | `docs/paper/response_to_reviewers.md`, point by point |

## C. LinkedIn

Text: `docs/outreach/linkedin.md`, English and Russian. Image: `docs/figures/uk_decomposition.png`. Post after the repository is public in its final state, so that the links resolve.

## GitHub Pages

Settings, Pages, source: branch `main`, folder `/docs`. The slides are then at
`https://m-erts.github.io/urban-functional-maps/slides/` and the paper at `.../paper/`.
`docs/.nojekyll` is present, so files are served as they are.
