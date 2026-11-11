# Section 2 figures and tables: handoff for independent review

**Branch:** `manuscript/section2-figures-tables` (from `main` d61f8ea; not merged). The final commit SHA is in the handoff message.
**Scope:** descriptive figures and tables only. No statistical inference. Frozen E08 results, E12 and E13 are untouched.

## Deliverables
| File | Content |
|---|---|
| `figures/section2/fig01_wbea_network.{pdf,svg}`, `_600dpi.png` | Fig. 1, 180 mm, three panels (see below) |
| `figures/section2/fig02_ch4_availability_2026.{pdf,svg}`, `_600dpi.png` | Fig. 2, 180 mm: daily CH4 availability, Jan-Sep 2026 |
| `figures/section2/fig02_ch4_availability_2026_single_column.*` | Fig. 2, 90 mm variant |
| `figures/section2/figS1_ch4_availability_2021_2025.*` | Supplementary: development period 2021-2025 |
| `tables/section2/table01_station_characteristics.tex` | Table 1 (booktabs) |
| `tables/section2/table02_data_sources_temporal_design.tex` | Table 2 (booktabs) |
| `figures/section2/CAPTIONS_AND_NOTES.md` | Suggested captions and table notes |
| `data/section2/*.csv` | Station list, frozen pairs, daily availability (2026; 2021-2025), coverage check, table sources |
| `data/section2/gis/` | Clipped Natural Earth layers (public domain) |
| `data/section2/GIS_SOURCES.md`, `QUALITY_CHECKLIST.md`, `validation_report.json` | Provenance, checklist, automated validation |
| `scripts/section2/` | `common.py`, `prepare_data.py`, `make_fig01.py`, `make_fig02.py`, `make_tables.py`, `validate.py`, `requirements.txt`, `README.md` |

### Fig. 1 panels
- **(a)** Canada and provinces in EPSG:3978, with Alberta highlighted, the study-area rectangle, Fort McMurray, and faint graticules labelled inline.
- **(b)** All 12 stations in UTM 12N, with Athabasca River and lakes, the 21 frozen pairs as thin grey lines, Fort McMurray, a scale bar, a north arrow, and a box showing the extent of (c).
- **(c)** Enlarged core cluster with all station labels.

The 21 lines would crowd (b), so the zoom panel was added, as the brief allowed.

## Data sources
- **Methane:** WBEA hourly CH4 exports (development panel 2021-2025; sealed confirmation panel Jan-Sep 2026, used here only to describe data availability), with validity codes Z, C and '.'.
- **Station coordinates:** `metadata/stations_official_2024.csv` (WBEA 2024 site documents).
- **Station pairs:** `experiments/E08_confirmation/confirmation_2026/h2_pairs.csv` (frozen).
- **Map layers:** Natural Earth 1:50m and 1:10m, from the official GitHub mirror.
- **Station variables:** non-empty columns of the WBEA exports.
- **Table 2 dates and definitions:** frozen protocol, decision log and WBEA official documents (monthly report Sep 2024; SOP-ANA-008).

## Validation: 15/15 automated checks pass (`validation_report.json`)
- **Coordinates:** exact match to metadata.
- **Pairs:** identical to the frozen list and to an independent recomputation of the <= 30 km rule on the 11 retained stations.
- **2026 completeness:** recomputed from hourly indicators, equal to the frozen E08 summary for all 12 stations (difference < 5e-5; frozen stored to 4 dp). AMS 2 = 41.2% is the only station below 50%.
- **Time handling:** 273 and 1,796 days with 24 hours each (hour-ending MST; the 00:00 value is assigned to the previous day); valid + Z + C + '.' + other = 24 for every station-day.
- **Missing values:** no coded hour carries a numeric value; no CH4 <= 0.
- **Figure files:** all PDFs are vector with embedded fonts and contain no raster images; SVG text is kept as text; PNGs are 600 dpi.
- **Tables:** booktabs, no vertical lines, no experiment identifiers or result language.

Visual inspection was done on the renders. Several layout problems were found and fixed before delivery (clipped labels, overlapping scale bar, colliding text, axis titles inserted by GeoPandas).

## Scientific decisions worth reviewing
1. **"Excluded" applies only to 2026.** AMS 2 had 92.5% coverage in 2021-2025 and was used in development (27 pairs). Fig. S1 therefore does not label it excluded, and the Fig. 1 caption states that the 21 pairs refer to the confirmation analysis.
2. **Availability classes are set by valid hours per day (0, 1-11, 12-22, 23-24),** not by percentage bins with a "complete" class. A full 24/24 day occurs on 0 of 3,276 station-days in 2026 and 23 of 21,552 in 2021-2025, because of the daily zero/span hour. A "complete" class would have misled readers.
3. **Instrument information is limited to what is verified.** The analyser model is given only for AMS 5; all stations are described by the SOP-level measurement principle.

## Unresolved issues (need your decision or additional sources)
1. **Athabasca oil sands region boundary.** No official polygon (for example from the Alberta Energy Regulator or Alberta's Oil Sands Areas GIS layer) could be retrieved from this environment, so none is drawn. The panel shows the study-area extent instead. If you supply the official layer, it can be added in a few minutes.
2. **Station relocations** before 2024 are not verified; only 2024 site documents were used.
3. **Typography.** DejaVu Sans, fully embedded, is used because Arial or Helvetica (and the Liberation Sans substitute) could not be installed here. Elsevier accepts it; switching requires only the font name in `common.py` on a machine with Arial.
4. **Fig. 1 has no single-column version.** Three map panels are not legible at 90 mm. A 90 mm version of panel (c) alone could be made if needed.
5. **Natural Earth river detail is coarse.** Only the Athabasca River is present at 1:10m; the Clearwater River is not shown.

## Repository note
`.gitignore` excludes all `*.pdf` files and every `data/` directory, safeguards for WBEA data and copyrighted papers. Two scoped exceptions were added so that the manuscript PDFs and derived availability counts can be committed: `!manuscript/figures/**/*.pdf` and `!manuscript/data/`. Raw WBEA data (`data/dev`, `sealed/`) and reference PDFs (`literature/pdf`) remain ignored (verified). The derived files contain daily counts of valid hours and validity codes, not methane concentrations.

---
# Revision 2 (editorial and presentation revision, 2026-11-11)
Validated data, the frozen pair list and all experimental results are unchanged. v1 figures, tables and scripts are preserved (`figures/section2/archive_v1/`, `tables/section2/archive_v1/`, `scripts/section2/make_fig0*_v1.py`).

## What changed
| Item | Revision |
|---|---|
| Fig. 1 | One coherent UTM 12N map (92 x 149 mm map area) with a compact, unlabelled location inset; no titles or panel labels; 7 pt station labels; all 21 frozen pairs; AMS 18 shown by an off-map position note; simplified 6-entry legend. Exact 180.0 x 158.0 mm |
| Fig. 2 | Same data and daily classes; exact 180.0 x 70.0 mm; legend gives hours and proportion of the day; label clipping fixed. 90 mm variant: 90.0 x 92.0 mm |
| Fig. S1 | Daily version retained (180.0 x 70.0 mm). New monthly option **S1b** (180.0 x 66.0 mm), recommended for readability |
| Table 1 | `table*` full width; station, name, verified coordinates, wind and temperature heights; instrument note limited to verified statements (co-reported THC/CH4/NMHC at all 12 stations, checked in the exports; daily zero/span per SOP-ANA-008 and monthly reports; Thermo 55i only for AMS 5; Sep 2024 analyser replacements at AMS 5 and AMS 23) |
| Table 2 | Simplified: datasets (variables, source, resolution, years) and temporal partitions (dates, use), with a timestamp-convention note. Selection and preprocessing rules moved to `tables/section2/METHODS_NOTES_moved_from_Table2.md` |
| LaTeX check | Compiled in Elsevier CAS double column (`cas-dc` 2.3, from the official template via a public GitHub mirror) with figures and tables: **0 errors, 0 overfull boxes** (after fixing an initial 313 pt overflow in Table 2 by switching to `tabularx`). PDF in `latex_check/` |
| Relocations | `data/section2/STATION_RELOCATION_CHECK.md`: AMS 1 (est. 1997) and AMS 23 (est. 2017) predate the study, with no relocation mentioned; the other 10 stations could not be verified here (documents too large to retrieve). Download steps and suggested manuscript wording given |
| Comparison | `figures/section2/FIGURE_REVISION_COMPARISON.md`: exact v1 vs v2 dimensions and final checklist |
| Validation | 26/26 automated checks pass (exact sizes, text inside page, no panel labels, vector/fonts, data checks) |

## Remaining limitations
- Station relocation history incomplete (10 of 12 stations).
- No oil sands region polygon (official layer not available here).
- DejaVu Sans font (Arial not available).
- CAS `\textwidth` is 174.5 mm, so 180 mm figures print at 97%. Producing them at exactly 174.5 mm would avoid scaling if preferred.

---
# Revision 3: FINAL (consolidated specification; supersedes revision 2)
- **Fig. 1:** all three original map components restored (regional context, full network, enlarged cluster), with no panel letters and no internal titles. Exactly 174.5 x 118.0 mm, the CAS `\textwidth`, so it prints at 100%. All 12 stations and all 21 frozen pairs appear on both network maps (automated component inventory). The revision-2 single-map version is archived (`archive_v2/`), not used.
- **Fig. 2:** unchanged design and data at 174.5 x 70.0 mm. A PDF rendering defect (hairline seams between daily cells at screen resolution) is fixed without changing data.
- **Fig. S1:** original daily version retained (174.5 x 70.0 mm), plus a clearly labelled ALTERNATIVE monthly version (174.5 x 66.0 mm; aggregation = valid / total hours per month; no interpolation).
- **Table 1:** unchanged from revision 2 (`table*`, verified content).
- **Table 2:** adds descriptive data-availability ranges per temporal partition: development 90.6-94.2%, reference 90.1-94.3%, confirmation 81.5-95.1% excluding AMS 2 at 41.2%.
  - Corrected reference-period end to **31 Dec 2023 23:00**, matching the frozen selection `.loc["2021":"2023"]` (26,279 h). Under hour-ending, the 1 Jan 2024 00:00 value, which belongs to 31 Dec, is not in the reference set. This is a one-hour subtlety worth stating in Methods.
- **Validation:** 30/30 checks (components, data hashes, frozen files, dimensions, text bounds, panel letters, fonts, vector). CAS double-column compile with `figure*` at `\textwidth`: 0 errors, 0 overfull boxes; pages rendered and inspected.
- **Remaining limitations (unchanged):** relocation history incomplete for 10 stations; no oil sands polygon; DejaVu Sans font; the optional single-column Fig. 2 remains 90 mm.

---
# Revision 4: combined Fig. 2 and manuscript placement (final)
- **Fig. 2 (combined), `fig02_ch4_availability.{pdf,svg}` + `_600dpi.png`:** 174.50 x 155.00 mm (CAS `\textwidth`).
  - Upper: monthly 2021-2025 (12 x 59). Middle: daily 2021-2025 (12 x 1,796). Lower: daily Jan-Sep 2026 (12 x 273).
  - One completeness definition for all three: 100 x valid hourly CH4 / hours in the cell. The monthly values are verified to equal aggregation of the same daily records.
  - Continuous **cividis** 0-100% with one shared, labelled vector colour bar, marking 23/24 h (normal operation with the daily zero/span hour).
  - Station identifiers and time axes on all plots. No titles or panel letters (the caption describes the upper, middle and lower plots). Right-hand period percentages shown for 2021-2025 and 2026 only, avoiding duplication. AMS 2 marked † in the 2026 plot.
  - Fully vector: 0 embedded raster images. The default Matplotlib colour bar embedded a bitmap, so it was replaced by 256 vector cells.
  - Script: `scripts/section2/make_fig02_combined.py`.
- **Individual availability figures:** archived (`figures/section2/archive_v3_individual/`). Script retained as `make_fig02_individual.py`, writing to the archive. Source daily data unchanged (SHA-256 verified).
- **Fig. 1:** unchanged (three components, no letters, 174.5 x 118.0 mm).
- **LaTeX placement:** representative full-length CAS document `latex_check/manuscript_check.{tex,pdf}` (Sections 1-3, both `figure*[!t]` declared right after their first citation, both `table*`, `\usepackage[section]{placeins}` plus `\FloatBarrier`, `\clearpage` before References, bibliography).
  - Result: 0 errors, 0 overfull boxes, 6 pages.
  - Pages (from `.aux`): Fig. 1 p.2, Table 1 p.2, Table 2 p.3, Fig. 2 p.4, References p.6. **All floats precede the References.** Fig. 2 and its caption fit on one page.
  - Reusable snippet: `latex_check/FIGURE_PLACEMENT_SNIPPET.tex`.
- **Validation:** 24/24 automated checks pass (`data/section2/validation_report.json`), including combined-figure components, same completeness definition, floats-before-references, exact sizes, text inside page, no panel letters, embedded fonts, no raster, data hashes and frozen files.
