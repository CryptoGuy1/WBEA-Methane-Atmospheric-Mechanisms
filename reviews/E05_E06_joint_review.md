# Joint scientific review: E05 + E06 (2026-11-10)

## Verdict
No material error in E05. One methodological flaw in the E06 criterion design (signal-dominated reference), found by the pre-registered test itself. Development status of H2: **directional coupling supported (criteria 1-2); quantitative lag-kernel criterion failed as pre-registered**; revised kernel test frozen for E08 (D-36). E07 does not depend on criterion 3, so experimentation continues.

## Technical and statistical validation
| Check | Result |
|---|---|
| Shared library reproduces E05 D | yes (`tests/test_h2_library.py`, tolerance 1e-4) |
| Null calibration of the injection background | 0/864 false detections at A = 0; thresholds conservative |
| RB-08: hour sets from wind averaged over t-3..t | pooled D 0.143 (E05: 0.128); 27/27 pairs positive. Robust |
| RB-09: AMS 9 pairs by AMS 9 sensor height | D higher in 10 m hours in 6 of 7 pairs (e.g. AMS 1-9: 0.86 vs 0.65); 20 m hours fall mostly in 2022-2023, so height and year are confounded. Not material; noted as a limitation |
| E06 crash | array-conversion bug fixed before any output was used; full re-run from a clean commit |

## Unexpected results
1. Observed lag centroids are shorter than the signal-dominated reference (criterion 3(ii) fails, 1/5 bins).
2. Directional coupling is weaker under stable conditions (E05: 0.079 vs 0.178 unstable), the opposite of the concentration-level effect (E04).
3. Two 26 km pairs (AMS 1-5, 5-9) are null despite adequate power (E06).

## Integration with E04
Stability raises the regional CH4 level (E04) while weakening organised inter-station propagation (E05). These are two different physical signatures, accumulation and advection, measured by two different estimands. This is the paper's central mechanistic contrast and should be framed as such, without fractions or source attribution.

## Backlog changes
RB-08 and RB-09 resolved (results above). New: RB-15 (Figure 7 should also show the SNR-matched reference), RB-16 (E06 detection thresholds borrowed from E05), RB-17 (height-year confounding at AMS 9).
