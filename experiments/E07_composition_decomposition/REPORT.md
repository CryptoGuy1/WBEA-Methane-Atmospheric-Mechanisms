# E07 H3: meteorological composition of year-to-year changes in CH4 excursion rates

**Revised 2026-11-10 (E07-r1; see end).** **Status:** exploratory (development data). **H3 as pre-registered (D-40): NOT SUPPORTED.** The pooled meteorology-mix share is small and its 95% CI includes zero. This is a substantive negative result.

## Question, estimand, assumptions
For each station and pair of years (Jan-Nov windows, 2021-2025; 120 contrasts), the change in P95 excursion rate is split exactly into a **meteorology-mix** term (change in the share of hours in each of 18 regimes) and a **within-regime** term (change in the excursion rate inside regimes). Pooled estimand: s = sum(c_k t_k) / sum(t_k^2), the share of between-year variation projected on the composition term. Regimes: AMS 5 stability tercile x station wind class x solar day/night. Working assumptions: conditional MAR for missing CH4 (examined with extreme missing-outcome scenarios); regimes capture the relevant meteorology. **The within-regime term is not an emission change**: it absorbs background growth, instrument drift, local activity and meteorology not resolved by the regimes.

## Results
| Analysis | Share | 95% CI |
|---|---|---|
| **Primary** (raw P95, Jan-Nov 2021-2025, 1,000 joint block-bootstrap replicates) | **0.027** | **-0.040 to 0.126** |
| Extreme missing-outcome scenarios: all missing CH4 hours as non-exceedance / as exceedance (not bounds; see E07-r1) | 0.022 / 0.019 | - |
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

**Implication for monitoring (cautious):** raw changes in excursion counts at the low-threshold remote stations should not be read as weather artefacts, nor as emission changes, without first checking background drift and instrument records. (The earlier sentence claiming that meteorology-normalised reporting adds most at the core stations is withdrawn in E07-r1: no direct operational comparison was made.)

## Limitations
- The share estimand is dominated by contrasts with large total change; it answers "how much of the overall variation", not "how much at a typical station".
- 18 coarse regimes, merged heavily; the wider gap with the deweathering baseline suggests unresolved meteorology (season within year, temperature, direction).
- Background adjustment (C - B_t) increases contrast variability (mean |total| 2.62 vs 1.64 pp), because the daily background estimate adds noise.
- 2021 and the Jan-Nov window: December, the highest-excursion month, is excluded from the primary analysis; including it (2021-2024 calendar years) raises the share to 0.10.

## E07 review checkpoint (meteorological composition and environmental implications)
Technical validation: Kitagawa identity holds by construction (`tests/test_v2_math.py`); merges logged (`h3_merge_log.csv`); bootstrap resamples blocks within years jointly across stations; the extreme missing-outcome scenarios (0.019 and 0.022) stay close to the primary 0.027, so missing data are unlikely to drive the result (wording corrected in E07-r1; these are not bounds). **No material error.** Non-critical issues RB-21 to RB-25 are in the backlog for the integrated review; per policy, the estimand is not changed after seeing the result.

## Figures
Main Figure 9 (`figure09_composition_decomposition`). Supplementary S3 (`figureS3_baseline_comparison`: H1 fixed effects vs deweathering; H3 Kitagawa vs deweathering).

## E07-r1 review corrections (2026-11-10, D-43; `review_r1.py`, `results/r1_*`). Exploratory, development stage
Original results, the registered primary estimator and the H3 decision are unchanged.

**1. Missing-data terminology.** The rows formerly labelled "Manski lower/upper" are **extreme missing-outcome scenarios**: every missing CH4 hour set to non-exceedance (share 0.022) or to exceedance (0.019). They are not mathematical bounds on the pooled projection share, which is a ratio of sums and not monotone in the imputed values, and they do not bracket the primary 0.027. (Hour-level Manski bounds on excursion rates in E03 are valid bounds on those rates.) Original wording preserved: "Manski bounds bracket the primary closely (0.019-0.022)".

**2. Boosted-tree comparison.** The 0.21 share comes from a **standardised-year contrast**: a model including year as a predictor, evaluated on each station's full meteorology with year set to each value. This differs from the discrete Kitagawa decomposition, which has no model and splits observed rates exactly. No uncertainty estimate exists for 0.21. Forward-year validation (train on earlier years, predict the next), averaged over 12 stations:

| Test year | Observed rate | Predicted (with year) | Predicted (no year) | AUC climatology | AUC with year | AUC no year | Brier climatology / with year / no year |
|---|---|---|---|---|---|---|---|
| 2024 | 0.050 | 0.047 | 0.043 | 0.70 | 0.80 | 0.80 | 0.046 / 0.047 / 0.045 |
| 2025 | 0.050 | 0.027 | 0.029 | 0.67 | 0.82 | 0.82 | 0.047 / 0.044 / 0.044 |

Meteorology discriminates excursion hours well out of sample, but the year predictor adds nothing out of sample and the models under-predict the 2025 level by about half. Station-level misses are largest at AMS 18 (0.102 observed vs 0.032), AMS 30 and AMS 23. **The 0.21 share rests on in-sample year effects and is not validated.** It stays as an exploratory comparison only.

**3. Regime merging.** Effective regimes per contrast: median 12 (range 4-18). Unstable-night cells are pooled in 99% of contrasts (unstable nights are rare) and neutral-night cells in 49% (`r1_cell_pooling_frequency.csv`, `r1_effective_regimes_by_*.csv`). The registered 18-regime design is in practice a 10-16-regime design.

**4. Regime-resolution sensitivity.** Fixed 6 regimes (stability tercile x day/night, no merging): **0.032 (CI -0.080 to 0.151)**. 18 regimes with a 25 h merge rule: 0.036. The negative H3 result does not depend on regime resolution within this range.

**5. Interpretation.** The within-regime term is not an emission-rate change. No claim is made that meteorological standardisation is more useful at particular stations; that would need a direct operational comparison.
