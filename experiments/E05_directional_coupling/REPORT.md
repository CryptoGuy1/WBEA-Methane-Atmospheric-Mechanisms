# E05 H2: direction-dependent lagged coupling between stations

**Status:** exploratory (development data 2021-2025). **H2 development gate (D-26, criteria 1-2): PASSED.** Criterion 3 (kernel shape against simulated references) is evaluated in E06. Not a confirmed result.

## Question and estimand
When the wind blows from station i toward station j, do CH4 changes at i precede those at j more than when the wind blows the other way, after removing the regional component?
D_ij = sum over lags 1-3 of w_l [rho_l(aligned) - rho_l(reversed)], with rho_l = corr(dR_i(t-l), dR_j(t)) - corr(dR_j(t-l), dR_i(t)) on leave-pair-out residual CH4 changes. Lag 0 is excluded because its asymmetry is identically zero. Weights come from the predicted transit time. The pooled estimand is the inverse-null-variance mean over the 27 pairs.

**What D is not:** a trajectory, a source location, an emission rate or a transport fraction. A positive D means concentration fluctuations propagate along the pair axis in the wind direction. It does not say where they originate.

## Inference
- Null: 1,000 circular shifts of the wind series by whole days (14 days to N - 14 days), the same shift for all pairs. This preserves hour of day and the CH4 series exactly and breaks only the wind-CH4 alignment. The smallest attainable p-value is 1/1,001 = 0.001.
- Family-wise per-pair p-values: max-T over null-standardised D.
- CIs: joint 14-day block bootstrap, 2,000 replicates, same draws for all pairs.

## Results
| Quantity | Value |
|---|---|
| Pooled D | **0.128** (95% CI 0.108-0.155) |
| Null mean / 95th percentile | -0.000 / 0.014 |
| One-sided p | <= 0.001 (no null replicate reached the observed value) |
| Pairs with D > 0 | 27 of 27 |
| Pairs with p < 0.05, unadjusted / family-wise | 24 / 21 |

- **Distance dependence:** D falls with separation (Spearman -0.65, p = 0.0003). It is largest for the closest pairs (AMS 1-9 at 2.7 km: 0.71; AMS 1-13 at 4.5 km: 0.64; AMS 9-13 at 6.0 km: 0.56) and around 0.1-0.2 for 15-25 km pairs.
- **Pairs not significant after correction (6):** AMS 9-30, 13-23, 5-13, 1-5, 5-9 and 11-30. Two are effectively null (AMS 1-5: 0.012; AMS 5-9: 0.002); both are 26.4-26.6 km apart with transit near the 3 h limit.
- **Wind-vs-CH4 timing:** shifting wind by +/-1 h relative to CH4 gives pooled D 0.138 and 0.113, both positive (criterion 2 met).
- **Diagnostics (not part of the gate):** delaying one station's CH4 by 1 h reduces pooled D to 0.052 (source delayed) or 0.066 (receptor delayed). The signal depends on the relative timing of the two stations, as a propagation signature should.
- **Regional component:** pooled D 0.152 without common-mode removal, 0.127 leave-one-out, 0.128 leave-pair-out (primary), 0.117 leave-pair-out excluding AMS 14/18. Most of the signal is not regional. The pairs that lose most when the regional component is removed are AMS 9-30, 11-30, 5-6 and 6-7 (Fig. 8).
- **Season:** DJF 0.143, MAM 0.123, JJA 0.124, SON 0.182.
- **Stability:** unstable 0.178, neutral 0.140, stable **0.079**. Directional coupling weakens under stable conditions, matching the lower inter-station correlation found in E03.
- **Observed lag profile (aligned hours, all pairs):** the ratio of lag-1 to lag-0 correlation rises with predicted transit (0.34 for tau < 0.5 h; 0.64, 1.19, 1.42 for 0.5-2 h) and collapses for 2-3 h, where both correlations are near zero. E06 compares this with simulated kernels.

## Decision
| Criterion (D-26) | Result | Met |
|---|---|---|
| Pooled D above 95th null percentile | p <= 0.001 | yes |
| Pooled D positive under +/-1 h wind shift | 0.138; 0.113 | yes |
| Kernel shape | deferred to E06 | - |
| **H2 development gate (1-2)** | | **passed; proceed to E06** |

## Interpretation (exploratory)
The network shows a consistent, wind-direction-dependent ordering of CH4 changes between neighbouring stations, strongest at a few kilometres and decaying with distance. Removing the regional component barely changes it, and randomising wind timing destroys it. Together with E04, the picture is a regional concentration level set largely by stability, plus advected local fluctuations that are strongest when the boundary layer is mixed and wind is organised. Under stable conditions the level rises (E04) but directional organisation weakens (stable-tercile D about half the unstable value).

## Limitations
- The p-value floor (0.001) means most per-pair p-values sit at the floor; more shifts would resolve them but not change the decision.
- Hours are selected on wind at the receptor hour; the wind may change during transit.
- Pairs share stations and wind; the joint bootstrap and the common shift preserve this dependence. Pairs are still not independent replicates.
- AMS 9 and AMS 18 alternate sensor heights; height-stratified checks for AMS 9 pairs are left to the E05 supplementary table if reviewers ask.

## Figures
Main Figure 6 (`figure06_directional_coupling`), main Figure 8 (`figure08_residualisation_sensitivity`), both redrawn from saved tables by `plot_e05.py` for layout only. Main Figure 7 (kernel shape) comes from E06.
