# E09 (X4) Elevated-wind sensitivity of the lag-centroid discrepancy

**Status:** exploratory (development data 2021-2025). **Primary outcome (D-55): INCONCLUSIVE.** The original E06 kernel criterion remains failed. A smaller centroid discrepancy would not prove a physical transport speed.

## Question
Is the E06 discrepancy between observed lag centroids and continuous-source reference centroids reduced when transit times use elevated wind instead of the 10 m station wind?

## Design
| Variant | Hours selected with | Transit time, upstream side and bins from | Isolates |
|---|---|---|---|
| W0 | station 10 m (pair mean) | station 10 m | E05/E06 baseline |
| W4_speed | W0 | W0 direction with ERA5 100 m speed | speed |
| **W4_full (primary, X4a)** | W0 | ERA5 100 m (pair-cell mean) | speed + direction |
| W4_resel (X4b) | ERA5 100 m | ERA5 100 m | + selection |
| W0_dc / W4_dc | hours aligned under BOTH W0 and ERA5 | W0 / ERA5 | speed on a direction-consistent common sample |
| T45 / T75 / T90 | W0 | AMS 5 tower 45/75/90 m (one location for all pairs) | supporting |

Observed centroid per transit bin = lag centroid of the pooled (n-weighted) lag-0..3 correlation profile of leave-pair-out residual changes in aligned hours. Reference = same statistic from continuous-source injections (A = 0.3, memory 180 min, 10 replicates) into real residuals with all winds shifted 182 days, under the same variant. SSE = sum over bins of (observed - mean reference)^2. Delta SSE = SSE(base) - SSE(alternative); 95% interval from 1,000 joint 14-day block bootstrap replicates of the observed centroids, each paired with a random reference replicate. Seed 20261119.

## Results
| Variant | Observed centroids by bin (h) | Reference (h) | SSE |
|---|---|---|---|
| W0 | 0.25, 0.39, 0.73, 1.11, 1.51 | 0.18, 0.36, 0.84, 1.44, 2.04 | 0.404 |
| W4_speed | 0.31, 0.61, 0.88, 1.40, 1.62 | 0.19, 0.43, 1.01, 1.48, 1.64 | 0.072 |
| **W4_full** | 0.25, 0.55, 0.80, 1.01, 1.31 | 0.19, 0.39, 0.91, 1.16, 1.48 | **0.090** |
| W4_resel | 0.21, 0.42, 0.72, 1.15, 1.19 | 0.18, 0.43, 1.01, 1.47, 2.04 | 0.921 |
| W0_dc | 0.25, 0.39, 0.67, 1.04, 1.29 | 0.19, 0.40, 1.08, 1.43, 1.92 | 0.714 |
| W4_dc | 0.26, 0.56, 0.80, 1.50, 1.60 | 0.19, 0.48, 1.09, 1.31, 1.74 | 0.152 |
| T45 / T75 / T90 | - | - | 0.091 / 0.197 / 0.160 |

| Comparison | Delta SSE | 95% interval | Reading |
|---|---|---|---|
| **Primary X4a: W0 vs ERA5 100 m, fixed hours** | **0.314** | **-0.081 to 0.772** | **inconclusive** |
| Speed only | 0.332 | -0.329 to 0.872 | inconclusive |
| X4b reselected hours | -0.517 | -2.253 to 0.174 | inconclusive (point estimate worse) |
| Direction-consistent common sample | 0.562 | -0.294 to 1.559 | inconclusive |
| AMS 5 45 / 75 / 90 m | 0.314 / 0.207 / 0.244 | all include 0 | inconclusive |

**Sample sizes and membership.** Faster transport moves hours from long-transit to short-transit bins: bins 1.5-2 h and 2-3 h fall from 39,929 and 56,380 aligned pair-hours (W0) to 22,223 and 18,431 (W4_full). Only 25-33% of shared hours stay in the same bin. Fixed-hour variants keep 89-98% of W0 hours in the 0-3 h range (Jaccard 0.89 W4_full; 0.98 W4_speed); reselection with ERA5 keeps only 0.46. The direction-consistent subset retains 70% of W0 hours.

**Direction disagreement (W0-aligned hours).** ERA5 100 m vs W0: median 19.5 deg, 20% of hours > 45 deg, 3% > 90 deg. AMS 5 45 m vs W0: median 11 deg, 4% > 45 deg. Tower representativeness declines with distance from AMS 5: mean cos(direction difference) 0.83-0.91 within 11 km, 0.73-0.86 at 22-43 km, 0.62 at AMS 18 (151 km).

## Interpretation
Every elevated-wind variant that keeps the W0 hours lowers the discrepancy (point estimates 0.21-0.56), and the speed-only variant accounts for most of the primary improvement (0.33 vs 0.31). That pattern is *compatible with* effective transport faster than the 10 m wind. No interval excludes zero, however, so the hypothesis is neither supported nor rejected. Reselecting hours with ERA5 wind worsens agreement, consistent with ERA5's coarser, less station-representative directions. Two caveats limit any physical reading:
1. Faster transit empties the long-transit bins that drove the original discrepancy, so improvements partly reflect re-binning and reduced power there; the reference absorbs re-binning but not the loss of precision.
2. Lag centroids of hour-averaged, differenced series are statistical lags, not transport times.

## Limitations
- 10 reference replicates; reference spread contributes substantially to interval width.
- AMS 5 tower wind is applied to all pairs despite declining representativeness with distance.
- ERA5 cells are shared by several stations (D-06).

## Decision
Primary criterion: inconclusive. Recorded as such; no method change is proposed to obtain significance. Whether X4 enters E08 is for the researcher's review (D-57).

## Outputs
`results/e09_centroids_reference_sse.csv`, `e09_delta_sse.csv`, `e09_decision.csv`, `e09_membership_by_pair_variant.csv`, `e09_direction_disagreement.csv`, `e09_tower_representativeness.csv`; `figures/e09_centroids_by_wind.{png,svg,pdf}`.
