# E07 H3: meteorological composition of year-to-year changes in CH4 excursion rates

**Status:** exploratory (development data). **H3 as pre-registered (D-40): NOT SUPPORTED.** The pooled meteorology-mix share is small and its 95% CI includes zero. This is a substantive negative result.

## Question, estimand, assumptions
For each station and pair of years (Jan-Nov windows, 2021-2025; 120 contrasts), the change in P95 excursion rate is split exactly into a **meteorology-mix** term (change in the share of hours in each of 18 regimes) and a **within-regime** term (change in the excursion rate inside regimes). Pooled estimand: s = sum(c_k t_k) / sum(t_k^2), the share of between-year variation projected on the composition term. Regimes: AMS 5 stability tercile x station wind class x solar day/night. Working assumptions: conditional MAR for missing CH4 (bounded by Manski); regimes capture the relevant meteorology. **The within-regime term is not an emission change**: it absorbs background growth, instrument drift, local activity and meteorology not resolved by the regimes.

## Results
| Analysis | Share | 95% CI |
|---|---|---|
| **Primary** (raw P95, Jan-Nov 2021-2025, 1,000 joint block-bootstrap replicates) | **0.027** | **-0.040 to 0.126** |
| Manski lower / upper (missing CH4 as non-exceedance / exceedance) | 0.022 / 0.019 | - |
| Background-adjusted excess C - B_t (D-16) | -0.007 | -0.032 to 0.032 |
| PWIP hours excluded | 0.037 | -0.038 to 0.152 |
| Full calendar years 2021-2024 | 0.101 | -0.019 to 0.237 |
| Baseline: boosted-tree deweathering, implied meteorology share | 0.213 | - |

- **Size of the terms.** Mean absolute composition term 0.45 pp; within-regime 1.61 pp; total change 1.64 pp. The composition term was larger than the within-regime term in 23 of 120 contrasts.
- **Station heterogeneity (descriptive).** Per-station shares: AMS 5 0.47, AMS 13 0.26, AMS 11 0.25, AMS 2 0.23, AMS 1 0.13, AMS 6 0.10, AMS 7 0.11; near zero or negative at AMS 14 (0.04), AMS 30 (0.02), AMS 18 (-0.03) and AMS 23 (-0.08). Exploratory, post hoc split: the 8 oil-sands core stations give 0.17 (mean |total| 1.04 pp), the 4 others -0.01 (mean |total| 2.85 pp). The pooled estimand weights contrasts by squared total change, so the four stations with large changes dominate it.
- **Merging.** The 50 h rule merged regimes in 119 of 120 contrasts (8-16 groups typical; minimum 4).
- **Baselines.** The deweathered change correlates closely with the Kitagawa within-regime term (r = 0.94, 120 contrasts), but the deweathering model attributes more to meteorology (0.21). It uses continuous predictors including day of year and temperature, which the 18 regimes do not resolve.

## Decision (D-40)
| Criterion | Value | Met |
|---|---|---|
| 95% CI of pooled share excludes 0 | 0.027 (-0.040 to 0.126) | **no** |

## Interpretation (exploratory)
At the resolution of the pre-registered regimes, year-to-year changes in station excursion counts in this network are **not** mainly a reshuffling of stability and wind conditions. The largest changes occur at AMS 14, 18, 23 and 30 and are almost entirely within-regime. These four stations combine large changes with low P95 thresholds (AMS 18: 0.07 ppm above typical background), where small shifts in regional background or instrument baseline can move rates by several percentage points (E03). At the core stations, where changes are smaller, regime composition accounts for a larger share (descriptively about 10-47% by station). The richer deweathering model's higher share (0.21) shows the answer depends on how much meteorology is resolved. That is a methodological finding in its own right.

**Implication for monitoring (cautious):** raw changes in excursion counts at the low-threshold remote stations should not be read as weather artefacts, nor as emission changes, without first checking background drift and instrument records. Meteorology-normalised reporting adds most at the core stations.

## Limitations
- The share estimand is dominated by contrasts with large total change; it answers "how much of the overall variation", not "how much at a typical station".
- 18 coarse regimes, merged heavily; the wider gap with the deweathering baseline suggests unresolved meteorology (season within year, temperature, direction).
- Background adjustment (C - B_t) increases contrast variability (mean |total| 2.62 vs 1.64 pp), because the daily background estimate adds noise.
- 2021 and the Jan-Nov window: December, the highest-excursion month, is excluded from the primary analysis; including it (2021-2024 calendar years) raises the share to 0.10.

## E07 review checkpoint (meteorological composition and environmental implications)
Technical validation: Kitagawa identity holds by construction (`tests/test_v2_math.py`); merges logged (`h3_merge_log.csv`); bootstrap resamples blocks within years jointly across stations; Manski bounds bracket the primary closely (0.019-0.022), so missing data do not drive the result. **No material error.** Non-critical issues RB-21 to RB-25 are in the backlog for the integrated review; per policy, the estimand is not changed after seeing the result.

## Figures
Main Figure 9 (`figure09_composition_decomposition`). Supplementary S3 (`figureS3_baseline_comparison`: H1 fixed effects vs deweathering; H3 Kitagawa vs deweathering).
