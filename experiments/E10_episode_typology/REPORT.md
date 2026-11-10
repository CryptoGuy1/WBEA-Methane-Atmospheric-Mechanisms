# E10 (X1) Methane-pattern and wind-alignment typology of P95 episodes

**Status:** exploratory (development data 2021-2025). **Typology NOT SUPPORTED** under the pre-registered rule (D-60): V1 failed; V2 (boundary-layer height) and V3 were met. The labels are not source identities and do not establish mechanisms.

## Design (D-56, D-60)
7,951 P95 episodes (R3 onsets, single-hour gaps bridged) at 12 stations. Labels use methane patterns and wind alignment only: network synchrony sigma (share of other valid core stations above their own P95 at t0-1..t0+1) and an upstream lead L (an eligible aligned upstream pair whose standardised leave-pair-out residual change reached z >= 1 at lags 1-3). **Wind enters L through pair eligibility, so the typology is not independent of wind.** Categories: accumulation-compatible (sigma >= 0.5, L = 0), mixed (sigma >= 0.5, L = 1), advection-compatible (sigma < 0.5, L = 1), isolated (sigma < 0.5, L = 0), unclassified (< 4 valid core stations). Disclosed deviation: when no eligible pair exists, L = 0 with `lead_assessable = False`, rather than 'unclassified'. Seed 20261120.

## Results
| Category | Share | 95% CI | n |
|---|---|---|---|
| Accumulation-compatible | 13.3% | 11.2-15.6% | 1,058 |
| Mixed | 4.0% | 3.2-4.8% | 315 |
| Advection-compatible | 12.2% | 11.1-13.2% | 968 |
| Isolated | 70.3% | 67.4-73.0% | 5,586 |
| Unclassified | 0.3% | 0.2-0.5% | 24 |

By station, advection-compatible shares range 0% (AMS 14, 18: no pairs) to 25% (AMS 1); an upstream lead was assessable at 17-74% of onsets at paired stations.

| Check | Result | Met |
|---|---|---|
| **V1 wind-shift placebo** (200 shifts; not independent of wind) | real advection-compatible share 0.122 vs placebo mean 0.141, 95th percentile 0.148 (p = 1.0) | **no** |
| **V2 external consistency: ERA5 BLH** (accumulation minus advection, median) | -76 m (-89 to -59) | yes |
| V2 AMS 5 stability (z) | +0.17 (-0.08 to 0.34) | not significant |
| V2 ERA5 100 m direction variability (3 h) | +5.8 deg (0.0 to 12.6); accumulation-compatible episodes have less steady elevated wind | yes (borderline) |
| **V3 temporal hold-out** (train 2021-2023, test 2024-2025; gain over station + F5 regime) | log duration +0.021 (0.003 to 0.039); log peak excess +0.011 (0.000 to 0.022) | yes (small) |
| V4 period stability | accumulation-compatible 10.9% -> 16.9%; advection-compatible 13.5% -> 10.1%; BLH contrast -76 m and -74 m | contrast stable, shares shift |

Classification stability (Cohen's kappa vs primary): sigma cut 0.4 / 0.6: 0.87 / 0.85; lead lags 1-2: 0.93; z 0.75 / 1.25: 0.94 / 0.95; **onset-available vs retrospective synchrony: 0.90**; leave-one-core-station-out (minimum): 0.90; P90 matched episodes (5,556 of 13,230 P90 onsets matched): 0.62.

## Exploratory post hoc diagnostic (`exploratory_v1_conditional.py`; not part of any decision)
| Quantity | Real wind | Placebo mean (5th-95th pct) |
|---|---|---|
| Share of episodes with an assessable upstream pair | 0.445 | 0.478 (0.462-0.497) |
| P(upstream lead given assessable) | 0.363 | 0.405 (0.391-0.419) |

Episode onsets occur in hours with fewer eligible aligned pairs, but that does not explain the failure: **conditional on eligibility, the lead rate is lower under real wind than under randomised wind.** Rises at a neighbouring station 1-3 h before onset are common regardless of wind direction, consistent with shared pre-onset build-up.

## Interpretation
The methane-pattern typology is internally stable, aligns with an independent boundary-layer contrast, and adds a small amount of out-of-sample information about episode duration and peak. Its central advection component fails the wind-shift check: at the level of individual episode onsets, the upstream-lead rule does not respond to wind direction. **The E05 directional coupling, which is significant when averaged over all eligible hours, does not translate into an episode-level advection label.** Most episodes (70%) are isolated, neither network-wide nor upstream-led.

## Limitations
- Labels depend on rule thresholds; stability is high, but P90 agreement is moderate (kappa 0.62).
- The V1 placebo is not independent of the wind used in labelling (stated in the design).
- The V3 gains are small and of limited practical size.

## Decision (D-60)
Typology **not supported**; reported in full. Per the protocol, episode-distribution reporting falls back to the F5 descriptive regime analysis. No redefinition of the rule is proposed.

## Outputs
`results/e10_episodes.csv`, `e10_shares_pooled.csv`, `e10_shares_by_station.csv`, `e10_v1_placebo.csv`, `e10_v2_external_consistency.csv`, `e10_v3_temporal_holdout.csv`, `e10_v4_period_stability.csv`, `e10_classification_stability.csv`, `e10_p90_population.csv`, `e10_decision.csv`, `exploratory_v1_conditional.csv`; `figures/e10_typology.{png,svg,pdf}`.

## Addendum (2026-11-10, researcher review): assessable vs non-assessable upstream lead
`L = 0` does not always mean a detectable lead was absent: for 55% of episodes (4,412 of 7,951) no eligible aligned upstream pair existed at onset, so a lead could not be assessed. Descriptive split (`addendum_assessability.py`; no re-classification):

| | n | Accumulation-compatible | Mixed | Advection-compatible | Isolated | Unclassified | Median BLH (m) |
|---|---|---|---|---|---|---|---|
| Lead assessable | 3,539 | 7.0% | 8.9% | 27.4% | 56.5% | 0.3% | 137 |
| No assessable pair | 4,412 | 18.4% | 0% | 0% | 81.3% | 0.3% | 89 |

"Isolated" in the no-assessable group means "not network-wide, lead not assessable", not "no upstream influence". **V1 used 200 random admissible whole-day wind shifts, not the full admissible set** (about 1,768 shifts in the development series); its p-value resolution is 1/201. The V1 failure is not near the decision boundary (real share 0.122 vs placebo mean 0.141).
