# E13: Post-confirmation seasonal-shift sensitivity of the 2026 H2 result. PRE-REGISTERED PLAN

**Status: POST-CONFIRMATION EXPLORATORY sensitivity analysis.** Not a confirmation, not a new hypothesis test. The registered E08 decision (H2 confirmed; pooled D = 0.287931708, p = 1/247) is unchanged whatever E13 finds. Branch `research/e13-h2-seasonal-shift-sensitivity`, created from the E12 branch head 0ebdff7. E08 code, results, protocol, decisions and tags are not modified, nor are E12 results or plan (enforced by tests). Committed BEFORE any seasonally restricted statistic is computed on 2026 data.

**2026 information already known when this plan was written:** the frozen E08 outputs (pooled D, p, per-pair D and null SDs in `h2_pairs.csv`, lag centroids, whole-period null means by offset tercile). No seasonally restricted 2026 statistic has been computed or seen.

## 1. Motivation
E12 (N2b) showed that the whole-period circular wind shift can be anti-conservative, rejecting 23.8% at alpha 0.05, when a lead-lag structure not tied to the hourly wind co-varies seasonally with wind regimes. A within-season shift reduced this to 5.2% (3.6-7.5%) in that scenario. E13 asks whether the 2026 statistic remains extreme when the shifted-wind reference keeps wind within comparable seasons.

## 2. Data and frozen inputs (identical to E08)
- `sealed/e08_panel/*.parquet` (2026-01-01 01:00 to 2026-10-01 00:00 MST hour-ending, 6,552 h); checksums re-verified against `sealed/e08_panel/SHA256SUMS.txt`.
- Frozen 2021-2023 reference medians; station-coverage exclusion (< 50% valid CH4: AMS 2, as in E08); composite station wind (D-03); 27-pair rule (<= 30 km) on the remaining stations (21 pairs).
- Pair drop rule (< 100 eligible hours either direction); H2 functions from `src/wbea/h2.py` and `src/wbea/e08.py` at `protocol-freeze`.

## 3. Seasonal partitions (fixed here; not chosen by p-value)
| Partition | Blocks (hour-ending MST) | Rationale | Admissible joint shift k (days) | Surrogates | p floor |
|---|---|---|---|---|---|
| **C1 (primary exploratory)**: calendar quarters | Jan-Mar (90 d, hours 1-2,160), Apr-Jun (91 d), Jul-Sep (92 d) | Identical to the E12 within-season procedure calibrated in N0-N3 and N2b | 14-76 | 63 | 1/64 = 0.0156 |
| **C2 (alternative grouping)**: cold vs warm half | Jan-Apr (120 d) and May-Sep (153 d) | Snow-cover / frozen-ground period vs growing season in northern Alberta | 14-106 | 93 | 1/94 = 0.0106 |
| Monthly blocks (considered, not run) | 28-31 d | - | 14-14 at most | <= 4 | not usable; documented only |

**Shift construction.** "Joint within-season circular shift": for shift k, the wind series in EACH block is rotated by k whole days *within that block* (wrapping from the block's end to its start); methane is not shifted. The same k is used in all blocks so each surrogate is one coherent dataset. This is not interchangeable with (a) independent shifts per block or (b) separate per-season statistics; (b) is run as configuration C4 below, (a) is not run.

## 4. Statistics (all exploratory except the frozen reference)
For each configuration, observed per-pair D_ij are the frozen values (k = 0 gives the unshifted masks). Transit-time weights w_l are unchanged: rotating within blocks permutes hours within each block, so the multiset of (mask, tau) values and the frozen weights are shift-invariant.
- **R0 Frozen reference (reproduction):** whole-period shifts (K = 246), frozen pooling weights. Must reproduce D = 0.287931708 and p = 1/247 exactly (check).
- **C1-w (primary exploratory):** C1 null; pooling weights 1/Var over the C1 surrogates (as in E12). Pooled observed D differs from 0.2879 because the weights differ.
- **C1-f (decomposition):** C1 null with the frozen E08 pooling weights, so the observed pooled D equals 0.2879; isolates the effect of the reference distribution from the effect of weighting.
- **C2-w and C2-f:** as C1 with partition C2.
- **C4 per-season statistics (descriptive):** each C1 quarter analysed separately: pair eligibility (>= 100 eligible hours per direction within the quarter), weights and LPO residuals computed within the quarter, with a within-quarter circular shift null (k = 14 to L - 14 days). Pooled D and p per quarter; pairs failing eligibility dropped; a quarter is "not evaluable" if fewer than 10 pairs remain. No combined p-value.

**p-values:** p = (1 + #{surrogates >= observed}) / (K + 1), one-sided, as frozen.
**Reported for each configuration:** observed pooled D; K; p; surrogate mean, SD, 5/50/95/99% quantiles and maximum; standardised position z = (observed - mean) / SD (descriptive only); number of pairs.

## 5. Interpretation rules (fixed before results)
Per configuration:
- **"remains unusual"** if p <= 0.05 (C1 floor 0.0156; C2 floor 0.0106);
- **"not unusual"** if p > 0.10;
- **"borderline"** otherwise.

Overall E13 statement:
- **strengthens** the H2 interpretation if C1-w and C2-w both "remain unusual";
- **materially challenges** it if C1-w is "not unusual";
- **qualifies** it in all other combinations.

C1-f and C2-f decide nothing; they decompose the result. C4 is descriptive.

## 6. Validity caveats (stated in advance)
Within-season shifts assume exchangeability *within* each block. Seasonal transitions inside a block (for example March thaw) and wrap-around at block edges are not removed. E12 established approximate calibration of this procedure only in its synthetic scenarios (N0 6.2%, N1a 6.6%, N2a 4.2%, N3 4.6%, N2b 5.2%); four of these were classified "inconclusive" or "calibrated" under its margin, so it is not a validated exact test. The p floor (1/64) limits resolution.

## 7. Tests
- Surrogate construction: within-block roll equals a manual roll, including wraparound.
- Block boundaries: lengths 2,160 / 2,184 / 2,208 h (C1) and 2,880 / 3,672 h (C2) summing to 6,552, with calendar dates checked.
- Shift invariance of the weights.
- Reproduction of the frozen per-pair D (`h2_pairs.csv`) and of the frozen pooled D and p from the 2026 data.
- Determinism.
- Non-modification of E08 and E12 files.

## 8. Outputs
`results/e13_summary.csv`, `results/e13_surrogates_*.csv`, `results/e13_per_season.csv`, `results/e13_results.json`; figures comparing the reference distributions; `E13_REPORT_FOR_MANUSCRIPT_AI.md`; `E13_MANUSCRIPT_HANDOFF.md`; `DEVIATIONS.md`.

---
## Terminology addendum (added at closure, 2026-11-11; the pre-registered text above is unchanged)
Partition C2 (January-April / May-September) is an **alternative calendar-based seasonal block** scheme. Its boundaries were predefined here and were **not derived from observed meteorological transitions**. The "cold vs warm half" label and the snow-cover/growing-season rationale above are motivating descriptions, not established meteorological seasons. The figure `e13_fig1_reference_distributions` (not regenerated at closure) labels this partition "cold/warm halves (C2)"; read it as these calendar-based blocks.
