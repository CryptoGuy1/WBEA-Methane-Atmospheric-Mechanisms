# E13 Report: Seasonal-shift sensitivity of the 2026 H2 result

**POST-CONFIRMATION EXPLORATORY sensitivity analysis.** It does not re-test or replace the registered E08 decision (H2 confirmed; D = 0.287931708, p = 1/247). Branch `research/e13-h2-seasonal-shift-sensitivity`; the final SHA is in `E13_MANUSCRIPT_HANDOFF.md` and the handoff message. Numbers come from `run_e13.py` (deterministic) on the sealed 2026 panel.

## 1. Bottom line
**The 2026 H2 statistic remains extreme under every pre-registered season-restricted reference.**
- **Pooled configurations.** Calendar quarters and cold/warm halves, with own or frozen weights: 0 of 63 and 0 of 93 surrogates reached the observed value, p at the floor (1/64 = 0.0156; 1/94 = 0.0106), and the observed D lies 7.2-7.7 null SDs above the surrogate mean.
- **Each quarter analysed separately:** the same, with D = 0.347, 0.216 and 0.201.

Under the pre-registered rule the outcome is **"strengthens"**. Precisely: E13 strengthens the *statistical robustness of the H2 result to the choice of shift reference*, addressing the seasonal-exchangeability concern raised by E12. **It does not strengthen any physical-transport interpretation.** E12's falsification result (an advected shared signal is always detected) and its 3 h lag blind spot are unaffected.

## 2. Motivation and literature context
Time-shift (circular or truncated) surrogates preserve each series' autocorrelation and test only alignment. Their validity rests on exchangeability or stationarity assumptions:
- Yuan & Shou (2024, *PLOS Biology*, doi 10.1371/journal.pbio.3002758) show nonparametric shift tests can be invalid when stationarity fails, and give a truncated-shift test valid under stationarity.
- Lancaster et al. (2018, *Physics Reports*, doi 10.1016/j.physrep.2018.06.001) review surrogate construction and its pitfalls.
- Zheng & Chen (2026, *Atmosphere* 17:588, doi 10.3390/atmos17060588) use within-year circular shifts for directed pollution-event networks.

In E12 (synthetic), the frozen whole-period shift was anti-conservative under constructed seasonal confounding (N2b: 23.8% at alpha 0.05), while a within-season shift gave 5.2% (3.6-7.5%). E13 applies that within-season construction, plus a second, pre-registered partition, to the real 2026 data.

## 3. Data and reproducibility
- **Data:** sealed 2026 panel (`sealed/e08_panel`, 12 files, SHA-256 verified), 1 Jan 01:00 - 1 Oct 00:00 2026 MST hour-ending, 6,552 h.
- **Frozen inputs:** 2021-2023 reference medians; E08 station-coverage rule (AMS 2 excluded, 41.2%); composite station wind; 21 pairs within 30 km.
- **Frozen functions:** `wbea.h2` and `wbea.e08` at `protocol-freeze` (2b7c79e). Fast routines from E12 (parity-tested to 1e-9) are imported read-only.
- **Reproduction check (test):** the whole-period path reproduces the frozen pooled D to < 1e-12 and p = 1/247 with K = 246, and per-pair D to the 5-decimal precision of `h2_pairs.csv`.
- **Commits:** plan 2d7227c (before any seasonal 2026 statistic); implementation and tests babd0bd (before the analysis run). Six tests pass.

## 4. Methods
**Frozen statistic.** For pair (i, j):
- leave-pair-out residuals R_i = X_i - median of the other stations (at least 4 valid);
- first differences dR;
- aligned set A and reversed set V from the pair-mean station wind (|U_par| >= 1 m/s, cos >= 0.707, tau <= 3 h);
- rho_l(S) = corr(dR_i(t-l), dR_j(t) | S) - corr(dR_j(t-l), dR_i(t) | S), with all four values finite;
- D_ij = sum over l = 1..3 of w_l [rho_l(A) - rho_l(V)], with w_l from transit times over A and V;
- pooled D = sum of omega_ij D_ij, with omega_ij proportional to 1 / Var_k(D_ij^(k)).

**p-value:** p = (1 + #{k : D^(k) >= D_obs}) / (K + 1).

**Joint within-season circular shift (C1, C2).** For shift k the wind in each block b is rotated by k whole days *within the block*:

```latex
U^{(k)}(t) = U\big(a_b + ((t - a_b - 24k) \bmod L_b)\big), \qquad t \in [a_b, a_b + L_b)
```

The same k is applied to every block; methane is not shifted.
- C1: Jan-Mar / Apr-Jun / Jul-Sep (90/91/92 d; k = 14-76; K = 63).
- C2: Jan-Apr / May-Sep (120/153 d; k = 14-106; K = 93).
- Monthly blocks were considered and rejected: at most 4 admissible shifts.

The procedure is implemented as within-block FFT circular cross-correlations of the six per-hour moment series with each mask, checked in tests against an explicit within-block roll, including wraparound.

**Invariances.** Observed per-pair D are unchanged (k = 0). Pair eligibility is unchanged (computed on unshifted wind). Transit-time weights are shift-invariant (within-block rotation permutes hours inside blocks; tested).

**Weighting variants:**
- **-w:** pooling weights from the season null's own variances. This is the E12 construction, so the observed pooled D differs slightly from 0.2879.
- **-f:** the frozen E08 weights. The observed pooled D is exactly 0.2879, isolating the effect of the reference distribution.

**C4 (separate per-season statistics; a different procedure, not interchangeable):** each quarter is analysed on its own. Residual levels are sliced, differences are taken within the quarter (no lag crosses its boundary), eligibility and weights come from the quarter's hours, and the null is a within-quarter circular shift (k = 14 to L - 14). No combined p.

**Interpretation rules (pre-registered):** p <= 0.05 "remains unusual"; p > 0.10 "not unusual"; otherwise "borderline". Overall: "strengthens" if C1-w and C2-w both remain unusual; "materially challenges" if C1-w is not unusual; otherwise "qualifies".

## 5. Results
### 5.1 Pooled configurations (21 pairs each)
| Configuration | K | p floor | Observed pooled D | Surrogates >= obs | p | Null mean | Null SD | Null 95% / 99% / max | z (descriptive) | Classification |
|---|---|---|---|---|---|---|---|---|---|---|
| R0 frozen whole-period (reproduction) | 246 | 0.0040 | **0.2879** | 0 | **0.0040** | 0.0010 | 0.0410 | 0.070 / 0.095 / 0.101 | 6.99 | (frozen) |
| **C1-w** quarters, own weights | 63 | 0.0156 | 0.2871 | 0 | **0.0156** | 0.0056 | 0.0373 | 0.057 / 0.063 / 0.067 | 7.55 | **remains unusual** |
| C1-f quarters, frozen weights | 63 | 0.0156 | 0.2879 | 0 | 0.0156 | 0.0046 | 0.0394 | 0.058 / 0.063 / 0.066 | 7.19 | remains unusual |
| **C2-w** halves, own weights | 93 | 0.0106 | 0.2877 | 0 | **0.0106** | 0.0065 | 0.0366 | 0.075 / 0.095 / 0.099 | 7.68 | **remains unusual** |
| C2-f halves, frozen weights | 93 | 0.0106 | 0.2879 | 0 | 0.0106 | 0.0063 | 0.0372 | 0.076 / 0.097 / 0.101 | 7.56 | remains unusual |

**Weighting effect:** negligible. Observed pooled D is 0.2871-0.2879 across weightings; the largest single-pair weight share is 0.113 (C1 own) against 0.078 (frozen).

**Reference-distribution effect:**
- Season-restricted nulls are slightly *narrower* (SD 0.037 vs 0.041) and centred slightly higher (mean 0.005-0.007 vs 0.001) than the whole-period null.
- Restricting shifts within seasons therefore did not widen the reference enough to approach the observed value; the largest surrogate in any configuration was 0.101.

**Pair level (C1 / C2, descriptive):**
- 21/21 pairs had D > 0.
- 20/21 and 19/21 had per-pair p <= 0.05.
- 18/21 and 17/21 were at the per-pair floor.

### 5.2 Separate per-season statistics (C4)
| Quarter | Days | Pairs | Station CH4 coverage (min / mean) | K | Observed pooled D | Surrogates >= obs | p | Null mean / SD / max | z | Classification |
|---|---|---|---|---|---|---|---|---|---|---|
| Jan-Mar | 90 | 21 | 0.73 / 0.92 | 63 | **0.347** | 0 | 0.0156 | 0.005 / 0.058 / 0.148 | 5.88 | remains unusual |
| Apr-Jun | 91 | 21 | 0.55 / 0.89 | 64 | **0.216** | 0 | 0.0154 | 0.000 / 0.035 / 0.072 | 6.21 | remains unusual |
| Jul-Sep | 92 | 20 | 0.91 / 0.94 | 65 | **0.201** | 0 | 0.0152 | -0.008 / 0.060 / 0.110 | 3.49 | remains unusual |

- **Seasonal pattern.** The directional statistic is largest in winter and smaller in spring and summer, but extreme relative to its own within-quarter reference in every quarter.
- **Coverage.** Apr-Jun had the lowest station coverage (minimum 0.55).
- **Pairs.** Jul-Sep lost one pair through the eligibility rule.
- **Not comparable across seasons.** Per-quarter D values use different hours, pairs and weights.

### 5.3 Overall rule outcome
C1-w and C2-w both "remain unusual", so the outcome is **"strengthens"**.

## 6. Statistical validity assessment
1. **These are not exact tests.** Within-season shifts assume exchangeability *within* each block. Seasonal transitions inside a block (for example the March-April thaw, or the June transition) and wraparound at block edges (late-quarter wind paired with early-quarter methane) remain.
2. **What E12 established about this procedure.** In synthetic scenarios it rejected at 6.2% (N0), 6.6% (N1a), 4.2% (N2a), 4.6% (N3) and 5.2% (N2b). Two were classified *calibrated* and three *inconclusive* under E12's margin; none was *inflated*. That supports approximate calibration under those scenarios only.
3. **Resolution.** The p-floors of 1/64 and 1/94 cap how small p can be. Every configuration hit its floor, so the p-values cannot be ranked against each other or against 1/247. The z-scores are descriptive; the null distributions are not assumed normal.
4. **Multiplicity.** Five pooled configurations plus three per-season analyses were run; all were pre-registered and are all reported. Because every outcome is at its floor, no selection among them occurred.
5. **Why the result is robust to this concern.** In E12's N2b, confounding inflated rejection through small shifts of D (median 0.012; maximum 0.053). In 2026 the observed D (0.288) is roughly three times the maximum surrogate under any construction (0.067-0.101). Seasonal confounding of the magnitude simulated in E12 cannot plausibly explain it.

## 7. Limitations and potentially misleading interpretations
- **Not a transport result.** E12's N1b showed an advected shared meteorological signal, with no methane moving between stations, produces significant H2 values (median D 0.13, rejection 100%). E13 does not address this.
- **Not about longer lags.** E12 showed coupling at a 3 h true lag is missed; E13 inherits that blind spot.
- **Do not read the p-values as a ranking.** A larger p under season-restricted shifts (0.0156 vs 0.0040) reflects fewer surrogates, not weaker evidence.
- **Do not compare per-quarter D across seasons.** They use different hours, pairs and weights.
- **Only one alternative grouping was tested** (C2). Other boundaries (for example snowmelt dates) were not tried, to avoid boundary selection; monthly blocks are infeasible.
- **Same data, same uncertainties.** The 2026 data remain subject to WBEA's annual validation review; AMS 2 is excluded as in E08.

## 8. Implications for the EMS manuscript
- **Statement.** E13 *strengthens* the statistical robustness of the confirmed H2 result to the choice of shift reference, and *does not change* its interpretive limits.
- **Recommended wording:**

  > "Because whole-period circular shifts can be anti-conservative under seasonal confounding (E12), we repeated the reference construction with shifts restricted to calendar quarters and to cold/warm halves (post-confirmation exploratory). The 2026 statistic exceeded all 63 and 93 surrogates respectively (p at the reference floors of 1/64 and 1/94; observed D 0.288 against maximum surrogate values of 0.067 and 0.099), and remained extreme when each quarter was analysed separately (D = 0.35, 0.22, 0.20). The directional-coupling result is therefore not an artefact of mixing seasons in the shift reference; it remains compatible with, but does not demonstrate, wind-driven transport."
- **Placement:** Figure `e13_fig1_reference_distributions` in the main text, next to the E12 calibration figure, or in the SI if space is limited. `e13_fig2_per_season` and both tables in the SI.

## 9. Outputs
`results/e13_summary.csv`, `results/e13_per_season.csv`, `results/e13_pairs_C1.csv`, `results/e13_pairs_C2.csv`, `results/e13_surrogates_*.csv` (all surrogate pooled-D values), `results/e13_results.json`, `figures/e13_fig1_reference_distributions.{png,svg,pdf}`, `figures/e13_fig2_per_season.{png,svg,pdf}`.
