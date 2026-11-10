# E04 H1: atmospheric stability and the regional CH4 level

**Status:** exploratory (development data 2021-2025). **Pre-registered gate (D-22): PASSED** on all three criteria. Not a confirmed result; E08 decides.

## Question and estimand
Does the network-wide CH4 level rise with near-surface stability, net of year x month x hour cycles?
b1 = change in the median CH4 anomaly of the 7 core stations (ppm) per 1 SD of AMS 5 T90 - T20, estimated within year x month x hour cells (1,439 cells). **Total** effect: no wind term. **Direct** effect: with log(U5 + 0.5).

## Assumptions
A1: within a year x month x hour cell, emissions do not co-vary with stability. Untestable directly; probed by the negative-control exposure S(t+24). A2: AMS 5 tower stability represents the core network (probed with ERA5 and AMS 1 proxies). The estimate is an association, not an emission or causal attribution.

## Results
| Estimand | n hours | ppm per SD | 95% CI (14-day block bootstrap, 2,000) |
|---|---|---|---|
| Total | 40,715 | 0.054 | 0.048-0.059 |
| **Direct (primary)** | 40,334 | **0.048** | **0.041-0.052** |

- **Uncertainty:** 7-, 21- and 30-day blocks give 0.042-0.053 at the widest.
- **Replication:** positive in all five years (0.037-0.059; every CI excludes 0) and all four seasons (JJA 0.038 to MAM 0.056).
- **Response definition:** dropping any one core station gives 0.043-0.057. Background-subtracted response 0.047; removing station-months below 75% coverage 0.048; excluding smoke hours 0.048. The expanded 11-station response is smaller (0.034, CI 0.029-0.038), as expected when the median includes AMS 14 and AMS 18, which are 40-150 km away from the mining area.
- **Alternative proxies:** ERA5 -log(boundary-layer height) at the AMS 5 cell gives 0.054 (0.047-0.059), an independent reanalysis proxy agreeing with the tower. AMS 5 T75 - T20: 0.045; T45 - T20: 0.038. AMS 1 T10 - T2 gives a much weaker 0.013 (0.007-0.017).
- **Negative control:** next-day stability S(t+24), given S(t), has coefficient 0.000 (-0.005 to 0.003); S(t) is unchanged at 0.048. No sign of multi-day synoptic confounding.
- **Baselines:** cell means alone explain R2 = 0.29 of the response. Stability adds a partial R2 of 0.14 given cells and wind. A random-forest meteorological normalisation (OOB R2 0.58) gives a partial-dependence slope of 0.052 ppm per SD, close to the fixed-effects estimate. The piecewise-linear spline is close to linear with mild flattening above +1.5 SD.

## Decision (D-22)
| Criterion | Met |
|---|---|
| Direct-effect CI excludes 0 | yes |
| Sign agrees in >= 4 of 5 years | yes (5 of 5) |
| Negative control not >= 50% of effect with CI excluding 0 | yes |
| **H1 gate** | **passed; proceed to E05** |

## Interpretation (exploratory)
A 1 SD increase in the 20-90 m temperature gradient at AMS 5 accompanies a rise of about 0.05 ppm in the core-network median CH4 anomaly, within the same year, month and hour. That is roughly a third to half of the gap between median and P95 at the core stations (P95 minus median 0.13-0.33 ppm in 2021-2023). The relation holds every year, every season, with every core station removed, and with an independent reanalysis proxy. Next-day stability has no residual association, which argues against slow synoptic co-variation of emissions and mixing as the explanation. Concentration enhancement under stability is consistent with reduced dilution; it says nothing about emission rates.

## Limitations and negative findings
- **Weak shallow-layer proxy.** The AMS 1 2-10 m gradient is a much weaker proxy (0.013 per SD). A shallow 8 m layer at a community site responds to surface radiative cooling and local obstacles more than to regional mixing depth. This favours deep-layer stability (tower or reanalysis) for this question.
- **Representativeness.** A single tower provides S for the whole network; ERA5 agreement mitigates but does not remove this.
- **Interval asymmetry.** Percentile intervals sit asymmetrically around some estimates (primary total 0.054 within 0.048-0.059), because duplicated blocks interact with cell absorption. The basic (reverse-percentile) interval for the direct effect is 0.043-0.054, and neither interval approaches 0. E08 keeps the pre-registered percentile interval; a bias-corrected interval will be reported alongside (D-24).
- **Seasonal variation.** The summer effect (0.038) is smaller than spring (0.056). Seasonal modification is not part of the pre-registered estimand and is reported descriptively.

## Figures
Main Figure 4 (`figure04_stability_elasticity`: partial residuals, spline, random-forest baseline). Main Figure 5 (`figure05_h1_robustness`: forest plot). The random-forest part of Supplementary S3 comes from `results/baseline_rf_partial_dependence.csv`.
