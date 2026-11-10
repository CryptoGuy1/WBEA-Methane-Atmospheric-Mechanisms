# E03 Diurnal, seasonal, spatial and meteorological patterns of CH4 excursions

**Amended 2026-11-10 (review corrections 1-2, PWIP rename; see Amendments).** **Status:** exploratory, descriptive. No hypothesis is decided here. Decision criterion (patterns adequately characterised to design E04-E07): met, with one design issue raised for E07 (D-16).

## Definitions and assumptions
- Excursion: hourly CH4 above the station's own 2021-2023 95th percentile (P90 and P99 computed for sensitivity). An excursion is a concentration statistic, **not** an emission event.
- Thresholds (ppm, P95): AMS 1 2.441; AMS 2 2.627; AMS 5 2.420; AMS 6 2.229; AMS 7 2.266; AMS 9 2.435; AMS 11 2.544; AMS 13 2.539; AMS 14 2.179; AMS 18 2.128; AMS 23 2.759; AMS 30 2.472.
- Uncertainty: 14-day joint block bootstrap across all 12 stations (2,000 replicates; seed 20261113).
- Regimes: AMS 5 T90 - T20 terciles with fixed 2021-2023 cut points (-0.6, 0.0 degC); station composite wind classes (<1, 1-2.5, >=2.5 m/s); solar day/night (elevation > 0 deg at 57.0N, 111.5W).
- n = 479,063 valid station-hours.

## Results
**Q1 Diurnal and seasonal cycle.** The pooled excursion rate peaks at 7.8% (95% CI 6.9-8.7) at hour ending 06 and falls to 2.7% (2.0-3.4) at 16. Monthly rates run from 1.2% (0.8-1.7) in May to 10.5% (7.0-14.6) in January and 10.2% (8.6-12.0) in December, with a secondary late-summer peak (5.7% in August). Summer excursions are confined to night and early morning; winter excursions occur at all hours.

**Q2 Stations.** Night (solar elevation <= 0) holds 55-69% of each station's excursions against 48% of valid hours. Peak hours fall between 01 and 08 at 11 stations (AMS 11: 21). Year-to-year rates vary widely: AMS 18 rises from 1.4% (2021) to 10.3% (2025), AMS 23 from 3.2% to 7.9% and AMS 30 from 3.9% to 7.5%, while AMS 2, 9, 11 and 14 fall in 2025.

**Q3 Spatial co-occurrence.** Joint excursions decline with distance. Unconditional lift (P(both)/(P(i)P(j))) ranges 1.6-11.5 (Spearman with distance -0.77). Conditioning on month x hour removes the shared calendar cycle and leaves lift 1.3-6.5 (Spearman -0.82). The highest values are AMS 1-13 (6.5) and AMS 1-9 (6.3). Even 177-194 km pairs retain lift 1.3-1.8. **Dependence-aware uncertainty (addendum):** Spearman(lift, distance) = -0.82, 95% CI -0.86 to -0.73 from a joint 14-day block bootstrap that recomputes all 66 lifts from the same draws; Mantel permutation of station labels p = 0.0001 (9,999 permutations, the floor); leave-one-station-out range -0.86 to -0.76; within the 10-station oil-sands core only, -0.64 (-0.74 to -0.51). This is a descriptive association. Common weather systems, shared industrial influences, similar instruments and temporal autocorrelation can all produce it; it is not evidence of methane transport (directional evidence is tested in E05/E06).

**Q4 Meteorological strata.** Excursion rates are 1.7%, 4.2% and 9.6% in the unstable, neutral and stable AMS 5 terciles; 12.5%, 6.6% and 1.8% for wind <1, 1-2.5 and >=2.5 m/s; and 12.3%, 7.2%, 4.0%, 1.4% and 0.5% across ERA5 boundary-layer-height quintiles (medians 59 to 1,389 m). The stable, <1 m/s regimes hold 7.5% of hours but 23.6% of excursions.

**Q5 Network covariance (Fig. S1).** Mean pairwise correlation of hourly anomalies **falls** with stability: 0.41 (unstable), 0.33 (neutral), 0.25 (stable). Stable conditions raise concentrations at most stations at once (Q4) but make hour-to-hour variations more station-specific.

**Q6 Episode definitions (Fig. S4).** Total P95 onsets range from 3,731 (6 h clearance) to 8,795 (missing counted as below). The 6 h clearance rule leaves 1 onset at hour ending 06, against 323 for the crossing-after-valid rule: the nightly Z gap removes dawn episodes, reproducing the earlier audit finding on 12 stations. Bridging single-hour gaps restores most of them (319). Manski bounds are wide at 01-06 (lower 5-6%, upper 24-25%), and E02 Q4 found no systematic difference in neighbouring concentrations at Z hours. The complete-case curve is reported under the working assumption of conditional missing-at-random, with these bounds as the assumption-free range.

**Q7 Potential wildfire-influenced periods (D-11, renamed D-31).** Hours flagged by FIRMS detections or network PM2.5 (9.2% of station-hours) have an excursion rate of 6.6% against 5.0% otherwise and hold 11.8% of excursions. The flag is not a direct smoke-transport measurement; it marks periods when wildfire influence is plausible. It is used as a sensitivity exclusion only.

## Interpretation (exploratory)
Excursions follow the stable-boundary-layer pattern in every stratification tried: nocturnal and winter maxima, monotone increase with stability and with lower wind and boundary-layer height. This is consistent with the H1 hypothesis but is a marginal association; season, hour and wind are confounded with stability here, and E04 estimates the adjusted effect.

Two findings change the analysis plan:
1. **Declining correlation under stability (Q5).** "Common mode" in H1 must be read as a shared *level* (network median excess), not as synchronised hour-to-hour variation. Under stable conditions local variability grows. This also predicts weaker H2 directional signals under stable, low-wind conditions.
2. **Remote-station trends (Q2).** AMS 18's P95 threshold (2.128 ppm) sits only about 0.07 ppm above typical background. A regional background rise of a few hundredths of a ppm over 2021-2025 (the global CH4 growth rate is of that order) would raise its excursion rate several-fold without any local change. Raw excursion-rate trends at low-threshold stations therefore cannot be read as local change. E07 must separate background drift from the within-regime term (D-16).

## Limitations
- Descriptive associations; no causal or emission interpretation.
- Regimes use one tower (AMS 5) for stability at all stations.
- T90 - T20 is reported at 0.1 degC resolution; ties at the 0.0 cut point go to the upper tercile (D-17).
- Lift at short distances may also reflect shared local sources.

## Negative findings
- Network correlation does not increase with stability (it decreases).
- The 6 h clearance episode rule is unsuitable with this network's calibration schedule.

## Figures
Main Figure 3 (`figure03_excursion_phenotype`), Supplementary S1 (`figureS1_network_correlation_by_stability`), Supplementary S4 (`figureS4_episode_definition_sensitivity`).

## Amendments
**2026-11-10 (RB-02, review correction 2).** Added dependence-aware uncertainty for the co-occurrence-distance relation (`addendum_dependence.py`; `results/addendum_*.csv`) and restricted its interpretation to description. Original wording, preserved: "Even 177-194 km pairs retain lift 1.3-1.8, which points to a regional component beyond the calendar."

**2026-11-10 (RB-01, review correction 1).** Original wording in Q6, preserved: "but E02 Q4 shows Z is ignorable given hour and month, so the complete-case curve is the appropriate estimate." Revised to a working assumption.

**2026-11-10 (RB-03).** "Smoke hours" renamed "potential wildfire-influenced periods (PWIP)". Result file names (`q7_smoke_sensitivity.csv`) and variable names in the archived script are unchanged; they refer to PWIP.
