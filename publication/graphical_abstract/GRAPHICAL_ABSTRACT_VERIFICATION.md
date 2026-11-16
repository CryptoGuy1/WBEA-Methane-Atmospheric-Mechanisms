# Graphical abstract: verification
**Files:** `graphical_abstract.pdf` and `.svg` (vector), `graphical_abstract.png` (300 dpi, 3137 x 1254 px). The PNG exceeds Elsevier's minimum of 1328 x 531 px at the same 2.5 : 1 ratio.
**Script:** `make_graphical_abstract.py`. It reads committed results only (experiment source `1788301`; station coordinates from the manuscript branch `b61ffbf`).

## Content provenance
- **No photographs, raster images or generative-AI imagery.** Every element is drawn in code; the PDF contains 0 raster images. Fonts: Liberation Sans (Arial-metric), embedded.
- **Station map:** official 2024 coordinates (km from AMS 5).
  - Lines: the 21 registered 2026 pairs (`h2_pairs.csv`).
  - Hollow marker: AMS 2, excluded in 2026.
  - AMS 14 and AMS 18 are outside the pair family and not drawn.
- **H1 thumbnail:** development 0.0475 (0.0411-0.0520) vs registered 2026 0.0520 (0.0391-0.0695) ppm/SD.
- **H2 thumbnail:** the actual 246-shift pooled null from the frozen run (maximum 0.1007) and the observed D = 0.287932. The script asserts these are reproduced exactly from the frozen matrices.
- **H3 thumbnail:** development 0.0269 (-0.0396-0.1264) vs registered 2026 0.0110 (-0.0199-0.0428).
- **Decisions:** as registered (H1 confirmed, H2 confirmed, H3 not confirmed).
- **Caveat:** the wind-advected shared-driver falsification was rejected in 200/200 synthetic realisations (Table S11).

## Checks
- All text inside the page.
- Legible at the 13.3 cm display width (headers, values, decisions and caveat).
- No overlapping elements.
