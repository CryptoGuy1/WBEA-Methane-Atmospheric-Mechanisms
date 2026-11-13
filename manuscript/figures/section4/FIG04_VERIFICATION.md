# Fig. 4 verification: Atmospheric stability and regional methane variability
Plotting only. No model refitted, no saved result altered, no frozen file modified. Script: `manuscript/scripts/section4/make_fig04_stability_results.py`; it asserts every plotted value against its source file before drawing.
Outputs: `fig04_stability_results.{pdf,svg}` (vector, fonts embedded, 0 raster images), `_600dpi.png`, `_600dpi.tiff` (LZW). Size 174.5 x 64.0 mm (CAS `\textwidth`); all text inside the page; panel labels (a)-(c) only; no subplot titles; no experiment codes.

## Panel (a): adjusted stability-response relationship
| Element | Source | Transformation |
|---|---|---|
| Linear effect | `experiments/E04_stability_elasticity/results/h1_functional_form.csv`, `linear_effect_ppm` | None (= 0.04752 x S; slope checked against the pooled estimate) |
| Piecewise-linear spline | same file, `spline_effect_ppm` (knots at the 10/30/50/70/90% quantiles of adjusted S, per `run_e04.py`) | None |

**Not reproduced: original partial-residual hexbin and 25 quantile-bin means.** `run_e04.py` (lines 148-153) computes the residuals `rl_s`, `rl_y` at plot time and never saves them. They are not in any results file. They were not digitised from the old PNG and not recomputed.

**Proposed plotting-only extraction (NOT executed; requires authorisation):** re-run only the existing E04 residualisation code path on the development panel (cell demeaning plus log-wind partialling, identical specification) and save `rl_s`, `rl_y` and the 25 quantile-bin means to a new file. No model or estimate would change. The original hexbin and bin means could then be restored to panel (a).

## Panel (b): development and independent confirmation
| Row | Source | Estimate (95% CI) | n hours |
|---|---|---|---|
| 2021 | `h1_estimates.csv` "Direct, 2021" | 0.05859 (0.04550-0.06940) | 8,270 |
| 2022 | "Direct, 2022" | 0.03724 (0.02895-0.04718) | 8,091 |
| 2023 | "Direct, 2023" | 0.04418 (0.03349-0.05142) | 8,088 |
| 2024 | "Direct, 2024" | 0.05082 (0.03683-0.06556) | 8,288 |
| 2025 | "Direct, 2025" | 0.04851 (0.03435-0.06367) | 7,597 |
| Pooled development (shaded band = its CI) | "Direct (with log wind)" | 0.04752 (0.04106-0.05203) | 40,334 |
| 2026 confirmation | `experiments/E08_confirmation/confirmation_2026/e08_results.json` H1 `b1_primary`, `b1_primary_ci` | 0.05204 (0.03906-0.06948) | 4,472 |
Intervals: 14-day block-bootstrap percentile 95% CIs as saved (2,000 replicates). No transformation.

## Panel (c): joint negative-control model
| Period | Next-day coefficient (95% CI) | Contemporaneous joint coefficient | Threshold -0.5 x joint | Source |
|---|---|---|---|---|
| Development 2021-2025 | -0.00004 (-0.00477 to 0.00264) | 0.04747 (0.04140-0.05230) | -0.0237 | `h1_estimates.csv` negative-control rows (n = 40,201) |
| 2026 | -0.01872 (-0.02684 to -0.00508) | 0.05462 (**no interval saved**) | -0.0273 | `e08_results.json` `b_nc`, `b_nc_ci`, `b1_joint` (n = 4,401) |
The threshold uses the **joint-model** contemporaneous coefficient, not the primary H1 coefficient. The 2026 next-day point (-0.0187) lies inside the threshold, so the registered rule is not triggered; its lower bound (-0.0268) approaches -0.0273.

## Required verifications
1. **Development pooled H1:** 0.04752 (0.04106-0.05203), matching all reports ("0.048 (0.041-0.052)").
2. **Annual 2021-2025:** as tabulated above, matching `h1_estimates.csv` exactly (asserted in the script).
3. **2026 H1:** 0.05204 (0.03906-0.06948), matching `e08_results.json` and all reports ("0.052 (0.039-0.069)").
4. **Next-day coefficients:** development -0.00004 (-0.00477 to 0.00264) vs 2026 -0.01872 (-0.02684 to -0.00508).
5. **2026 comparison against the joint contemporaneous coefficient:** abs(-0.01872) / 0.05462 = 0.343 < 0.5. This matches the saved `ratio_nc` = -0.34276.

## Disagreements and caveats found (not silently resolved)
- **2026 next-day CI exists in two versions.** The registered value (2,000 replicates) is -0.0268 to -0.0051. The post-confirmation diagnostic (`h1_nc_covariance_by_period.csv`, 300 replicates) gives -0.0265 to -0.0036. **The registered value is plotted.**
- **No saved interval for the 2026 contemporaneous joint coefficient.** The E08 runner saved only the point. It is drawn as a hollow point without a bar; the caption must state this.
- **Windows and networks differ.** Annual and pooled development estimates use full calendar years (2025 to 2 Dec) and 7 core stations. The 2026 estimate uses Jan-Sep and 6 core stations (AMS 2 excluded). Jan-Sep development-year point estimates exist (`h1_nc_covariance_by_period.csv`: 0.057, 0.0295, 0.0411, 0.0496, 0.0437) but without saved CIs, so the registered annual rows are plotted.
- **Sample sizes differ within the development joint model:** 40,201 vs 40,334 in the primary model, because S(t+24) must be available. This is expected, not an error.

---
## Revision 2 (presentation only; no values changed)
- **(a)** Legend now reads "Linear fit" and "Piecewise-linear spline". **Observational layer not restored: the partial-residual observations are unavailable.** All branches and local files were re-searched: E04 saved only `h1_functional_form.csv` (curves), `baseline_rf_partial_dependence.csv`, estimates and summary tables. `run_e04.py` computes `rl_s`/`rl_y` at plot time without saving them. Restoring the layer requires the plotting-only extraction proposed above (not executed; awaiting authorisation).
- **(b)** Re-checked against `h1_estimates.csv` and `e08_results.json`; no numerical or formatting error found; unchanged.
- **(c)** Contemporaneous joint-model intervals: **development available** (0.04747, 0.04140-0.05230; `h1_estimates.csv`) and plotted; **2026 unavailable**. `e08_results.json` holds only the point `b1_joint` = 0.05462 (keys: `n_joint`, `b1_joint`), and `h1_nc_covariance_by_period.csv` also holds only points. The 2026 point remains a hollow marker without a bar.
- **(c)** Dotted ticks are now labelled in the legend as the criterion $-0.5|\hat\beta_S^{NC}|$, using the period-specific joint-model coefficient: development -0.0237, 2026 -0.0273. They illustrate the registered magnitude criterion for a negative next-day coefficient and are not uncertainty intervals. The panel remained uncrowded, so the markers are retained.
- Checks: PDF 174.5 x 64.0 mm; all text inside the page; 0 raster images; fonts embedded; PNG and TIFF at 600 dpi (TIFF LZW).
