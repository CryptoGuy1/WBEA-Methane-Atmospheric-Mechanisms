# E12: Synthetic calibration of the frozen H2 shifted-wind test. PRE-REGISTERED PLAN

**Status:** post-confirmation exploratory methodological study. Committed BEFORE any implementation output, pilot or production simulation. Branch `research/e12-h2-null-calibration`. The frozen E08 results, code, decisions and tags (`protocol-freeze` = 2b7c79e, `e08-confirmation` = 4c011a8) are not modified. No 2026 methane data are used. The registered H2 decision (confirmed; D = 0.287931708, p = 1/247) stands regardless of E12; E12 can only change how that p-value is characterised.

## 1. Questions (reported separately)
- **Q1 Null calibration.** Under data-generating processes with NO wind-conditioned inter-station coupling, but with autocorrelation, shared regional forcing, station-specific delays, seasonal drift, diurnal structure and missingness, does the frozen test reject at about 5%?
- **Q2 Seasonal-confounding sensitivity.** When a non-wind-locked lead-lag structure co-varies seasonally with wind regimes, does the whole-day circular wind shift produce false rejections, and do season-restricted or truncated shifts reduce them?
- **Q3 Detection power.** For known injected upstream-to-downstream coupling with D below, within and above the observed range (0.13-0.29), how often does the test reject, and how does power depend on the true lag (1, 2, 3 h)?
- **Q4 Interpretation (falsification).** Does a wind-advected shared meteorological driver, with no methane transport between stations, make H2 reject? This is a conditional-null violation by construction, not a calibration test.

**Two nulls, kept distinct.** The *statistical null* of the shift test is that the methane series are unrelated to the hourly timing of the wind series (exchangeability under whole-day circular wind shifts). The *physical null* is "no wind-conditioned inter-station methane coupling". N0, N1a, N2a and N3 satisfy both. N2b satisfies the physical null at the hourly scale but violates exchangeability through seasonal co-variation. N1b violates the statistical null with no methane transport.

## 2. Frozen statistic (unchanged)
Exactly the E08 H2 statistic and inference, from `src/wbea/h2.py` and `src/wbea/e08.py` at `protocol-freeze`:
- Leave-pair-out median residuals (at least 4 other stations), first differences.
- Aligned/reversed hour sets from pair-mean station wind: |U_par| >= 1 m/s, cos >= 0.707, tau <= 3 h.
- rho_l = corr(dR_i(t-l), dR_j(t)) - corr(dR_j(t-l), dR_i(t)) over hours with all four values finite; D_ij = sum over l = 1..3 of w_l (rho_l aligned - rho_l reversed), with w_l from tau over eligible hours.
- Pairs with < 100 eligible hours in either direction dropped; at least 10 pairs required.
- Pooled D with weights proportional to 1 / Var over the K = 246 admissible whole-day circular wind shifts (14-259 days for 273 days); one-sided p = (1 + #{null >= observed}) / (K + 1); alpha = 0.05.

**Fast implementation (to be parity-tested).** Shifting the wind circularly only rotates the aligned and reversed masks; the weights depend on the multiset of (mask, tau) values and are therefore shift-invariant. All 247 masked sums are computed with circular cross-correlation (FFT) of the six per-hour moment series with each mask. Parity with the frozen loop (`h2.pair_wind` -> `h2.sets` -> `h2.weights` -> `h2.D_stat`; `e08.pooled_inverse_null_variance`; `e08.finite_shift_p`) is required to an absolute tolerance of 1e-9 on per-pair D and pooled D, and identical p, on at least three synthetic fixtures (N0, N3 with missingness, P1). If parity fails, the frozen loop is used and replicate counts follow section 6.

## 3. Synthetic network
- 11 stations (WBEA official 2024 coordinates, AMS 2 excluded), giving the identical 21 E08 pairs (verified).
- 6,552 hours, 2031-01-01 01:00 to 2031-10-01 00:00, hour-ending (non-leap, matching 2026). Seasons: Jan-Mar, Apr-Jun, Jul-Sep.
- Units: CH4 in ppm (levels); differencing is done by the frozen pipeline.

**Regional wind** (`synthetic_params.json`, estimated once from development wind only; no methane, no 2026 data): an 8-sector Markov chain with season-specific transition matrices; direction uniform within ±22.5 deg of the sector centre; log speed = season x hour mean + AR(1) residual (phi 0.815, SD 0.596); speeds floored at 0.3 m/s.

**Station wind:** regional direction + fixed station offset ~ N(0, 8.2 deg) + hourly N(0, 51.8 deg) deviation (development values); speed x station ratio ~ U(0.64, 0.99) x exp(N(0, 0.1)); 0.5% missing.

**Baseline CH4** for station i:
X_i(t) = 2.0 + 0.05 S(t) + c(t) + e_i(t), where
- S is a stability index: AR(1) phi 0.9 plus a night-time maximum diurnal term, standardised;
- c is a regional AR(1) with phi 0.97 and marginal SD 0.05;
- e_i is a station AR(1) with phi_i ~ U(0.6, 0.9) and marginal SD sigma_i ~ U(0.03, 0.06);
- 3% of CH4 hours missing completely at random.

## 4. Scenarios
| ID | Family | Generating additions (beyond baseline) | Role |
|---|---|---|---|
| N0 | Baseline null | none | Q1 |
| N1a | Common driver, station-specific delays, wind-independent | X_i += lambda_i g(t - d_i); g AR(1) phi 0.8, SD 0.06; lambda_i ~ U(0.5, 1.5); d_i ~ U{0, 1, 2, 3} h | Q1 |
| N2a | Seasonal drift | winter (Jan-Mar) variance of c and e doubled and level +0.1 ppm; abrupt step at 1 April; summer regional wind uses transition matrices tilted toward 180 deg (from S) sectors, winter toward 0 deg (from N) | Q1 |
| N3 | Strong autocorrelation, diurnal coupling, missingness | phi_i ~ U(0.85, 0.97); night accumulation of 0.05 ppm via S; diurnal wind (night speed x 0.6; night direction biased +180 deg with probability 0.3); per-station zero/span gap of 1 h every 25 h within hours 01-06; one station missing Jul-Sep; MCAR 3% | Q1 |
| N2b | Seasonal confounding | N2a winds plus a winter-only regional driver arriving later at more southerly stations: delay = round(3 x (latitude rank fraction)) h, independent of hourly wind; absent Apr-Sep | Q2 |
| N1b | Falsification | shared driver g advected with the hourly regional wind: X_i += g(t - tau_i(t)), tau_i = projection of station position (relative to centroid) on the wind direction / (3.6 U), capped at 6 h; no methane source at any station | Q4 |
| P1 | Positive coupling | each station has a local AR(1) source q_i (phi 0.7); X_i += a q_i(t); when the pair-mean station wind is aligned i -> j (cos >= 0.707, U >= 1), X_j += 0.8 a q_i(t - L); reversed likewise | Q3 |

**P1 effect sizes.** Five target medians of pooled D: 0.07 (below), 0.13 and 0.21 (within), 0.29 (upper edge), 0.40 (above), with L = 1. The amplitude a for each target is chosen by a pilot (20 replicates per candidate a on a fixed grid of 12 values from 0.005 to 0.30, linear interpolation of median pooled D), recorded in `p1_amplitudes.json` and committed BEFORE production. The pilot uses only P1 pooled-D medians; no null rejection rates are inspected. Lags L = 2 and 3 use the amplitude for target 0.21.

## 5. Alternative nulls and baselines (exploratory; new statistics, never substituted for H2)
- **Within-season shift:** the wind is shifted circularly by k whole days within each 90/91-day season simultaneously, k = 14 to 76 (63 shifts; p floor 1/64). Pooled with weights from this null.
- **Truncated time-shift** (Yuan-and-Shou-style, approximate implementation; not their exact procedure): methane window fixed to hours [60 d, N - 60 d); wind window offset by k days, k in [-60, -14] U [14, 60] (94 shifts, no wrap-around; p floor 1/95). The observed value uses k = 0 on the same truncated window.
- **Baseline B1, ungated directional asymmetry:** A_ij = sum over l of w_l rho_l over ALL hours (no wind conditioning); naive per-pair Fisher-z test ignoring autocorrelation; reported as the share of pairs "significant" at 0.05 and the mean |A|. Descriptive comparison only.

## 6. Replicates, seeds, uncertainty
- **Replicates:** 500 each for N0, N1a, N2a, N3 and N2b; 200 for N1b; 200 per P1 configuration (5 amplitudes at L = 1, plus L = 2 and 3) = 1,400.
- **Benchmark first:** 10 replicates timed. If the projected total exceeds 12 h, all null scenarios drop to 300 and P1 to 150 (documented in DEVIATIONS.md); never below 200 for N0 and N2b.
- **Seeds:** replicate r of scenario index s uses seed 20261212 + 100000 s + r; scenario indices N0 = 1, N1a = 2, N2a = 3, N3 = 4, N2b = 5, N1b = 6, P1 = 7-13.
- **Uncertainty:** Wilson 95% interval for each rejection rate; Monte Carlo SE = sqrt(r (1 - r) / n). p-value quantiles (5/50/95%), empirical CDF, and pooled-D distributions are reported.

## 7. Pre-specified classification rules
For each Q1 scenario and each null method (rate r, Wilson interval [L, U]):
- **calibrated:** L <= 0.05 <= U and U <= 0.075;
- **conservative:** U < 0.05;
- **inflated:** L > 0.05;
- **inconclusive:** otherwise.

**Q1 overall verdict** (primary method): *calibrated* if every Q1 scenario is calibrated or conservative; *miscalibrated* if any is inflated; otherwise *inconclusive*.

**Q2** (N2b, primary method): *robust to the tested seasonal confounding* if calibrated or conservative under the rule above; *sensitive* if inflated; otherwise *inconclusive*. Alternative nulls are reported with the same rule, as exploratory.

**Q3** (per configuration): *adequate power* if the Wilson lower bound >= 0.80; *limited power* if the upper bound < 0.80; otherwise *inconclusive*.

**Q4:** the rejection rate is reported, with no calibration verdict; a high rate demonstrates that rejection does not identify methane transport.

**Results that do not meet a rule's conditions are classified inconclusive.** No scenario, parameter or replicate is added, removed or re-run after production outputs are seen. Any deviation goes in DEVIATIONS.md with its reason.

## 8. Outputs
Per-replicate CSV (scenario, replicate, seed, n_pairs, pooled D, p for each of the three nulls, baseline statistics, runtime); a summary table; figures (rejection rates with intervals, p-value CDFs, power curves, pooled-D distributions); tests; `REPORT_FOR_MANUSCRIPT_AI.md`; `MANUSCRIPT_HANDOFF.md`; `README.md`; `DEVIATIONS.md`.
