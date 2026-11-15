# E14 (Experiment B): Empirical year-swapped null for the frozen H2 test. Report
**Status:** POST-CONFIRMATION EXPLORATORY. Development data only. No frozen code, output, decision or manuscript file was modified.
**Commits:** plan `05440d4` (before any swap result) -> implementation and tests `666e7e8` (before the production run) -> results (see `RESULTS_COMMIT.txt`).

## 1. Executive summary
**Question.** Does seasonal co-variation that actually exists in WBEA observations make the frozen whole-period shifted-wind reference reject when there is no hour-level wind-methane coupling? E12 showed that a *constructed* seasonal confounder can inflate rejection to 23.8%. Whether the real network contains confounding of damaging size had not been tested.

**Design.** Real development methane from year Y was combined with real winds from a different year Y', aligned by calendar date and hour (Jan-Sep; 29 Feb removed). The complete frozen H2 procedure was then run. This preserves real seasonality, persistence, diurnal cycles, common drivers, station heterogeneity and missingness without fitted parameters, while removing all hour-level coupling. All 20 ordered year combinations were run (an exhaustive enumeration), plus 5 same-year anchors with real coupling. Both the frozen station rule and the 2026 station set were used.

**Result (pre-specified rule).** The frozen whole-period reference rejected **1 of 20** year-swapped replicates: **5.0%, Wilson 95% CI 0.9-23.6%**. This falls in the **"no evidence of inflation"** band (0-3/20). The 2026 station set gave the same 1/20. Swap p-values are consistent with uniform (KS p = 0.57), and standardised statistics are centred near zero (mean z = 0.14, SD 1.06). All five same-year anchors reached the p floor (z 5.5-6.9).

**What it adds.** First evidence from real data that the whole-period reference is not visibly inflated by the seasonal co-variation present in this network. A 1/20 outcome would be unlikely if the true rate were as large as E12's constructed case (P = 0.03), but plausible up to about 15% (P = 0.18). **It does not establish calibration**, and it says nothing about transport.

## 2. Comparison with existing analyses
| Analysis | Data | What it answers | Relation to E14 |
|---|---|---|---|
| E12 N0-N3 nulls | synthetic methane and Markov winds | generic nulls near 5% | **Corroborated** with real data |
| E12 N2b | synthetic, constructed seasonal confounder | the test *can* be inflated (23.8%) | **Not contradicted**; E14 finds no evidence that the real data contain confounding of that size (P = 0.03 for 1/20 at 23.8%) |
| E12 N1b | synthetic advected shared driver | the test cannot identify transport | **Unchanged**; E14 does not address physical specificity |
| E13 | 2026 data, season-restricted references | the 2026 statistic is extreme under alternative references | **Extended**; whole-period and within-season references agree on real-data nulls (18-19 of 20 identical decisions) |
| Synthetic scenarios A-D (as proposed) | synthetic | would re-tune E12 ingredients | **Not built**; this would duplicate E12 and add researcher degrees of freedom (EXPERIMENT_PLAN.md, section 1) |

## 3. Null definitions
- **(a) Zero inter-station transport:** a physical hypothesis; not testable here.
- **(b) No H2 directional contrast:** the absence of hour-level wind-conditioned lead-order asymmetry.
- **(c) Exchangeability of shifted-wind alignments:** the assumption the reference relies on.

Year-swapping makes (b) hold by construction, because methane and wind come from different years. A rejection would therefore be a Type-I error with respect to (b), caused by a failure of (c) under real seasonal co-variation. It is not a physical-specificity result. The only remaining link between the two series is calendar position (season, day of year and hour), which is exactly the channel through which seasonal confounding acts.

## 4. Realism: what the null preserves (development data; `results/seasonal_recurrence.json`)
- **Preserved exactly (observed data):** methane levels, seasonality, persistence, diurnal cycle, cross-station common drivers, station heterogeneity and missingness (year Y); wind direction, speed, persistence, diurnal cycle and seasonal climatology (year Y').
- **Seasonal structure recurs across years, so swaps carry real seasonal co-variation:**
  - Methane residual-difference variability is about twice as large in winter as in summer (network mean SD 0.176 ppm in January vs 0.084 ppm in June); its monthly cycle correlates between years at r = 0.58.
  - The monthly aligned-wind fraction varies seasonally (0.18-0.25) and recurs at r = 0.49 (network) and 0.54 (pair x month).
- **Not preserved:** any hour-level coupling. Interannual differences in timing and operations are carried along realistically but are not separately controlled.
- **Not separately manipulated:** seasonality, persistence, common-driver strength and missingness cannot be isolated in an empirical null. E14 measures their combined real-world effect, not individual contributions.

## 5. Design accounting
- **Replicates:** 50 = (20 swaps + 5 anchors) x 2 station sets. Completed 50/50; failures 0; non-evaluable 0.
- **Pair counts:** 27 pairs in every replicate (frozen rule; no station fell below 50%) and 21 for the 2026 station set. K = 246 everywhere.
- **Determinism:** no random numbers, so no seed schedule is needed; a test confirms identical reruns. Runtime 44 s.
- **Environment:** Python 3.12, NumPy and pandas as recorded in `results/run_log.json`.
- **Parity gate:** same-year 2025 reproduces the frozen dry run D = 0.18411446516401547 (27 pairs, K = 246, p = 1/247) to 5.6e-17.
- **Why n = 20:** it is the complete set of distinct ordered year combinations available in development data. The resolution limit was stated before running.

## 6. Results (`results/summary.csv`, `results/replicates.csv`, `results/secondary_stats.json`)
| Station set | Reference | Rejected / 20 | Rate (Wilson 95% CI) | Mean p |
|---|---|---|---|---|
| Frozen rule (12 stations, 27 pairs) | **Whole-period (frozen)** | **1** | **5.0% (0.9-23.6%)** | 0.45 |
| | Within calendar quarters (exploratory) | 2 | 10.0% (2.8-30.1%) | 0.46 |
| | Within Jan-Apr / May-Sep (exploratory) | 0 | 0.0% (0.0-16.1%) | 0.46 |
| 2026 station set (11 stations, 21 pairs) | Whole-period (frozen) | 1 | 5.0% (0.9-23.6%) | 0.43 |
| | Within calendar quarters | 1 | 5.0% (0.9-23.6%) | 0.43 |
| | Within Jan-Apr / May-Sep | 1 | 5.0% (0.9-23.6%) | 0.44 |

**Further detail (frozen rule):**
- **Rejected replicate:** methane 2025 with wind 2023 (z = 2.06, p = 0.024). No methane or wind year recurs among rejections.
- **Paired whole-period vs quarters:** both reject 1, whole-period only 0, quarters only 1, neither 18. Whole-period vs Jan-Apr/May-Sep: both 0, whole-period only 1, other only 0, neither 19.
- **Magnitudes:** swap pooled D ranged from -0.063 to 0.068; the same-year anchors from 0.082 to 0.184, all at the p floor; the registered 2026 statistic is 0.288 (z = 6.99, cited). The largest null value lies below every anchor.
- **Uniformity:** p-values KS D = 0.17 (p = 0.57); Wilcoxon test for z > 0, p = 0.165. Both are descriptive, because replicates share years.

**Figure:** `figures/e14_yearswap_null.{pdf,svg,png}`. (a) Standardised statistics of the year-swapped nulls vs same-year anchors, with the 2026 value as a reference line. (b) Empirical CDF of the swap p-values against uniform. (c) The recurring seasonal cycle of methane residual variability, which shows that swaps carry real seasonal structure.

## 7. Interpretation
- **Establishes:** in real WBEA development data, combining methane and wind with matching calendar timing but no hour-level coupling did not produce excess rejections under the frozen reference (1/20). The same-year statistics were clearly separated from every swap statistic: pooled D 0.082-0.184 vs at most 0.068, and z 5.5-6.9 vs at most 2.1.
- **Does not establish:**
  - that the reference is calibrated (rates up to about 24% remain compatible);
  - anything about 2026 specifically: the confirmation data were not used, and 2026 seasonality may differ;
  - which component (seasonality, persistence, common drivers, missingness) matters;
  - physical transport. E12's falsification result, that the test cannot separate methane transport from a wind-advected shared signal, is untouched.
- **About the anchors:** the same-year results (significant in every development year) are development data. They are not independent confirmation and are reported only as positive references.

## 8. Limitations and threats to validity
1. **Resolution:** with n = 20, inflation of 10-15% cannot be distinguished from nominal.
2. **Shared years:** each year appears in 8 of the 20 swaps, so the Wilson interval is nominal.
3. **Seasonal recurrence is moderate** (r of about 0.5-0.6). Year-specific seasonal timing is not carried by swaps; if confounding in the real data depends on exact intra-annual timing, swaps understate it.
4. **Interannual operational differences** (missingness patterns) are mixed into each swap.
5. **Development data only.** The 2026 period may differ.
6. **Physical specificity:** no bearing on transport identifiability (see E12 N1b).

## 9. Recommendation
**Supplementary Material, with one sentence in Results section 4.4.** E14 adds genuinely new information: the first real-data check of the seasonal-confounding vulnerability that E12 exposed. It narrows that concern ("not evident at the magnitude of the constructed case") without resolving calibration. It does not change any registered result or conclusion, so a main-text figure is not justified. Its value is in bounding a limitation, not in strengthening the 2026 finding. It **modestly improves** the paper's treatment of the calibration limitation; it does not remove that limitation.

## 10. Artifact manifest
See `MANIFEST.md` (paths, SHA-256, tests, commits).
