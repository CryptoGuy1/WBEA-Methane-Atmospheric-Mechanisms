# Fig. 6 verification: meteorological-regime composition of methane-excursion changes
Plotting only. No H3 calculation was rerun or changed; no experiment, result or frozen file was modified. Script: `manuscript/scripts/section4/make_fig06_meteorological_composition.py`; every check below is asserted in the script before plotting.
Outputs: `fig06_meteorological_composition.{pdf,svg}` (vector, 0 raster images, fonts embedded), `.png` and `.tiff` (600 dpi; TIFF LZW). Size 174.5 x 132.0 mm; all text inside the page; panel letters (a)-(c) only; no titles or experiment codes.

## Conversion and identity
- Saved contrasts are fractional rate changes; all plotted values are **x 100 = percentage points (pp)**.
- **Decomposition identity t = c + w:** verified from the frozen code (`wbea.e08.kitagawa_groups`: composition = sum (p_a - p_b)(q_a + q_b)/2; within = sum (p_a + p_b)(q_a - q_b)/2; total = rate_a - rate_b) and numerically, max abs(c + w - t) = 1.0e-6 in both sets (6-dp CSV rounding).
- **Sign convention:** development contrasts are later minus earlier year; confirmation contrasts are 2026 minus each development year.

## (a) Development: `experiments/E07_composition_decomposition/results/h3_contrasts_primary.csv`
- **All 120** station-year contrasts (12 stations x 10 year pairs, Jan-Nov 2021-2025): c on x, w on y.
- **Ranges:** c -1.94 to 1.04 pp; w -6.12 to 9.18 pp.
- **Mean abs(c) = 0.454 pp** (approx. 0.45) and **mean abs(w) = 1.613 pp** (approx. 1.61).
- Equal scales on both axes (-10 to 10 pp), so relative magnitudes are shown honestly. No fitted line; the deweathering baseline is not used.

## (b) 2026 confirmation: `experiments/E08_confirmation/confirmation_2026/h3_contrasts.csv`
- **All 55** contrasts, all estimable (`e08_results.json`: `contrasts_estimable` = 55).
- **AMS 18 (5 contrasts, orange diamonds):** c -0.16 to 1.16 pp; w 38.22 to 46.68 pp.
- **Other 50 (blue):** c -2.04 to 0.59 pp; w -4.53 to 11.66 pp.
- **Main axes:** x -10 to 10 pp (same as a), y -10 to 50 pp.
- **Inset:** the same 50 non-AMS-18 observations (no exclusion or transformation), x -2.5 to 1.5 and y -6 to 12.5 pp, matching the dotted box. All 50 lie inside it (asserted). Linear axes; no per-contrast intervals (none exist).

## (c) Post-confirmation exploratory diagnostic: `experiments/E08_post_confirmation_exploratory/results/h3_2026_denominator_by_station.csv`
Share of each station in the denominator sum_k t_k^2 of the registered projection-share estimator, plotted in descending order. Recomputed from `h3_contrasts.csv`: matches the saved shares within 1e-5; recomputed shares sum to 1.0 (saved file 1.00001 from 5-dp rounding).

| Station | sum t^2 | Denominator share |
|---|---|---|
| AMS 18 | 0.91470 | 92.93% |
| AMS 9 | 0.03570 | 3.63% |
| AMS 1 | 0.00961 | 0.98% |
| AMS 23 | 0.00603 | 0.61% |
| AMS 7 | 0.00528 | 0.54% |
| AMS 14 | 0.00357 | 0.36% |
| AMS 30 | 0.00299 | 0.30% |
| AMS 11 | 0.00290 | 0.29% |
| AMS 6 | 0.00289 | 0.29% |
| AMS 13 | 0.00036 | 0.04% |
| AMS 5 | 0.00023 | 0.02% |

The axis label marks the panel as a post-confirmation diagnostic. It is not part of the frozen confirmation decision. Linear axis from 0 to 100%, untruncated.

## Required scientific checks
1. **Development pooled H3 (Jan-Nov):** 0.0269 (-0.0396 to 0.1264), from `h3_sensitivity.csv`.
2. **Matched Jan-Sep development:** 0.0261 (-0.0284 to 0.1238), from `PRE_E08/results/h3_jan_sep_benchmark.csv`.
3. **Registered 2026:** 0.0110 (-0.0199 to 0.0428), from `e08_results.json`.
4. **55/55 confirmation contrasts evaluable;** 0% non-estimable bootstrap replicates.
5. **AMS 18 share of the 2026 denominator:** 92.93%.
6. **AMS 18 share in matched development Jan-Sep:** 39.05%.
7. **Excluding AMS 18 (exploratory point only, no interval):** -0.0852, also recomputed from the contrasts.
8. **Six-regime descriptive sensitivity:** 0.0123 (-0.0214 to 0.0416), from `descriptive_results.json`.

## Source inconsistencies and compromises
- **Registered share, two decimal-precision versions:** `e08_results.json` gives 0.011018334786; `h3_weight_concentration.json` gives 0.011018148677 (recomputed from the 6-dp contrast CSV; difference 1.9e-7). **The registered value is authoritative.**
- **Superseded labels:** `h3_sensitivity.csv` still uses "Manski lower/upper" (now "extreme missing-outcome scenarios"). These rows are not plotted.
- **Different scales:** panels (a) and (b) share the x scale but not the y scale. The AMS 18 values (up to 46.7 pp) would otherwise compress the development cloud; the caption should note this.
- No statistical calculations or results were changed.
