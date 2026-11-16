# E15 (Experiment A): Matched-pair and temporal comparability of the H2 directional statistic. Report
**Status:** POST-CONFIRMATION EXPLORATORY and descriptive. The 2026 data were already opened by the registered confirmation, so nothing here is independent confirmation. No frozen E08, E12, E13 or E14 file, result or decision was modified; no manuscript file was touched.
**Commits:** plan `f8e6e0b` (before any computation) -> implementation and tests `fc56f1d` (before the production run) -> results (see `MANIFEST.md`).

## 1. Executive summary
The published development statistic (D = 0.1285) and the frozen 2026 statistic (D = 0.2879) differ by **0.159**. The pre-specified analyses separate the reference construction, calendar window, pair set and residual universe from the period itself:
- **Reference construction** (1,000 random shifts -> all admissible shifts): **+0.0008**.
- **Calendar window** (full period -> pooled Jan-Sep): **-0.0031**.
- **Pair set** (27 -> 21 shared pairs): **+0.0045**.
- **Residual universe** (AMS 2 removed from the leave-pair-out median): **+0.0068**.
- **Together:** **+0.0090 (about 6% of the gap), in both decomposition orders.**
- **Remaining difference between periods** for the same 21 pairs, same 11-station universe and same Jan-Sep calendar: **+0.150 (about 94%).**

**The difference is therefore not an artefact** of AMS 2's exclusion, the window or the reference. It is a period difference among identical pairs: the 2026 value exceeds every development Jan-Sep year analysed the same way (0.077-0.202).

**But it is heterogeneous:**
- 17 of 21 pairs increased, with no single pair driving the pool (leave-one-pair-out changes <= 0.009).
- The four shortest pairs (2.7-6.0 km), which had the largest development values, all **decreased**; the change correlates with separation (r = 0.66).
- The size of the gap depends materially on the weighting: 0.150 with each period's own inverse-null-variance weights, 0.141 with the development weights, 0.119 with the 2026 weights, and 0.086 with equal weights.

**Measured observing conditions don't explain it.** Aligned and reversed hours, wind speed, residual variability and methane completeness in 2026 all fall within the development years' range.

**No physical interpretation follows.** D is not a transport, coupling or emission measure.

## 2. Question
How much of the development-confirmation difference in pooled D is associated with pair composition, calendar window, residualisation, weights and reference construction, and how much remains within the same pairs across periods? This is a comparability question about two numbers, not a physical question.

## 3. Audited definitions
- **Point estimator:** identical. E05's local functions and the frozen `src/wbea/h2.py` match line for line (documented as decision D-26). Verified: the frozen method on the full development window reproduces E05's saved per-pair D for all 27 pairs within E05's 5-decimal rounding (max difference 4.97e-6).
- **Reference construction:** different, and the only algorithmic difference.

| | Development (E05) | Confirmation (E08) |
|---|---|---|
| Window | full 2021-01-01 01:00 to 2025-12-02 00:00 | Jan-Sep 2026 |
| Station universe | 12 | 11 |
| Shifts | 1,000 seeded random whole-day shifts | all 246 admissible shifts |
| Pair weights | 1/Var(null) of its own reference | 1/Var(null) of its own reference |

- **Reproduction gates (all passed):**
  - G1: A0 = 0.12850 from E05's saved D and saved null; A1 = 0.2879317084641316 from the saved frozen matrices; A1 recomputed through E15's own loader agrees to 5.6e-17.
  - G2: the pooled-window code on the single 2025 window reproduces the frozen dry run (0.18411446516401547) to 5.6e-17.

## 4. Pair lists
- **Development:** 27 pairs. **Confirmation:** 21.
- **Intersection:** exactly the 21 confirmation pairs, with identical orientation (i->j, bearing). No confirmation pair is new.
- **Development only (6):** `AMS 1->AMS 2`, `AMS 2->AMS 5`, `AMS 2->AMS 9`, `AMS 2->AMS 11`, `AMS 2->AMS 13`, `AMS 2->AMS 30`. All involve AMS 2.
- **Indirect effect:** removing AMS 2 also changes the leave-pair-out regional median of *every* remaining pair (verified by test), so its exclusion is not only a pair deletion.

## 5. Results of the controlled comparisons (`results/summary_table.md`, `comparison_table.csv`)
| ID | Configuration | Pairs | Reference | Pooled D | Null SD | z |
|---|---|---|---|---|---|---|
| A0 | Published development (full period) | 27 | 1,000 random | **0.1285** | 0.0090 | 14.38 |
| A2 | Full period, frozen-style reference | 27 | all 1,769 | 0.1293 | 0.0089 | 14.55 |
| A2b | Full period, 21 pairs, 11-station universe | 21 | all 1,769 | 0.1379 | 0.0111 | 12.42 |
| A3 | Jan-Sep 2021-2025 pooled* | 27 | within-year k = 14..259 | 0.1262 | 0.0111 | 11.38 |
| A4 | as A3, 21 shared pairs (AMS 2 in universe)* | 21 | same | 0.1307 | 0.0127 | 10.23 |
| A5 | as A4, 11-station universe* | 21 | same | **0.1375** | 0.0141 | 9.66 |
| A5y | each Jan-Sep 2021 / 2022 / 2023 / 2024 / 2025 (21 pairs, 11 stations) | 21 | all 246 | 0.1224 / 0.1526 / 0.0768 / 0.1815 / 0.2019 | 0.018-0.039 | 4.4-5.8 |
| A3y | each Jan-Sep, 27 pairs, 12 stations | 27 | all 246 | 0.1283 / 0.1512 / 0.0820 / 0.1492 / 0.1841 | | 5.5-6.9 |
| A1 | **2026 frozen confirmation** | 21 | all 246 | **0.2879** | 0.0410 | 6.99 |
| A7 | 2026, AMS 2 in residual universe** | 21 | all 246 | 0.2749 | 0.0396 | 6.93 |
| A6 | 2026, AMS 2 retained, 27 pairs** | 27 | all 246 | **not evaluable** | | |

\* Exploratory pooled construction: per-year sufficient statistics summed; no lag crosses a year boundary; the same within-year shift for all years and pairs.
\*\* Overrides the frozen exclusion of AMS 2 solely for diagnosis.

All p-values are at their finite floors (1/1001, 1/1770 or 1/247), so p conveys nothing about magnitude. **z is not an effect size:** the 2026 null SD (0.041) is about three times that of the pooled development analysis.

**Decomposition** (telescoping; exact by construction but order-dependent; `decomposition_paths.csv`):

| Step | Path 1 | Path 2 |
|---|---|---|
| Reference (A0 -> A2) | +0.0008 | +0.0008 |
| Window | -0.0031 (A2 -> A3) | -0.0004 (A2b -> A5) |
| Pair set | +0.0045 (A3 -> A4) | +0.0086, pairs and universe together (A2 -> A2b) |
| Residual universe | +0.0068 (A4 -> A5) | (combined above) |
| **Period, same pairs/universe/window type (A5 -> A1)** | **+0.1505** | **+0.1505** |
| Total | 0.1594 | 0.1594 |

The order changes only how the small non-period part (0.0090) is split between window and composition. That interaction is small (the window step is -0.0031 vs -0.0004). No further additive attribution is claimed.

**2026 residualisation (A7 vs A1):** keeping AMS 2 in the 2026 residual universe lowers pooled D by 0.013. This is consistent in sign and size with the development step A4 -> A5 (+0.007).

## 6. Calendar-window comparability
- **Window effect is small:** restricting development to Jan-Sep changes pooled D by -0.003 (27 pairs) or -0.0004 (21 pairs, 11 stations).
- **Single years are evaluable:** each development Jan-Sep year has K = 246 and 21-27 eligible pairs.
- **Interannual spread (21 pairs, 11 stations):** 0.077-0.202 (mean 0.147, SD 0.049, five years). 2026 (0.288) lies above all five, 2.85 SDs above their mean. This is descriptive only: five dependent years are not a sampling distribution.
- **Matching calendar months is not matching meteorology,** but the measured environment is similar (section 9).

## 7. Regional residualisation
The leave-pair-out universe matters but is minor: +0.0068 (development) and +0.013 (2026) when AMS 2 is removed. Both point in the same direction, and both are small relative to the period difference.

## 8. Pooling weights (`weight_sensitivity.csv`, `shared_pairs_A5_vs_A1.csv`)
| Weighting | Development Jan-Sep pooled | 2026 | Gap |
|---|---|---|---|
| Own inverse-null-variance (registered style) | 0.1375 | 0.2879 | **0.150** |
| Development weights for both | 0.1375 | 0.2786 | 0.141 |
| 2026 weights for both | 0.1688 | 0.2879 | 0.119 |
| Equal weights | 0.2196 | 0.3060 | **0.086** |

The weighting materially modifies the *size* of the gap (0.086-0.150) but not its sign. Inverse-null-variance weights down-weight the short pairs, which have large D in development and large null variance. Equal weighting therefore raises the development value more than the 2026 value. Weights are more concentrated in development (effective pairs 15.2; maximum weight 0.108) than in 2026 (18.3; 0.078). These are descriptive; the registered statistic uses its own weights.

## 9. Period environment (21 pairs, 11 stations; `period_environment.csv`)
| | Development Jan-Sep 2021-2025 (range) | Jan-Sep 2026 |
|---|---|---|
| Aligned hours | 26,174-29,582 | 27,948 |
| Reversed hours | 25,639-28,354 | 26,938 |
| Median wind speed, eligible hours (m/s) | 2.97-3.09 | 3.09 |
| SD of residual change (ppm) | 0.111-0.184 | 0.116 |
| CH4 coverage (11 stations) | 0.906-0.935 | 0.917 |

**No measured data-environment variable separates 2026 from the development years.** The difference therefore remains **unexplained** by the quantities examined. It is not attributable to emissions or to physical coupling on this evidence.

## 10. Pair-level heterogeneity and influence
- **Direction:** 17/21 pairs have larger D in 2026 (median change +0.109; range -0.285 to +0.301). In 11/21 pairs the 2026 value exceeds all five development years.
- **The four decreases are the four shortest pairs:**

| Pair | Separation | Development -> 2026 |
|---|---|---|
| AMS 1->AMS 9 | 2.7 km | 0.73 -> 0.52 |
| AMS 1->AMS 13 | 4.5 km | 0.70 -> 0.41 |
| AMS 6->AMS 7 | 5.6 km | 0.12 -> 0.10 |
| AMS 9->AMS 13 | 6.0 km | 0.68 -> 0.46 |

  Across pairs, change correlates with separation (r = 0.66). The rise is concentrated at longer separations.
- **Influence:** leave-one-pair-out pooled D moves by at most 0.009 (2026) and 0.013 (development). No pair dominates the pooled statistic.
- **Eligibility:** every shared pair is eligible in every window analysed.

**Figure** (`figures/e15_comparability.{pdf,svg,png}`):
- **(a)** Pooled D through each controlled step, the five development Jan-Sep years and the 2026 confirmation.
- **(b)** Per-pair D: development (Jan-Sep pooled) against 2026, coloured by separation, marker size proportional to the 2026 weight, with the 1:1 line.

## 11. Interpretation
- **Comparability:** the published development and confirmation values are comparable *in algorithm*: same point estimator, and a reference difference that is numerically negligible. They are **not comparable as effect sizes**: on identical pairs and calendar months the two periods differ substantially, the difference varies across pairs, and its size depends on the weighting.
- **Compositional vs temporal:** compositional and residualisation differences are small (+0.011 combined) relative to the temporal (period) difference (+0.150).
- **Not identifiable:** why 2026 differs. Candidate explanations include interannual meteorological structure not captured by the measured summaries, changes in local sources or background variability, and instrument behaviour. None can be distinguished with these data, and none is claimed.

## 12. Uncertainty and limitations
1. **No sampling-based uncertainty for differences.** Pairs share stations, hours and regional forcing, so no independent-sample standard errors were computed. The development-year spread is reported only as context.
2. **The pooled Jan-Sep construction (A3-A5) is exploratory.** The single-year analyses (A3y, A5y) use the frozen procedure exactly.
3. **A6 is not evaluable** (DEVIATIONS D2): AMS 2 has no valid methane from May 2026, so some surrogates are undefined. The 2026 27-vs-21-pair contrast is unavailable.
4. **Matched calendar windows are not matched meteorology.** The environment summaries are coarse.
5. **Already-opened 2026 data:** every comparison involving 2026 is post hoc.
6. **No claim** about transport, coupling strength, emissions or causes.

## 13. Not mathematically identifiable
- A unique additive attribution: the decomposition is order-dependent, and only two orders are reported.
- The separation of weighting from pair-level change in the period step: these interact, as the weight-scheme table shows.
- Any causal component of the period difference.

## 14. Relationship to existing H2 findings
- **E05 and E08:** both reproduced exactly; registered decisions unchanged.
- **E12 (calibration and specificity), E13 (season-restricted references) and E14 (cross-year negative control)** address whether the *test* is valid. E15 addresses whether the *magnitudes* are comparable. Its findings are consistent with the reporting amendment D-73: the H2 magnitudes should not be compared as effect sizes. E15 now quantifies *why*: not composition, window or reference, but a heterogeneous period difference among the same pairs.

## 15. Reproducibility and tests
- **Reproduce:** `python run_e15.py && python analyze_e15.py` (deterministic; production run 29 s).
- **Tests:** E15 tests 10/10 pass. Full regression suite (repository, E12, E13, E14, E15): **70 passed**.
- **A6 in the run log:** the run log lists no issues because A6 returned a summary with undefined values, not an empty pair set. A6 is documented in DEVIATIONS D2 and `results/A6_nonevaluable_surrogates.csv`.
- **Seal-test exemption** for this folder: DEVIATIONS D1.
- **Frozen files** verified unchanged against `protocol-freeze`, `e08-confirmation`, and the E12, E13 and E14 commits.

## 16. Recommendation
- **A. Does controlling pair composition materially change the comparison?** No. Composition and residual universe together move pooled D by about +0.011, roughly 7% of the gap.
- **B. Do matched Jan-Sep windows materially change it?** No (-0.003 to -0.0004). The 2026 value exceeds every matched development year.
- **C. Do residualisation and weights explain a meaningful portion?** Residualisation: no. Weights: they do not explain the difference, but they materially modify its size (0.086 equal-weighted vs 0.150 registered-style).
- **D. Robust or concentrated?** Broad (17/21 pairs; no single pair influential) but heterogeneous: the shortest pairs decreased, and the change correlates with separation.
- **E. Does this change the interpretation of the H2 confirmation?** It does not change the registered result. It strengthens one point: the larger 2026 value is **not** an artefact of AMS 2's exclusion, the window or the reference, so it must not be presented as a like-for-like increase either. The difference is real in the data but unexplained, heterogeneous by separation, and weight-sensitive.
- **F. Inclusion:** **a short main-text statement (one or two sentences in section 4.2) plus Supplementary Material** (comparison table, shared-pair table, figure). No main-text figure.
- **G. New beyond E12-E14?** Yes. E12-E14 concern the validity of the test. E15 is the only analysis of magnitude comparability, and it answers the reviewer question likely to arise from 0.128 vs 0.288.
