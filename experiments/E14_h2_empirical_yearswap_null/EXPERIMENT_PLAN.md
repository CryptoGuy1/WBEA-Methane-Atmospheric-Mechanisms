# E14 (Experiment B): Empirical year-swapped null for the frozen H2 shifted-wind test
**Status:** POST-CONFIRMATION EXPLORATORY. Plan committed before any swap replicate is computed.
**Data:** development data only (2021-01-01 01:00 to 2025-12-02 00:00). No sealed or 2026 methane data are read; the registered 2026 values are cited from `e08_results.json` for comparison only.
**Frozen items:** E08 code, outputs and decisions; E12 and E13 results; manuscript files. Nothing is modified. The frozen H2 statistic is reused via `src/wbea/h2.py`, `src/wbea/e08.py` and the parity-tested E12 fast routines, through the E13 helpers `pair_data`, `D_whole`, `D_blocks` and `summarise` (imported read-only).

## 1. Audit result: what exists, what this adds
- **E12** (synthetic): every scenario uses synthetic methane and synthetic Markov-chain winds. Four generic nulls are near 5%. One *constructed* seasonal-confounding mechanism (N2b) inflates rejection to 23.8%; within-season and truncated alternatives reduce it.
- **E13** (2026 data): the observed 2026 statistic remains extreme under season-restricted references.
- **Not yet tested:** whether seasonal co-variation that actually exists in WBEA data (real winds, real methane, real missingness) inflates the whole-period shifted-wind test. E12 shows it *can* in a constructed case; nothing shows whether it *does* at a damaging magnitude in this network.
- **Why not synthetic scenarios A-D:** they would re-combine E12's ingredients (seasonal drift, persistence, common driver, missingness) with newly tuned parameters. That adds researcher degrees of freedom without a realism guarantee. An empirical null avoids parameter tuning entirely.

## 2. Design
For development years Y (methane) and Y' (wind), Y != Y', take Jan 1 01:00 to Oct 1 00:00 of each year (273 days, 6,552 hours). The 2024 window drops 29 February so both series align on calendar date and hour. Pair the full methane panel of year Y with the full composite-wind panels of year Y', and run the complete frozen H2 procedure:
- station coverage rule (>= 50% valid CH4 in the window, applied to methane year Y);
- 2021-2023 reference medians;
- leave-pair-out residuals and first differences;
- 30-km pairs and the >= 100 aligned/reversed eligibility rule;
- transit weights;
- all 246 whole-day joint wind shifts (k = 14..259);
- inverse-null-variance pooling;
- finite-shift p.

**Replicates:** all 20 ordered (Y, Y') combinations with Y != Y'. This is an exhaustive enumeration of the design, not a sample, so the count cannot be increased without changing the design.

**Same-year anchors (not nulls):** the 5 combinations Y = Y' retain real hour-level wind-methane coupling. They serve as positive references, and Y = Y' = 2025 is the parity check.

**Primary station set:** the frozen coverage rule applied to each methane-year window. **Secondary:** the 2026 confirmation network (AMS 2 removed; 11 stations).

## 3. Null definitions
- **(a) Zero inter-station methane transport:** not tested here; it is a physical hypothesis.
- **(b) No H2 directional contrast:** the absence of hour-level wind-conditioned lead-order asymmetry.
- **(c) Exchangeability of shifted-wind alignments:** the assumption the reference relies on.

In a year-swap, methane and wind come from different years, so there is **no hour-level wind-methane coupling of any kind, and in particular no inter-station transport aligned with the paired wind**. Null (b) holds at the hourly scale. What remains is the *calendar-level* association between methane's seasonal structure (year Y) and the wind climatology (year Y'). A rejection therefore indicates that the whole-period shifted reference treats real seasonal co-variation as directional signal. This is a failure of (c) caused by seasonal confounding, and it is a legitimate Type-I error with respect to null (b). It is not evidence about physical transport.

**Data-generating structure.** Meteorology (year Y') determines the aligned/reversed masks and transit weights. Methane (year Y) has its own regional common drivers, station residuals, seasonal cycle, diurnal cycle and missingness. The only link between the two is the shared calendar position (season, day of year, hour). The shifted reference breaks that link for every surrogate except k = 0.

## 4. Pre-specified analysis and decision rule (alpha = 0.05)
- **Primary:** the number of the 20 swap replicates rejected by the whole-period reference (p <= 0.05; finite p floor 1/247), reported with a Wilson 95% interval and per-year counts. The replicates share years, so they are not fully independent; the Wilson interval is reported as nominal.
- **Rule** (binomial tail at 5%, n = 20: P(X >= 3) = 0.076, P(X >= 4) = 0.016):
  - **>= 4/20 rejected:** evidence that real seasonal co-variation inflates the whole-period test.
  - **0-3/20 rejected:** no evidence of inflation at the resolution of this design. This does *not* establish calibration.
- **Secondary (descriptive):**
  - p-value distribution and z = (D - null mean)/null SD for each replicate;
  - swap pooled D relative to the same-year anchors and to the registered 2026 statistic (cited);
  - paired comparison of whole-period vs the E13 within-season references (calendar quarters C1; Jan-Apr/May-Sep C2) on the same replicates (2 x 2 rejection table, no independence assumption);
  - secondary station set.
- **Parity gate (before any swap):** the Y = Y' = 2025 run must reproduce the frozen dry-run pooled D = 0.18411446516401547 (27 pairs, K = 246) to within 1e-10. Otherwise stop.

## 5. Limitations known in advance
- **Resolution:** with n = 20, a true rate below about 15% cannot be distinguished from 5% with confidence.
- **Interannual differences:** swaps also mix interannual differences in network operations (missingness patterns), which is realistic but not separately controlled.
- **No transport claims:** no statement about transport, emission rates or universal calibration follows from this experiment.

---
## Addendum (2026-11-15, after independent review; the pre-registered text above is unchanged)
This addendum corrects interpretation only. No threshold, design element or computation changed, and all numerical outputs are byte-identical.
1. **Section 3 overstated the null.** Year-swapping removes the *synchronous same-year alignment* of wind and methane. It does **not** guarantee a zero expected H2 directional contrast: calendar-recurrent seasonal and diurnal structure in both series survives the swap and can create dependence between the combined series. The design is therefore an **empirical cross-year negative control**, not a strict statistical null. Its rejection rate is **not** a verified Type-I error rate.
2. **Section 4 (decision rule).** The four-rejection threshold and its binomial tail probabilities assumed independent replicates. The 20 combinations reuse five methane years and five wind years (each year enters 8 combinations), so the threshold is retained only as a pre-declared *descriptive* benchmark, and the Wilson interval is nominal.
3. **Terminology.** "Same-year anchors" retain the observed alignment of wind and methane. They are not evidence of physical coupling or transport.
The corrected interpretation is in `REPORT.md` (v2); the original report is preserved as `REPORT_v1_superseded.md`.
