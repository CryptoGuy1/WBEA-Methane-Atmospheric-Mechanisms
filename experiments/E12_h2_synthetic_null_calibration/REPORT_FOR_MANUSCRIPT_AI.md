# E12 Report: Synthetic calibration of the frozen H2 shifted-wind test

**Prepared for independent review. Post-confirmation exploratory methodological study.** Branch `research/e12-h2-null-calibration` of `CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms`. The final commit SHA is reported in the handoff message and in `MANUSCRIPT_HANDOFF.md`. All numbers below come from executed code (`analyze_e12.py` on `results/raw_*.csv`).

## 1. Executive result
| Question | Pre-registered classification | Key numbers (primary test, alpha = 0.05) |
|---|---|---|
| **Q1 Null calibration** (4 nulls) | **Inconclusive** overall by rule: N0, N2a, N3 *calibrated*; N1a *inconclusive* | Rejection rates 4.6%, 5.4%, 4.8%, 4.6%; every Wilson 95% interval contains 0.05. N1a's upper bound (0.0774) exceeds the pre-registered 0.075 margin by 0.0024 |
| **Q2 Seasonal-confounding sensitivity** (N2b) | **Sensitive** (primary inflated) | **23.8% (20.3-27.7%)**. Exploratory alternatives: within-season shift 5.2% (3.6-7.5%), truncated shift 6.8% (4.9-9.4%), both *inconclusive* by rule |
| **Q3 Detection power** | *Adequate* at D below and within the observed range up to about 0.20; *limited* (0%) for a 3 h true lag; **inconclusive at D >= 0.21** (not reachable by the tested models) | 100% (lower bound 98.1%) at median D 0.069, 0.108, 0.131, 0.177, 0.195; lag 3: 0%, median D -0.040 |
| **Q4 Falsification** (N1b) | No verdict by design | **100% rejection**, median D 0.132, with no methane transport between stations |

**Editorial verdict: conditionally robust.** The frozen test behaves close to nominal under the tested stationary, common-driver, seasonal-drift, autocorrelation and missingness nulls, but formally Q1 is inconclusive under the pre-registered margin. It is **not robust to seasonal confounding** of the tested form. A significant H2 result does **not** discriminate methane transport from an advected shared signal. **The registered 2026 decision is unchanged; the p = 1/247 characterisation must carry these caveats.**

## 2. Provenance and integrity
- Frozen references, unchanged: `protocol-freeze` = 2b7c79e259ea1fbc957998da9f921db8abdf38ea; `e08-confirmation` = 4c011a8. A test (`test_frozen_files_unmodified`) confirms an empty diff for `src/wbea`, the protocol, `config`, both E08 runners and the confirmation outputs.
- Plan committed before any implementation output: c45f8ef4a5f8a34721d625cab0fb849912f467b6 (pushed). Implementation: 285e5d7. Pilots and final power configurations, fixed before production: d0231fa (pushed).
- Production: 4,100 replicates, 0 failures, 0 not evaluable, about 42 min on 1 CPU (0.56-0.65 s per replicate); `results/production_log.txt`.
- Deviations D1-D5: `DEVIATIONS.md`. D3 and D4 change the power design (section 5); D1 and D2 are implementation fixes made before production; D5 is presentation only.
- No 2026 methane data used. Wind parameters came from development wind only (2021-2025, Jan-Sep; AMS 5 regional; `synthetic_params.json`).

## 3. Definitions
- **Statistical null of the shift test:** methane series are unrelated to the hourly timing of the wind series, i.e. exchangeable under whole-day circular wind shifts.
- **Physical null:** no wind-conditioned inter-station methane coupling.
- **Positive alternative:** methane emitted near station i appears at downstream station j at a known lag when the pair-mean wind is aligned i -> j (and vice versa).
- N0, N1a, N2a and N3 satisfy both nulls. N2b satisfies the physical null at the hourly scale but violates exchangeability through seasonal co-variation. N1b violates the statistical null with no methane transport.

## 4. Design (full equations in `EXPERIMENT_PLAN.md`, code in `e12/generator.py`)
- **Network:** 11 WBEA stations (official coordinates, AMS 2 excluded), giving the identical 21 E08 pairs. 6,552 hours (1 Jan 01:00 - 1 Oct 00:00, hour-ending).
- **Regional wind:** 8-sector Markov chain with season-specific transitions; log-speed AR(1) (phi 0.815). Station wind = regional + fixed offset (SD 8.2 deg) + hourly scatter (SD 51.8 deg), speed ratio 0.64-0.99.
- **CH4 (ppm):** 2.0 + 0.05 S + regional AR(1) (phi 0.97, SD 0.05) + station AR(1) (phi 0.6-0.9, SD 0.03-0.06), 3% missing completely at random.

| Scenario | Addition |
|---|---|
| N1a | Common driver with station-specific delays 0-3 h, independent of wind |
| N2a | Winter variance doubled, +0.1 ppm level step at 1 April, seasonally tilted wind regimes (winter from N, summer from S) |
| N3 | phi 0.85-0.97, station diurnal cycles, diurnal wind (night speed x 0.6, 30% night reversals), daily zero/span gap rotating through hours 01-06, one station missing Jul-Sep |
| N2b | N2a winds plus a winter-only driver arriving 0-3 h later at more southerly stations (latitude rank), independent of hourly wind |
| N1b | Shared driver advected with the hourly regional wind (station delay = position projected on the wind / speed, capped at ±6 h) |
| P1 | Local AR(1) source at each station; 0.8 x source added downstream at fixed lag L when aligned |
| P1T | As P1, with lag = round(transit time), 1-3 h |

- **Primary test:** the frozen H2 statistic and 246-shift finite p, computed by an exact FFT implementation. Parity with the frozen loop holds to 1e-9 for per-pair and pooled D, with identical p, including a full 246-shift check (`tests/test_e12.py`).
- **Exploratory alternatives:** within-season circular shift (63 shifts, p floor 1/64); truncated non-circular shift, a Yuan-and-Shou-style approximation and not their exact procedure (94 shifts, floor 1/95).
- **Baseline B1:** ungated directional asymmetry with a naive per-pair Fisher-z test.
- **Seeds:** 20261212 + 100000 x scenario index + replicate.

## 5. Results
### 5.1 Q1 Null calibration (primary method)
| Scenario | n | Rejections | Rate | Wilson 95% | MC SE | Classification | p 5% / 50% | pooled D 5 / 50 / 95% |
|---|---|---|---|---|---|---|---|---|
| N0 baseline | 500 | 23 | 0.046 | 0.031-0.068 | 0.009 | calibrated | 0.053 / 0.474 | -0.016 / 0.001 / 0.016 |
| N1a common driver | 500 | 27 | 0.054 | 0.037-0.077 | 0.010 | **inconclusive** | 0.041 / 0.472 | -0.015 / 0.001 / 0.014 |
| N2a seasonal drift | 500 | 24 | 0.048 | 0.033-0.070 | 0.010 | calibrated | 0.057 / 0.500 | -0.018 / 0.000 / 0.015 |
| N3 autocorrelation + gaps | 500 | 23 | 0.046 | 0.031-0.068 | 0.009 | calibrated | 0.057 / 0.486 | -0.022 / 0.000 / 0.020 |

p-value CDFs lie close to uniform (`figures/e12_null_pvalue_cdf_and_D`). The largest pooled D across all 2,000 calibration-null replicates was 0.042.

**Interpretation.** There is no evidence of inflation in these four nulls. The overall Q1 verdict is *inconclusive* only because N1a's upper interval limit narrowly exceeds the pre-registered 0.075 margin; its point estimate (5.4%) is nominal. More replicates would be needed to classify N1a, and none were added after seeing results.

### 5.2 Q2 Seasonal-confounding sensitivity (N2b)
| Method | Rejections / 500 | Rate | Wilson 95% | Classification |
|---|---|---|---|---|
| **Primary (whole-period circular shift)** | 119 | **0.238** | 0.203-0.277 | **inflated -> Q2 "sensitive"** |
| Within-season shift (exploratory) | 26 | 0.052 | 0.036-0.075 | inconclusive (upper bound 0.0751) |
| Truncated shift (exploratory) | 34 | 0.068 | 0.049-0.094 | inconclusive |

In N2b, median pooled D was 0.012 (95th percentile 0.032, maximum 0.053), and the p-value reached the 1/247 floor in 4.0% of replicates.

**Interpretation.** When a lead-lag structure that is *not* tied to the hourly wind co-varies seasonally with wind regimes, the whole-period circular shift moves wind into other seasons, the null distribution loses that structure, and the test rejects about five times too often. Restricting shifts to within seasons removed most of the inflation in this scenario. N2b was constructed to exhibit this threat; its strength is arbitrary, so the 23.8% is a demonstration of the mechanism, not an estimate of the error rate in the WBEA data.

### 5.3 Q3 Detection power (primary method; n = 200 each)
| Configuration | Amplitude | True lag | Median D (5-95%) | Power | Wilson 95% | Classification |
|---|---|---|---|---|---|---|
| P1_t007 | 0.0185 | 1 h | 0.069 (0.050-0.091) | 1.000 | 0.981-1.000 | adequate |
| P1_t013 | 0.0372 | 1 h | 0.131 (0.112-0.155) | 1.000 | 0.981-1.000 | adequate |
| P1_ceiling | 0.30 | 1 h | 0.195 (0.180-0.210) | 1.000 | 0.981-1.000 | adequate |
| P1_L2 | 0.30 | 2 h | 0.108 (0.092-0.126) | 1.000 | 0.981-1.000 | adequate |
| **P1_L3** | 0.30 | **3 h** | **-0.040** (-0.058 to -0.023) | **0.000** | 0.000-0.019 | **limited** |
| P1T_t013 | 0.0422 | transit | 0.131 (0.113-0.147) | 1.000 | 0.981-1.000 | adequate |
| P1T_ceiling | 0.30 | transit | 0.177 (0.164-0.195) | 1.000 | 0.981-1.000 | adequate |

- **Above the observed range (D >= 0.21): inconclusive.** Median pooled D saturates at about 0.20 (P1) and 0.18 (P1T) however strong the coupling (pilots; DEVIATIONS D3/D4).
- **Below and within the range up to about 0.20:** detection is complete. The p-value sat at the floor in every replicate.
- **Lag 3 is a negative finding.** When the true lag exceeds the lags carrying most of the frozen weight (transit times <= 3 h put weight mainly on lags 1-2), the first-differenced signal's negative short-lag autocorrelation turns D *negative* and the one-sided test never rejects. The H2 statistic can therefore miss, and reverse the sign of, coupling at longer true lags.

### 5.4 Q4 Falsification (N1b, n = 200)
All three methods rejected in 200/200 replicates (Wilson 0.981-1.000). Median pooled D was 0.132 (5-95%: 0.104-0.161; maximum 0.180), inside the lower half of the observed 0.13-0.29 range. **A shared meteorological signal advected with the wind, with no methane moving between stations, produces significant H2 values of realistic size.**

### 5.5 Baseline comparison (B1, ungated directional asymmetry with naive Fisher-z per pair)
| Scenario | Share of pairs "significant" | Mean abs asymmetry | H2 primary rejection |
|---|---|---|---|
| N0 | 6.3% | 0.010 | 4.6% |
| N1a | **82.3%** | 0.119 | 5.4% |
| N2b | 65.2% | 0.034 | 23.8% |
| N1b | 15.5% | 0.014 | 100% |
| P1_t013 | 9.6% | 0.009 | 100% |

A naive directed-network approach declares most pairs "directional" when stations simply respond to a common driver with different delays (N1a). It barely detects the true wind-conditioned coupling (P1: 9.6% of pairs). The H2 wind-reversal contrast removes wind-independent lead-lag structure (N1a stays at 5.4%) and detects wind-conditioned coupling. It does not remove seasonally co-varying structure (N2b) or advected shared signals (N1b).

## 6. Implications for the registered E08 result (D = 0.2879, p = 1/247)
1. **The decision stands.** E12 cannot alter the pre-registered confirmation.
2. **What p = 1/247 means.** It is a finite-shift reference p-value: none of the 246 shifted-wind statistics reached the observed one. E12 shows that this reference is approximately calibrated under the tested exchangeable nulls. It can be anti-conservative when non-wind-locked structure co-varies seasonally with wind regimes, the weakest point for a nine-month window spanning winter to summer.
3. **Magnitude context, descriptive only and not a calibration claim:** the observed 2026 D exceeds every simulated null D (calibration nulls max 0.042; N2b max 0.053) and the positive-model ceilings (about 0.18-0.20). N1b, an advected shared driver, reached 0.18. These magnitudes depend on simulator parameters and must not be used as probabilities.
4. **Interpretation.** A significant H2 is evidence of wind-dependent directional coupling. It is not evidence of methane transport between stations (N1b) and not evidence about lags beyond about 2 h (P1_L3).
5. **Recommended additional analysis (requires separate authorisation; post-confirmation exploratory):** apply the within-season shift reference to the 2026 confirmation data as a sensitivity, reported separately and never substituted for the registered p.

## 7. Limitations
- A single simulator family. Station wind deviations are modelled as independent hourly scatter; there is no vertical structure, terrain flow or real emission geometry.
- N2b and N1b are constructed demonstrations; their effect sizes are arbitrary.
- The 0.075 calibration margin is a pre-registered convention. With 500 replicates the Wilson interval width is about ±2 percentage points, so classifications near the margin are sensitive.
- The truncated-shift alternative approximates, and does not reproduce, Yuan and Shou's exact test.
- Power above D = 0.21 was not testable; the positive models do not reproduce the observed 2026 magnitude.
- Alternatives reuse the frozen lag weights; their pooled weights come from their own shift sets.

## 8. Proposed manuscript language (EMS)
> "In a pre-registered synthetic study (4,100 replicates; 11-station geometry, 21 pairs, 246 admissible shifts), the shifted-wind test rejected at 4.6-5.4% under four null scenarios with autocorrelation, common drivers with station-specific delays, seasonal drift and realistic gaps (all Wilson 95% intervals included 0.05). Rejection rose to 23.8% (95% CI 20.3-27.7%) when a non-wind-locked lead-lag pattern co-varied seasonally with wind regimes, and fell to 5.2% (3.6-7.5%) with within-season shifts. The test detected injected wind-conditioned coupling with D of 0.07-0.20 in all replicates, but not coupling at a 3 h lag. A wind-advected shared signal with no inter-station methane transport was detected in all replicates. We therefore interpret the confirmed H2 result as wind-dependent directional coupling compatible with, but not demonstrating, transport, and its finite-shift p-value as conditional on seasonal exchangeability."

## 9. Reproduction
`make test` (7 tests) · `make production` (about 40 min) · `make analysis`. Outputs: `results/summary_by_scenario_method.csv`, `results/verdicts.json`, `results/raw_*.csv`, `figures/e12_null_rejection_rates.*`, `figures/e12_null_pvalue_cdf_and_D.*`, `figures/e12_power.*`. Environment: `requirements.txt` (Python 3.12.3).
