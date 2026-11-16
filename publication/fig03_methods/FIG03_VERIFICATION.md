# Figure 3 (methods schematic): verification
**Files:** `fig03_methods_schematic.pdf` and `.svg` (vector), `.png` (600 dpi). Size 174.5 x 112 mm (CAS text width).
**Script:** `make_fig03_methods_schematic.py`.
**Content:** text, equations and boxes only. No data plots, icons, photographs or generated imagery (0 raster images). It replaces the earlier AI-drawn Figure 3, which contained generated artwork and illustrative fake data.

## Every statement checked against the frozen record
- **Timeline:**
  - Development 2021-2025.
  - Protocol and code frozen at tag `protocol-freeze` (2b7c79e, 2026-11-11 00:30 UTC), before the single confirmation run at `e08-confirmation` (4c011a8, 00:36 UTC).
  - Confirmation window: Jan-Sep 2026.
- **H1:**
  - Model: Supplement Eq. S1 (7 core stations; standardisation on 2021-2023; log(U + 0.5)), verified in `run_e04.py`.
  - Bootstrap: 14-day blocks, 2,000 replicates (`config/project.toml`).
  - Decision rule, verbatim from `src/wbea/e08.py::h1_decision`: primary CI entirely above 0, and NOT [next-day CI excludes 0 AND |b_nc| >= 0.5 x joint-model coefficient].
- **H2:**
  - Statistic: Eqs. S2-S4.
  - Reference: all whole-day circular shifts, K = 246 in 2026.
  - Decision, from `run_e08.py`, all three criteria required: (i) p < 0.05; (ii) D > 0 under wind timing +1 h and -1 h; (iii) the lag-centroid ordering rule (`centroid_rule`).
- **H3:**
  - Statistic: Eq. S9 (projection share).
  - Regimes: 18 (stability x wind x day/night).
  - Decision, from `run_e08.py`: 95% CI excludes 0.
- **Post-confirmation checks:** mapped to Supplement Sections 8, 9.1-9.2, 9.3 and 10.

## Style
- DejaVu Sans, matching Figures 4-7; fonts embedded.
- Panel letters (a)-(c); no figure title.
- All text inside the page.
