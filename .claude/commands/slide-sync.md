Check the documents against the pipeline:
1. `python scripts/render_docs.py --check` must pass (README, paper, slides, announcement).
2. Read templates/slides.html and list every number that is typed and not a `{{placeholder}}`; each needs a
   reason to be typed (a date, a threshold declared in config/params.yaml).
3. Check every map and chart for the attribution of its source and the source colour of DESIGN.md.
$ARGUMENTS
