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
