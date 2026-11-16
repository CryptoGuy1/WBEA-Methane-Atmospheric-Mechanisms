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

## Flowchart version (recommended): `fig03_flowchart.*`
- **Design:** a minimal-text flowchart following the model EMS papers. It shows the study timeline (development, frozen protocol, confirmation), the data, preprocessing, the H1-H3 estimators, the registered decisions and the post-confirmation checks.
- **Text:** 2-4 words per box; equations and decision rules stay in the Methods text and Supplement.
- **Format:** 174.5 x 74 mm; vector, 0 raster images; DejaVu Sans, matching Figures 4-7.
- **Accuracy:** content is consistent with the frozen protocol (estimators, timeline) and the Supplement sections. The more detailed schematic (`fig03_methods_schematic.*`) is kept as an alternative.

## Flowchart revision (after external AI review; each point checked before implementing)
1. **Shared preprocessing.** The review is correct that regional residualisation is H2-specific:
   - H2: leave-pair-out residuals (`src/wbea/h2.py`).
   - H1: network median of station anomalies centred on 2021-2023 medians (`run_e04.py`).
   - H3: station P95 excursion rates.

   The shared box now reads "Quality control + 2021-2023 reference values", the common element of all three (anomaly centring and stability standardisation for H1; anomalies for H2; P95 thresholds for H3). The review's wording, "Reference quantities", was refined for precision. "Leave-pair-out residuals" now appears in the H2 box.
2. **Estimands.** The review is correct that "shifted-wind test" names a procedure. Applied consistently to all three boxes, not only H2: estimand plus method (H1 "Stability association / regression"; H2 "Directional dependence / shifted-wind reference; leave-pair-out residuals"; H3 "Regime composition / rate decomposition").
3. **Confirmation path.** The review is correct. The dashed arrow from confirmation directly to the decisions is removed. Both data periods (2021-2025, Jan-Sep 2026) now enter the shared path, the frozen protocol feeds a dashed group around H1-H3 (procedures fixed), and "Registered decisions (2026)" follows from H1-H3.
