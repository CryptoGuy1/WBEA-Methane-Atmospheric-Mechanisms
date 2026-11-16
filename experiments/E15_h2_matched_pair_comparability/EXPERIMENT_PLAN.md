# E15 (Experiment A): Matched-pair and temporal comparability of the H2 directional statistic
**Status:** POST-CONFIRMATION EXPLORATORY, descriptive. Plan committed before any new statistic is computed. The 2026 data were already opened by the registered confirmation, so nothing here is independent confirmation. No frozen file, result or decision changes; no comparison can alter the registered H2 result.

## 1. Question
How much of the numerical difference between the published development statistic (pooled D = 0.1285) and the frozen 2026 statistic (D = 0.2879) is associated with differences in:
- the reference construction;
- the calendar window;
- the pair set;
- the leave-pair-out residual universe;
- pooling weights;

and how much remains within the same pairs across periods? The quantity of interest is the comparability of two numbers. It is not a physical effect: D is not a transport, coupling or emission measure.

## 2. Audit (completed before this plan)
- **Point estimator.** `src/wbea/h2.py` (frozen) documents that its logic is identical to the local functions in `experiments/E05_directional_coupling/run_e05.py`; the residual, wind, set, weight and statistic code match line for line. *Verified empirically below (gate G1) before use.*
- **Reference construction differs.** E05 uses 1,000 seeded random whole-day shifts from [14, N_d - 14) over the full development window (2021-01-01 01:00 to 2025-12-02 00:00; 12 stations). E08 uses all 246 admissible shifts (k = 14..259) over Jan-Sep 2026 (11 stations). Pair weights are 1/Var(null) from each analysis's own reference.
- **Pair sets.** Development has 27 pairs; confirmation 21. The intersection is exactly the 21 confirmation pairs, with identical orientation (i->j, bearing). The 6 development-only pairs all involve AMS 2 (`AMS 1->AMS 2`, `AMS 2->AMS 5`, `AMS 2->AMS 9`, `AMS 2->AMS 11`, `AMS 2->AMS 13`, `AMS 2->AMS 30`).
- **Residual universe.** The leave-pair-out median uses all other *retained* stations (>= 4 needed). Removing AMS 2 therefore changes the regional reference of every remaining pair, not only the pairs containing AMS 2.

## 3. Analyses (all with the frozen statistic via E13/E14 helpers; development data unless stated)
| ID | Window | Station universe (residuals) | Pairs | Reference | Role |
|---|---|---|---|---|---|
| A0 | Full development (1,796 d) | 12 | 27 | E05 random 1,000 (saved) | published development (reproduced from saved files) |
| A1 | Jan-Sep 2026 | 11 | 21 | all 246 (saved) | frozen confirmation (reproduced from saved files) |
| A2 | Full development | 12 | 27 | all admissible (k = 14..1782) | reference effect: A0 -> A2 |
| A2b | Full development | 11 | 21 | all admissible | for the alternative path order |
| A3 | Jan-Sep 2021-2025 pooled | 12 | 27 | joint within-year shift, k = 14..259 | window effect: A2 -> A3 |
| A3y | Jan-Sep, each year | 12 | 27 | all 246 per year | interannual spread |
| A4 | Jan-Sep 2021-2025 pooled | 12 | 21 (shared) | within-year, k = 14..259 | pair restriction: A3 -> A4 |
| A5 | Jan-Sep 2021-2025 pooled | 11 | 21 | within-year, k = 14..259 | residual universe: A4 -> A5 |
| A5y | Jan-Sep, each year | 11 | 21 | all 246 per year | interannual spread, confirmation network |
| A6 | Jan-Sep 2026 | 12 (AMS 2 included) | 27 | all 246 | 2026 network composition, exploratory |
| A7 | Jan-Sep 2026 | 12 (AMS 2 included) | 21 | all 246 | 2026 residual-universe contrast (A7 vs A1) |

- **Pooled Jan-Sep (A3, A4, A5):** each year's window (hours ending 1 Jan 01:00 to 1 Oct 00:00; 29 Feb 2024 removed, as in E14) is processed separately: residuals, first differences and lagged products never cross a year boundary. Aligned and reversed sufficient statistics are summed over years. Transit-lag weights are computed on the combined aligned/reversed hours. The >= 100 aligned and reversed eligibility rule applies to the combined counts. Each surrogate applies the same within-year circular shift k to every year and pair. *This is an exploratory construction, not a frozen procedure.*
- **A6/A7:** these override the frozen coverage exclusion of AMS 2 (41.2% valid) *only* to isolate network composition at fixed period. They never replace A1.

## 4. Pre-specified comparisons
1. **Context:** A0 vs A1.
2. **Common pairs:** A5 vs A1 (21 pairs, same 11-station universe; development Jan-Sep pooled vs 2026).
3. **Calendar window:** A2 vs A3, and the spread of A3y and A5y; full-period context.
4. **Network composition, fixed period:** A3 vs A4 (development); A6 vs A7 (2026).
5. **Residualisation:** A4 vs A5 (development); A7 vs A1 (2026).
6. **Pooling weights:** for the 21 shared pairs, D_ij, null SD, normalised weights and contributions w_ij D_ij in A5 and A1. Descriptive cross-weighted pools: 2026 D_ij with A5 weights, A5 D_ij with 2026 weights, and equal weights in both. Effective number of pairs = 1 / sum(w^2). These are never confirmatory.
7. **Reference construction:** A0 vs A2: same data, pairs and point estimates; only the reference (and hence weights) differs.

**Decomposition.** A telescoping path A0 -> A2 -> A3 -> A4 -> A5 -> A1 is *exact by construction* (successive differences sum to the total) but order-dependent. One alternative order, A0 -> A2 -> A2b -> A5 -> A1, is reported to show the order sensitivity. No additive attribution beyond these two paths is claimed. Interactions are reported as the difference between the orders.

**Pair-level diagnostics (A5 and A1):**
- D_ij, sign, aligned/reversed hours and null SD;
- weight and contribution;
- eligibility in each window;
- leave-one-pair-out pooled D (with the other pairs' precisions renormalised).

**Period environment (descriptive, 21 pairs, 11-station universe; each development Jan-Sep year and 2026):**
- aligned and reversed hours;
- median wind speed on eligible hours;
- SD of residual changes;
- methane valid-hour coverage;
- effective number of pairs.

## 5. Gates and uncertainty
- **G1:** A2's per-pair D_ij must equal E05's saved D (to E05's 5-decimal rounding), and A0 must reproduce the saved E05 pooled value (0.1285) from the saved null. A1 must reproduce 0.2879317084641316. If any fails, stop and report.
- **G2:** E14's parity anchor (2025 Jan-Sep, 12 stations, 27 pairs: 0.18411446516401547) must be reproduced by A3y[2025].
- **Uncertainty:** pairs share stations, hours and regional forcing, so no independent-sample standard errors are computed. Differences are descriptive. The interannual spread of the development Jan-Sep years (A3y, A5y) is reported as empirical context, not as a sampling distribution. The method is deterministic (no random numbers).

## 6. Protections
- No frozen E08, E12, E13 or E14 file is modified.
- The 2026 sealed panel is read only by this experiment's own loader, under a named, documented seal-test exemption (as for E13).
- No restriction is chosen by its outcome; all analyses above are reported.
- No manuscript file is touched.
