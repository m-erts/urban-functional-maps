# Design System: Swiss Civic Lab (Geospatial Benchmark)

## Philosophy
- Objective, institutional clarity inspired by international research institutes (JRC, Eurostat).
- High data density: side-by-side metric tables, resolution comparisons, choropleths.
- No AI fluff: zero floating cards, zero glow/neon bloat, strict 1px grid structure.

## Palette
- Canvas: #F8FAFC (paper white) / #0F172A (dark reading mode)
- Surfaces / Header: #F1F5F9 / #1E293B
- Typography: Inter, -apple-system, sans-serif
- Monospace / Metrics: JetBrains Mono / IBM Plex Mono
- Borders: 1px solid #CBD5E1 (light) / #334155 (dark)

## Semantic Geo-Sources
- Eurostat: #1D4ED8 (institutional blue)
- OpenStreetMap: #15803D (open data green)
- Census / Ground Truth: #D97706 (warm amber)

## Validation (added 2026-09-29)
- Source colours checked with the six-check palette validator (lightness band, chroma floor, colour-vision-deficiency separation, contrast) on canvas #F8FAFC: all pass.
- OpenStreetMap green and census amber separate at dE 6.5 under protanopia, inside the 6 to 8 band that is legal only with a second encoding. Every chart that shows both therefore labels them directly or gives them different marker shapes.
- Dark reading mode uses #3B82F6 for Eurostat and #16A34A for OpenStreetMap; #1D4ED8 has a contrast of 2.66:1 on #0F172A, below the 3:1 floor for marks.
- Added tokens: reference layers #475569, artefacts (cut-off fragments, structural zeros) #B91C1C.
- Sequential ramps are one hue per source, light to dark. The diverging ramp runs blue, neutral grey #E2E8F0, amber.
- Figures: `src/omfm/viz/style.py`. Slides: `templates/slides.html`. Paper: `docs/paper/paper.css`.
