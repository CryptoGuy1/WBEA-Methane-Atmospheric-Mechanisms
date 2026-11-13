# Fig. 7 verification: synthetic calibration, detection power and falsification
Plotting only. No simulation was rerun and no test, result or classification changed. No branch was merged: the E12 files are read with `git show research/e12-h2-null-calibration:...`. Script: `manuscript/scripts/section4/make_fig07_h2_calibration_falsification.py`; every value is asserted before plotting.
Outputs: `fig07_h2_calibration_falsification.{pdf,svg}` (vector, 0 raster images, fonts embedded), `.png` and `.tiff` (600 dpi; TIFF LZW). Size 174.5 x 118.0 mm; all text inside the page; panel letters (a)-(d) only; no titles and no internal scenario codes (checked in the PDF text layer).

## Source: `results/summary_by_scenario_method.csv` and `results/verdicts.json` (E12 branch)
Rates are plotted as rate x 100. Wilson limits are the saved values; each was also re-derived from the saved counts (z = 1.96) and agrees within 1e-6.

| Panel | Internal ID / method / role | Display label | n | Rejections | % | Wilson 95% CI (%) | Registered classification | Median D |
|---|---|---|---|---|---|---|---|---|
| (a) | `N0` / primary / Q1 null calibration | Baseline null | 500 | 23 | 4.6 | 3.0845-6.8078 | calibrated | 0.0008 |
| (a) | `N1a` / primary / Q1 null calibration | Wind-independent delayed common driver | 500 | 27 | 5.4 | 3.7374-7.7427 | inconclusive | 0.0005 |
| (a) | `N2a` / primary / Q1 null calibration | Seasonal drift | 500 | 24 | 4.8 | 3.2465-7.0427 | calibrated | 0.0001 |
| (a) | `N3` / primary / Q1 null calibration | Strong autocorrelation, diurnal structure, missingness | 500 | 23 | 4.6 | 3.0845-6.8078 | calibrated | 0.0004 |
| (b) | `N2b` / primary / Q2 seasonal confounding | Seasonal confounding: whole-period shifts (frozen test) | 500 | 119 | 23.8 | 20.2759-27.7236 | inflated | 0.0123 |
| (b) | `N2b` / within-season shift / Q2 seasonal confounding | Seasonal confounding: within-season shifts (exploratory) | 500 | 26 | 5.2 | 3.5730-7.5101 | inconclusive | 0.0194 |
| (b) | `N2b` / truncated shift / Q2 seasonal confounding | Seasonal confounding: truncated shifts (exploratory) | 500 | 34 | 6.8 | 4.9067-9.3521 | inconclusive | 0.0146 |
| (c) | `N1a` / primary / Q1 null calibration | Wind-independent delayed common driver (statistical null) | 500 | 27 | 5.4 | 3.7374-7.7427 | inconclusive | 0.0005 |
| (c) | `N1b` / primary / Q4 falsification | Wind-advected shared driver, no methane transfer (physical falsification) | 200 | 200 | 100.0 | 98.1155-100.0000 | n/a (falsification) | 0.1318 |
| (d) | `P1_t007` / primary / Q3 power | Fixed 1-h lag, lower amplitude | 200 | 200 | 100.0 | 98.1155-100.0000 | adequate power | 0.0686 |
| (d) | `P1_t013` / primary / Q3 power | Fixed 1-h lag, intermediate amplitude | 200 | 200 | 100.0 | 98.1155-100.0000 | adequate power | 0.1307 |
| (d) | `P1_ceiling` / primary / Q3 power | Fixed 1-h lag, high amplitude | 200 | 200 | 100.0 | 98.1155-100.0000 | adequate power | 0.1953 |
| (d) | `P1_L2` / primary / Q3 power | Fixed 2-h lag | 200 | 200 | 100.0 | 98.1155-100.0000 | adequate power | 0.1078 |
| (d) | `P1_L3` / primary / Q3 power | Fixed 3-h lag | 200 | 0 | 0.0 | 0.0000-1.8845 | limited power | -0.0398 |
| (d) | `P1T_t013` / primary / Q3 power | Transit-dependent lag, intermediate amplitude | 200 | 200 | 100.0 | 98.1155-100.0000 | adequate power | 0.1307 |
| (d) | `P1T_ceiling` / primary / Q3 power | Transit-dependent lag, high amplitude | 200 | 200 | 100.0 | 98.1155-100.0000 | adequate power | 0.1768 |

## Required confirmations
- **Production:** 4100 replicates (4 x 500 calibration nulls + 500 seasonal confounding + 200 falsification + 7 x 200 positive controls). All 4,100 rows are present in the 13 raw files, `total_not_evaluable` = 0, and `production_log.txt` records every scenario as completed (0 failures).
- **Calibration nulls:** 4.6%, 5.4%, 4.8% and 4.6%. **Overall null calibration: inconclusive**, because the delayed-common-driver upper Wilson bound (7.7427%) exceeds the prespecified 7.5% margin. Panel (a) shows the 7.5% margin as a dotted line and each row's registered classification.
- **Seasonal confounding:** whole-period 23.8% (inflated); within-season 5.2% and truncated 6.8%, both **inconclusive** (upper bounds 7.51% and 9.35% exceed 7.5%). The alternatives are drawn with open markers and labelled exploratory.
- **Falsification:** the wind-advected shared driver is rejected 100% (200/200).
- **Power:** the fixed 3-h lag has 0% detection (median D = -0.0398); the other six configurations have 100%. Power at D >= 0.21: "inconclusive: not testable with the tested coupling models (DEVIATIONS D4)". The panel does not extend claims beyond D = 0.195.

## Interpretation safeguards (for the caption)
- **(b)** The 23.8% is the rejection rate in one constructed seasonal-confounding simulation, not an estimated false-positive rate for the WBEA network.
- **(c)** The wind-independent delayed common driver is a **statistical null** for the wind-shift test. The wind-advected shared driver is a **physical-specificity falsification scenario**: it deliberately contains wind-dependent structure but no inter-station methane transfer, so it is not a null of the wind-shift test. Its 100% rejection shows the test cannot distinguish wind-advected shared signals from methane transfer. It does not imply such a driver exists in the WBEA data.
- **(d)** The seven points are discrete simulation conditions. No curve is drawn and nothing is interpolated.

## Visual compromises found at publication width
- Wilson intervals at 0% and 100% (e.g. 0-1.88% and 98.1-100%) and the delayed-driver interval in (c) (3.7-7.7% on a 0-100% axis) are drawn but are narrower than the markers. This is correct, not an omission.
- In (d), the fixed 1-h intermediate (D = 0.1307) and transit-dependent intermediate (D = 0.1307) configurations coincide; they are distinguished by marker shape (filled circle inside an open diamond), not by any offset. No values were shifted.
- Panel (c) axis extends to 104% so the 100% marker is not clipped; ticks and the axis spine stop at 100%.
