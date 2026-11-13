# Fig. 5 verification: wind-conditioned directional coupling and lag diagnostics
Plotting only. No statistic recomputed beyond the frozen pooling of saved values; no experiment code, data or frozen output changed. Script: `manuscript/scripts/section4/make_fig05_directional_coupling_results.py`; every value below is asserted in the script before plotting.
Outputs: `fig05_directional_coupling_results.{pdf,svg}` (vector, 0 raster images, fonts embedded), `.png` and `.tiff` (600 dpi; TIFF LZW). Size 174.5 x 122.0 mm; all text inside the page; panel letters only; no titles or experiment codes.

## (a) Development pairwise statistics
- **Pairs:** 27, separation 2.66-27.32 km (`E05/results/h2_pair_statistics.csv`).
- **Values plotted:** observed `D` per pair, with error bars from the saved 95% 14-day block-bootstrap CIs (`ci_lo`, `ci_hi`; range -0.081 to 0.901). The intervals did not cause unreadable overplotting, so they are retained.
- **Grey ticks:** saved per-pair shifted-wind null 95th percentiles (`null_p95`). In development these came from 1,000 random whole-day shifts, not the 246 finite shifts used in confirmation.
- **Family-wise significance:** `p_maxT_familywise < 0.05` in **21/27** pairs (filled markers), matching `h2_pooled.csv` (`pairs_familywise_lt_05` = 21).
- **Pooled development statistic (caption only, not plotted):** **D = 0.1285 (95% CI 0.1084-0.15528)** from `h2_pooled.csv`. Earlier text rounded it to 0.128 and the old E05 figure to 0.129; 0.1285 is the saved value.

## (b) 2026 pairwise statistics
- **Pairs:** 21, from `h2_pairs.csv` and `h2_Dobs.npy` (equal to 5 dp). Order identical to `descriptive/h2_pairs_maxT.csv`.
- **Pair mapping:** all 21 identifiers found in the E05 pair table with the same orientation; separations taken from it:

| Pair | km | 2026 D |
|---|---|---|
| AMS 1->AMS 5 | 26.42 | 0.24398 |
| AMS 1->AMS 9 | 2.66 | 0.51465 |
| AMS 1->AMS 11 | 19.96 | 0.38215 |
| AMS 1->AMS 13 | 4.48 | 0.41246 |
| AMS 1->AMS 23 | 17.73 | 0.22503 |
| AMS 1->AMS 30 | 7.56 | 0.42317 |
| AMS 5->AMS 6 | 24.09 | 0.26653 |
| AMS 5->AMS 7 | 26.67 | 0.23098 |
| AMS 5->AMS 9 | 26.56 | 0.33232 |
| AMS 5->AMS 11 | 6.64 | 0.33199 |
| AMS 5->AMS 13 | 22.36 | 0.25120 |
| AMS 6->AMS 7 | 5.62 | 0.09784 |
| AMS 9->AMS 11 | 19.97 | 0.18970 |
| AMS 9->AMS 13 | 6.03 | 0.46201 |
| AMS 9->AMS 23 | 16.93 | 0.26934 |
| AMS 9->AMS 30 | 8.80 | 0.15702 |
| AMS 11->AMS 13 | 16.07 | 0.38394 |
| AMS 11->AMS 30 | 27.32 | 0.20930 |
| AMS 13->AMS 23 | 22.21 | 0.26116 |
| AMS 13->AMS 30 | 11.30 | 0.41091 |
| AMS 23->AMS 30 | 12.96 | 0.37019 |

- **Family-wise significance:** **14/21** pairs with `p_maxT_familywise < 0.05`.
- **No 2026 pair-level bootstrap CIs exist in the saved outputs; none are drawn.**
- **Grey ticks:** each pair's 95th percentile of its 246 saved shifted-wind values (column of `h2_null_matrix.npy`). These are null-reference quantiles, not confidence intervals.
- **Scales:** both panels share x 0-29 km and y -0.15 to 0.95. The full ranges fit: development values and CIs -0.081 to 0.901; 2026 values 0.098-0.515.

## (c) 2026 whole-period shifted-wind reference
- **Null matrix:** `h2_null_matrix.npy` has shape (246, 21). Rows are admissible whole-day shifts k = 14..259 in order; columns are pairs in `h2_pairs.csv` row order (`run_e08.py` lines 64-100: `Dnull[k-1, p]`).
- **Weights:** omega_p proportional to 1/Var_k(D_p^(k)), normalised, via the frozen `wbea.e08.pooled_inverse_null_variance`. They sum to 1 and match the CSV `weight` column to within 4.9e-06, the CSV's 5-dp rounding. Using the rounded CSV weights would give 0.2879322, so the exact frozen weights are used.
- **Observed pooled statistic:** **D = 0.2879317085**, identical to `e08_results.json`.
- **Reference:** 246 pooled surrogates; maximum 0.1007; **0 of 246 >= observed**; finite-reference **p = (1 + 0)/(246 + 1) = 1/247 = 0.0040486**, identical to the saved `p`.
- **Drawn:** histogram (bin width 0.01), observed value as a vertical line, zero reference. No smoothing and no confidence band.

## (d) Lag centroid vs nominal transit time
- **Development:** centroids from `E06/results/e06_observed_vs_reference_kernel.csv`, with bars showing the saved range over development years (`centroid_min_by_year`, `centroid_max_by_year`).
- **Reference boxes:** the saved signal-dominated simulated reference range (`ref_centroid_min`/`max`; A = 3 injections, both signal memories, all pairs; D-35). This is a **development-period reference**, not a confidence interval.
- **2026:** centroids from `e08_results.json` `centroids`. **No per-bin 2026 CIs exist.** Only the last-minus-first difference has a saved interval (0.744-1.539), which is reported in text, not drawn.

| Class | Development centroid (range over years) | Simulated reference range | Development inside reference? | 2026 centroid |
|---|---|---|---|---|
| 0-0.5 h | 0.2468 (0.2072-0.2833) | 0.1698-0.2980 | yes | 0.1295 |
| 0.5-1.0 h | 0.3848 (0.2732-0.4386) | 0.5799-0.9770 | no | 0.3490 |
| 1.0-1.5 h | 0.7255 (0.4927-1.1392) | 1.0000-1.1575 | no | 0.5605 |
| 1.5-2.0 h | 1.1102 (0.4738-1.5414) | 1.6506-1.9836 | no | 0.9751 |
| 2.0-3.0 h | 1.5126 (0.7684-2.0571) | 1.7028-2.2234 | no | 1.1180 |

- **Original kernel criterion: FAILED.** 1/5 development centroids lie within the reference range, where 4/5 were required.
- **Registered 2026 criterion:** ordered lag centroids (rho = 1.0 >= 0.9; difference CI excludes 0). It was met. **This is not agreement with the reference range**, and 2026 centroids also lie below the reference in classes 2-5. The figure does not imply that 2026 passed the kernel-matching criterion.
- **Dotted line (centroid = transit time):** a visual reference at bin midpoints (0.25, 0.75, 1.25, 1.75, 2.5 h), as in the original E06 figure.

## Inspection at publication width (174.5 mm)
- No clipping; all text inside the page (automated `pdftotext -bbox` check).
- **Minor marker overlap:** the 2026 points at 26.4-27.3 km and the development points at about 16 km and 26 km partly overlap but stay distinguishable. No values were shifted.
- **Remaining ambiguity:** the development and 2026 null ticks come from different reference constructions (1,000 random vs 246 finite shifts) and windows. The caption should say so.

---
## Editorial revision (final)
- **Removed** the in-panel labels "2021–2025, 27 pairs" (a) and "2026, 21 pairs" (b); these details belong in the caption.
- **Numerical values unchanged.** A pixel comparison of the old and new 600 dpi renders found exactly two changed regions, located where the two labels were; every data mark, tick, range, histogram bar and axis is pixel-identical. All plotted values are written to `fig05_plotted_values.json`.
- **Null-reference indicators correctly mapped**, checked by reading the plotted marker coordinates back from the figure:
  - (a) each tick lies at the same separation as its pair's observation and at that pair's saved `null_p95` (27/27, same row of `h2_pair_statistics.csv`);
  - (b) each tick lies at its pair's separation and equals the 95th percentile of the matching null-matrix column (21/21; column p = row p of `h2_pairs.csv`, as in `run_e08.py`);
  - every observation is drawn once at its own separation.
  The ticks remain null-reference thresholds, not confidence intervals.
- **(d)** Development year ranges (thin dark vertical bars) and the simulated reference ranges (light orange boxes) remain visually distinct; neither is labelled a confidence interval. The dotted centroid = transit-time diagonal remains a descriptive reference only.
- Exports: PDF 174.5 x 122.0 mm (vector, fonts embedded, 0 raster images), SVG, PNG and TIFF at 600 dpi; all text inside the page; inspected at 150 dpi print width with no clipping.

---
## Editorial revision 2
- **(a)** Legend entry now reads "95% block-bootstrap CI (2021–2025)". No legend added to (b).
- **(c)** Removed the three-line annotation (wind-shift count, exceedances, finite p); the blue observed line and "Observed D = 0.2879" are retained. The statistics (246 shifts; 0 of 246 >= observed; p = 1/247 = 0.0040486) move to the caption and Results text.
- **Numerical content unchanged:** `fig05_plotted_values.json` is identical to the previous version. A pixel comparison shows changes only in panel (a)'s legend (the shorter label narrows the right-anchored legend box, so its handles shift within the legend; no data marks move) and in the removed annotation area of (c).
- Exports: PDF 174.5 x 122.0 mm (vector, fonts embedded, 0 raster images), SVG, PNG and TIFF at 600 dpi.
