# Section 2 figures: original (v1) vs revised (v2)
v1 files are preserved in `archive_v1/` (scripts `make_fig01_v1.py`, `make_fig02_v1.py`).

## Exact exported dimensions (PDF page = MediaBox, measured with pdfinfo)
| Figure | v1 (tight-bbox crop) | v2 (fixed canvas) | Intended use |
|---|---|---|---|
| Fig. 1 network map | 158.6 x 101.4 mm | **180.0 x 158.0 mm** | Full width |
| Fig. 2 availability, Jan-Sep 2026 | 173.0 x 59.8 mm | **180.0 x 70.0 mm** | Full width (preferred) |
| Fig. 2, single-column variant | cropped (not measured) | **90.0 x 92.0 mm** | Optional |
| Fig. S1 daily 2021-2025 | cropped | **180.0 x 70.0 mm** | Supplementary |
| Fig. S1b monthly 2021-2025 (new) | - | **180.0 x 66.0 mm** | Supplementary (recommended) |

v1 used `bbox_inches="tight"`, which cropped the canvas, so the PDFs were not the stated 180 mm. v2 saves without cropping: the canvas equals the page (automated check, ±0.1 mm). In the Elsevier CAS double-column class, `\textwidth` = 174.5 mm, so full-width figures print at 97% (7 pt -> 6.8 pt; 6 pt -> 5.8 pt).

## Changes
**Fig. 1:**
- three labelled panels (a-c) became **one coherent map** (UTM 12N) plus a compact, unlabelled location inset;
- no titles or panel letters;
- the main map is enlarged to 92 x 149 mm, and station labels are 7 pt;
- all 21 frozen pairs are drawn;
- AMS 18, 92 km south, is shown by an off-map position note (geographic indicator, not a transport arrow);
- the legend is simplified to 6 entries;
- the data attribution note is moved under the legend.

**Fig. 2:**
- data and daily classes unchanged;
- exact 180 mm canvas;
- legend entries give hours and the proportion of 24 h, in two columns;
- the left margin is widened so the "AMS 2 (excluded)" label is not clipped.

**Fig. S1:** daily version retained (AMS 2 not marked excluded, since no exclusion applied in 2021-2025). New monthly option S1b: monthly completeness is markedly more readable over 59 months, and outages (for example AMS 5 and AMS 11 in mid-2021, AMS 18 in January 2024) are clear. The partial month of December 2025 is excluded.

## Final publication-quality checklist
| Item | Status |
|---|---|
| No titles or panel labels inside Figs 1-2 | PASS (automated: no "(a)"-type labels in PDF text) |
| Exact dimensions as documented | PASS (automated) |
| All text inside the page; no clipping | PASS (automated `pdftotext -bbox`; visual) |
| Vector PDF/SVG, embedded fonts, no raster images; PNG 600 dpi | PASS (automated) |
| Station labels legible at print size (>= 6.8 pt after CAS scaling) | PASS |
| 21 frozen pairs; coordinates exact; data unchanged | PASS (automated) |
| Colour-blind-friendly palette; no transport arrows; no significance colours | PASS |
| Compiles in Elsevier CAS (cas-dc 2.3) with 0 overfull boxes | PASS (`manuscript/latex_check/`) |
