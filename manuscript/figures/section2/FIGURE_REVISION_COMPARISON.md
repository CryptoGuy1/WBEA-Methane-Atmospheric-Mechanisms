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

---
# Revision 3 (final consolidated specification; supersedes revision 2)
The revision-2 single map removed Fig. 1's full-network map, which this specification forbids. Revision 3 **restores all three original map components** of v1, without panel letters or internal titles. Revision-2 outputs are preserved in `archive_v2/`, with script `make_fig01_v2.py`.

| Figure | v1 | v2 | **v3 (final)** |
|---|---|---|---|
| Fig. 1 | 3 maps, (a)-(c), 158.6 x 101.4 mm | 1 map + inset, 180.0 x 158.0 mm | **3 maps, no letters, 174.5 x 118.0 mm** |
| Fig. 2 | 173.0 x 59.8 mm | 180.0 x 70.0 mm | **174.5 x 70.0 mm** |
| Fig. S1 daily | cropped | 180.0 x 70.0 mm | **174.5 x 70.0 mm (retained)** |
| Fig. S1 monthly | - | 180.0 x 66.0 mm | **174.5 x 66.0 mm, labelled ALTERNATIVE** |
| Fig. 2 single column | cropped | 90.0 x 92.0 mm | 90.0 x 92.0 mm (optional) |

174.5 mm equals the Elsevier CAS double-column `\textwidth` (494.5 pt), so the figures print at 100%: 6.8 pt labels, 6.3-6.5 pt legends, 5.6 pt attribution.

## Fig. 1 v3 component inventory (automated, `data/section2/fig01_components.json`)
- **Regional context map** (EPSG:3978): Canada, Alberta, study-area box, Fort McMurray, graticules.
- **Full network map** (UTM 12N): all 12 stations, 21 pairs, AMS 14/18 labelled, dashed enlarged-map extent, Athabasca River, Fort McMurray, 25 km scale bar, north arrow, latitude/longitude ticks.
- **Enlarged cluster map** (UTM 12N): 21 pairs, 10 labelled cluster stations, AMS 2 open square, 10 km scale bar, north arrow, ticks.
- **Legend** with 7 entries: Study area, Extent of enlarged map, station, excluded station, pair, community, river/lakes.

## Layout changes only (no data changes)
- Explicit millimetre positioning: maps are 109.5 mm tall (v1: about 90 mm).
- Panel letters and the "(c)" tag on the extent box removed; the box is explained in the legend.
- Collisions and edge clipping fixed (50°N label, rightmost tick).
- **Fig. 2 seam fix:** adjacent vector cells showed hairline white seams in PDF viewers at screen resolution (anti-aliasing). Cells are now stroked with their own fill colour (0.15 pt); data unchanged.

## Final checklist (all automated unless noted)
| Item | Status |
|---|---|
| All original components present (3 maps; 12 stations and 21 pairs per network map) | PASS |
| No panel letters; no internal titles | PASS |
| Coordinates, pairs, availability data unchanged (SHA-256 before/after) | PASS |
| Frozen experimental files unchanged (git diff vs `protocol-freeze`, `e08-confirmation`) | PASS |
| Exact PDF dimensions; all text inside page | PASS |
| Vector PDF/SVG, embedded fonts, 600-dpi PNG | PASS |
| CAS double-column compile with `figure*` at `\textwidth`: 0 errors, 0 overfull boxes | PASS |
| Visual inspection at print size (CAS pages rendered) | PASS |
