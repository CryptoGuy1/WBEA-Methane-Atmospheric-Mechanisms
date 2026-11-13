# Verification: meteorological-regime heatmap of methane-excursion frequency
**Development-period descriptive figure (2021-01-01 to 2025-12-02, 12 stations). It is not an independent 2026 confirmation result.** The frequencies are unadjusted observational excursion frequencies, not causal effects of stability or wind and not emission rates.
Plotting only. No rate was recalculated from raw observations, and the E03 experiment, frozen protocol, E08 confirmation and existing figures are unchanged.
Script: `manuscript/scripts/section4/make_fig_meteorological_regime_heatmap.py`. Plotted values: `fig_meteorological_regime_heatmap_values.json`.
Outputs: `fig_meteorological_regime_heatmap.{pdf,svg}` (fully vector: cells, colour bar (256 vector segments), text and separators; 0 raster images; fonts embedded), `.png` and `.tiff` (600 dpi; TIFF LZW). Size 174.5 x 83.0 mm (2.10:1); all text inside the page; panel letters (a), (b) only; no titles or experiment codes.

## Source and definitions (verified in `run_e03.py`, lines 77-93)
- **Authoritative table:** `experiments/E03_excursion_patterns/results/q4_regime_table.csv`; 18 rows, exactly one per stability x wind x solar combination.
- **Stability:** AMS 5 T90 - T20, terciles with fixed 2021-2023 cut points t1 = -0.6 degC and t2 = 0.0 degC (`stability_tercile_cutpoints_degC.csv`); unstable < t1 <= neutral < t2 <= stable (`np.digitize`).
- **Wind:** each station's composite wind speed, classes < 1, 1-2.5 and >= 2.5 m/s (`CFG["h3"]["wind_classes_ms"]`).
- **Night:** solar elevation <= 0 degrees.
- **Sample:** valid station-hours require valid CH4, stability and wind (`dropna`).
- **Outcome:** an excursion is CH4 above the station's fixed 2021-2023 P95; `rate_pct` = 100 x excursions / hours.

## Plotted matrices (rate_pct; cells show one decimal)
**(a) Daytime**
| Stability \ Wind (m/s) | <1 | 1-2.5 | >=2.5 |
|---|---|---|---|
| Unstable | 5.53% (shown 5.5%) | 2.48% (shown 2.5%) | 0.57% (shown 0.6%) |
| Neutral | 9.89% (shown 9.9%) | 5.65% (shown 5.7%) | 1.49% (shown 1.5%) |
| Stable | 18.28% (shown 18.3%) | 10.20% (shown 10.2%) | 4.09% (shown 4.1%) |

**(b) Nighttime**
| Stability \ Wind (m/s) | <1 | 1-2.5 | >=2.5 |
|---|---|---|---|
| Unstable | 6.77% (shown 6.8%) | 4.31% (shown 4.3%) | 1.64% (shown 1.6%) |
| Neutral | 8.90% (shown 8.9%) | 5.83% (shown 5.8%) | 1.92% (shown 1.9%) |
| Stable | 15.59% (shown 15.6%) | 9.76% (shown 9.8%) | 4.19% (shown 4.2%) |

**Colour scale:** one shared linear `cividis` scale from the observed minimum 0.57% to the maximum 18.28%, identical in both panels. Annotation colour is dark wherever its WCAG contrast is >= 4:1, otherwise white.

## Required checks (all asserted in the script)
- Stable / <1 / day = **18.28%**; stable / <1 / night = **15.59%**; unstable / >=2.5 / day = **0.57%**; unstable / >=2.5 / night = **1.64%**; neutral / <1 / day = **9.89%**; neutral / <1 / night = **8.90%**.
- Global minimum 0.57% and maximum 18.28%.
- Every cell is mapped by its regime name (stability|wind|solar), not by row position.

## Supporting counts (source table)
| Stability | Wind | Solar | Hours | Excursions | Share of hours (%) | Share of excursions (%) | Rate (%) |
|---|---|---|---|---|---|---|---|
| unstable | <1 | day | 7,484 | 414 | 1.59 | 1.72 | 5.53 |
| unstable | 1-2.5 | day | 41,608 | 1,031 | 8.82 | 4.29 | 2.48 |
| unstable | >=2.5 | day | 85,057 | 489 | 18.04 | 2.04 | 0.57 |
| neutral | <1 | day | 8,219 | 813 | 1.74 | 3.38 | 9.89 |
| neutral | 1-2.5 | day | 28,913 | 1,634 | 6.13 | 6.80 | 5.65 |
| neutral | >=2.5 | day | 37,226 | 554 | 7.89 | 2.31 | 1.49 |
| stable | <1 | day | 6,958 | 1,272 | 1.48 | 5.29 | 18.28 |
| stable | 1-2.5 | day | 18,163 | 1,853 | 3.85 | 7.71 | 10.20 |
| stable | >=2.5 | day | 11,895 | 487 | 2.52 | 2.03 | 4.09 |
| unstable | <1 | night | 2,230 | 151 | 0.47 | 0.63 | 6.77 |
| unstable | 1-2.5 | night | 8,245 | 355 | 1.75 | 1.48 | 4.31 |
| unstable | >=2.5 | night | 15,451 | 253 | 3.28 | 1.05 | 1.64 |
| neutral | <1 | night | 11,331 | 1,008 | 2.40 | 4.20 | 8.90 |
| neutral | 1-2.5 | night | 31,010 | 1,809 | 6.58 | 7.53 | 5.83 |
| neutral | >=2.5 | night | 41,564 | 800 | 8.81 | 3.33 | 1.92 |
| stable | <1 | night | 28,165 | 4,391 | 5.97 | 18.28 | 15.59 |
| stable | 1-2.5 | night | 54,269 | 5,299 | 11.51 | 22.05 | 9.76 |
| stable | >=2.5 | night | 33,731 | 1,414 | 7.15 | 5.89 | 4.19 |

Totals: 471,519 station-hours, 24,027 excursions (overall 5.10%). Internal consistency: each rate equals 100 x excursions / hours within 0.005 (2-dp rounding); both share columns recompute within 0.005 and sum to 99.98% and 100.01% (rounding).

## Discrepancies and caveats
- **No numerical discrepancies.** The six required values, the minimum and the maximum match the source exactly.
- **Rounding:** 0.57% is displayed as "0.6%" and 1.64% as "1.6%" because of the one-decimal display; the exact values are above.
- **Cell sizes are unequal.** Cells range from 2,230 hours (unstable / <1 / night) to 85,057 hours (unstable / >=2.5 / day). No uncertainty is shown, because none was computed for this table; the caption may mention the smallest cell size.
- **Population:** the development period includes AMS 2, which was later excluded from the 2026 confirmation.
- **Patterns (all 18 values preserved as observed):** in both panels, every row decreases monotonically with wind class and every column increases with stability class. The day/night contrast is not uniform: night exceeds day in six cells, but **day exceeds night in three**: stable / <1 (18.28 vs 15.59%), stable / 1-2.5 (10.20 vs 9.76%) and neutral / <1 (9.89 vs 8.90%). (An earlier draft of this report wrongly stated that the night-time cells were not monotone; corrected.)
