# Supplementary publication assets
Figures S1-S23, tables TS1-TS14 and provenance manifests for the Supplementary Information (EMS). Built on branch `publication/supplementary-assets`.
**Not included yet:** `supplementary.tex` and the compiled PDF.

## Layout
- **`figures/`:** `figSNN_*.{pdf,svg,png}`. PDF/SVG are vector; PNG is 600 dpi.
- **`tables/`:** `TS1.tex` … `TS14.tex` (booktabs + longtable; need `booktabs`, `longtable`, `array`).
- **`scripts/`:**
  - `pubstyle.py`: style and read-only data access;
  - `make_figs_s01_s09.py`, `make_figs_s10_s21.py`: figures;
  - `make_tables.py`: tables;
  - `extract_e01_windrose_sectors.py`: S1 wind-rose aggregates;
  - `build_publication_manifests.py`: manifests.
- **`data/`:** `figS01_windrose_sectors.csv`, aggregate sector frequencies only.
- **Manifests:** `figure_manifest.csv`, `table_manifest.csv`, `evidence_manifest.csv` (per-input source commits; SHA-256 of every output).
- **Reports:** `FIGURE_CORRECTIONS_REPORT.md`, `PUBLICATION_ASSET_QA.md`.

## Sources and reproduction
- **Experiment results:** read with `git show` from the pinned commit `1788301` (`research/e15-h2-matched-pair-comparability`).
- **Manuscript inputs:** read from `b61ffbf` (`manuscript/section2-figures-tables`).
- **Reproduce:** `python scripts/make_figs_s01_s09.py && python scripts/make_figs_s10_s21.py && python scripts/make_tables.py && python scripts/build_publication_manifests.py`.
- **Data dependencies:** S1 needs local WBEA development data only to re-extract its aggregates. S6 needs the authorised, uncommitted residual extraction file. WBEA hourly data are not distributed.
