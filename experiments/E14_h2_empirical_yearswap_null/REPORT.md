# E14 (Experiment B): Empirical cross-year negative control for the frozen H2 test. Corrected report (v2)
**Status:** POST-CONFIRMATION EXPLORATORY. Development data only. This version corrects the *interpretation* in `REPORT_v1_superseded.md` after independent review. No design element, threshold or computation changed, and every numerical output is byte-identical to the original run (checksums in `MANIFEST.md`). No frozen E08, E12 or E13 code or result and no manuscript file was modified.
**Commits:** plan `05440d4` -> implementation `666e7e8` -> original results `cf84a8b` -> this correction (see `MANIFEST.md`).

## 1. Corrected scientific question
When observed development-period methane from one year is combined with observed winds from a *different* year, aligned by calendar date and hour, how often does the frozen whole-period shifted-wind test reject?

This is an **empirical cross-year negative control**. It removes the synchronous same-year alignment of the two records but retains calendar-recurrent seasonal and diurnal structure. It asks whether that retained structure, together with real persistence, common variation and missingness, *frequently* produces rejections. It is not a strict statistical null, and its rejection rate is not a verified Type-I error rate.

## 2. What the swap retains and removes
**Four distinct notions:**
- **(a) Removal of synchronous same-year alignment:** achieved by construction.
- **(b) Zero expected H2 directional contrast:** **not** guaranteed. Wind climatology (seasonal and diurnal direction and speed regimes) recurs between years, and so does methane's seasonal and diurnal structure (in development data, the monthly cycle of residual-change variability correlates between years at r = 0.58; the monthly aligned-wind fraction at r of about 0.5). If methane's lead-order structure varies with season or hour of day in a way correlated with the recurring wind climatology, a cross-year combination can carry a non-zero expected contrast. No mathematical argument shows this expectation is zero.
- **(c) Absence of physical methane transport:** not addressed. Even same-year combinations do not establish transport (see E12 falsification).
- **(d) Exchangeability of shifted reference alignments:** the assumption under scrutiny. The shifted reference breaks calendar alignment for every surrogate except the observed one; a swap keeps calendar alignment. A swap therefore probes whether calendar-recurrent dependence *alone* makes the observed alignment look extreme relative to calendar-misaligned shifts.

**Retained (observed data):**
- methane levels, seasonality, diurnal cycle, persistence, cross-station common variation, station heterogeneity and missingness (year Y);
- wind direction, speed, persistence, diurnal cycle and seasonal climatology (year Y');
- calendar-recurrent dependence between the two.

**Removed:** day-to-day synchronisation, including the response of methane to the actual weather of its own year.

**Not controlled, carried into each combination:**
- shared long-term influences (trends, network or analyser changes such as the September 2024 analyser replacements at AMS 5 and AMS 23);
- year-specific weather events in either record;
- differences in measurement completeness between years.

**Not statistically independent:** the methane and wind records are not independent simply because they come from different years.

## 3. Observed findings (unchanged numerical results)
**Frozen station rule** (12 stations, 27 pairs, K = 246 in every combination; `results/summary.csv`):

| Reference | Rejections at p <= 0.05 | Proportion (nominal Wilson 95% CI) |
|---|---|---|
| **Whole-period shifts (frozen reference)** | **1 / 20** | 5.0% (0.9-23.6%) |
| Within calendar quarters (exploratory) | 2 / 20 | 10.0% (2.8-30.1%) |
| Within Jan-Apr / May-Sep (exploratory) | 0 / 20 | 0.0% (0.0-16.1%) |

**2026 station set** (AMS 2 removed; 11 stations, 21 pairs): 1/20 under each of the three references.

**Descriptive detail (frozen rule):**
- **Rejected combination:** methane 2025 with wind 2023 (z = 2.06, p = 0.024).
- **Cross-year pooled statistics:** D from -0.063 to 0.068; z from -2.50 to 2.06 (mean 0.14, SD 1.06); mean p 0.45.
- **Same-year combinations (observed alignment, development data):** D from 0.082 to 0.184; z from 5.5 to 6.9; all at the p floor (1/247). The registered 2026 statistic (D = 0.288, z = 6.99) is cited for reference only.
- **Paired decisions:** whole-period vs quarters: both reject 1, whole-period only 0, quarters only 1, neither 18. Whole-period vs Jan-Apr/May-Sep: both 0, whole-period only 1, other only 0, neither 19.

**Dependence and inferential status.** The 20 ordered combinations reuse five methane years and five wind years; each year enters 8 combinations. The proportions are therefore **descriptive**. Specifically:
- the **Wilson intervals are nominal**;
- the **binomial comparisons** in v1 (e.g. P(<= 1 rejection) = 0.03 at a 23.8% rate) assume independence and are **withdrawn as inferential statements**;
- the **Kolmogorov-Smirnov** (p = 0.57) and **Wilcoxon** (p = 0.165) results are **descriptive summaries, not tests**;
- the **pre-declared four-rejection threshold** is retained as a descriptive benchmark (1/20 is below it). Its error rates were derived under independence and do not apply.

A p-value distribution close to the diagonal does not establish valid calibration.

## 4. What E14 establishes
- In five development years of WBEA data, calendar-aligned cross-year combinations of observed methane and wind **did not frequently produce rejections** under the frozen whole-period reference (1/20). Their standardised statistics were small, and in every case below those of the same-year (observed-alignment) combinations.
- The exploratory season-restricted references behaved similarly on these combinations (2/20 and 0/20 for the frozen network; 1/20 each for the 2026 station set). Their decisions agreed with the whole-period reference in 18-19 of 20 paired comparisons.

## 5. What E14 does not establish
- Calibration of the shifted-wind reference, or a Type-I error rate, in development data or in general.
- Calibration for the 2026 confirmation data: none were used, and 2026 seasonality and completeness may differ.
- That the expected H2 contrast is zero for cross-year combinations.
- Which component (seasonality, persistence, common variation, missingness) matters; none is manipulated separately.
- Anything about physical methane transport or emission rates.
- That E12's constructed seasonal-confounding mechanism is absent from the real data in general. It establishes only that it was not *evident* as frequent rejections in these 20 combinations.

## 6. Relationship to E12 and E13
- **E12 (synthetic).**
  - Its constructed seasonal-confounding scenario (23.8% rejection) **remains a valid demonstration** that the whole-period reference can be inflated under its own assumptions. **E14 does not refute E12.** E14 shows that comparable inflation was not apparent in these cross-year combinations of observed data, which have different and unquantified confounding strength.
  - E14 corroborates, descriptively and with real data, E12's finding of near-nominal behaviour under its generic nulls.
  - E12's falsification result (the test cannot distinguish methane transfer from a wind-advected shared signal) is untouched.
- **E13 (2026 data).** E13 showed the observed 2026 statistic remains extreme under season-restricted references. E14 shows those references behave similarly to the whole-period reference on cross-year development combinations. Neither E13's nor E14's alternative references are **replacement confirmatory tests**, because they:
  1. were not pre-registered for the 2026 confirmation;
  2. have coarser p-value floors (1/64 for quarters, 1/94 for Jan-Apr/May-Sep);
  3. rest on their own within-block exchangeability assumptions and wrap-around boundary effects.

  The registered H2 decision rests solely on the frozen whole-period test.

## 7. Remaining limitations
1. **Dependence:** five years supply all 20 combinations, so no proportion has a valid sampling-based interval.
2. **Resolution:** even ignoring dependence, 20 combinations cannot distinguish rejection proportions of 10-20% from 5%.
3. **Partial recurrence:** calendar recurrence is only partial (r of about 0.5-0.6). Year-specific timing is not carried by swaps; if real confounding depends on exact intra-annual timing, cross-year combinations understate it.
4. **Uncontrolled differences:** inter-year differences in completeness, instruments and events are mixed into each combination.
5. **Development data only:** five years, one network.
6. **Physical specificity:** no bearing on whether directional dependence reflects transport.

## 8. Recommendation
**Include in the Supplementary Material as an empirical cross-year negative control, with a one- or two-sentence mention in Results section 4.4.**

The mention should convey only that:
- observed methane and wind from different development years, aligned by calendar date, rarely produced rejections under the frozen reference;
- this is a descriptive negative control based on dependent combinations, not a calibration or Type-I error estimate.

E14 adds real-data context to the calibration limitation identified by E12 but does not remove it, and it changes no registered result.

## 9. Changes from v1 (transparency)
- **Null claim:** "(b) holds by construction" and "a legitimate Type-I error" are withdrawn, and the design is reframed as a cross-year negative control.
- **Inferential statistics:** binomial comparisons withdrawn as inferential statements; Wilson intervals labelled nominal; KS and Wilcoxon results labelled descriptive; the four-rejection threshold retained as a descriptive benchmark.
- **Terminology:** "real coupling" replaced by "observed alignment"; "null" replaced by "negative control" in the figure.
- **E12 relationship:** stated explicitly that E14 does not refute E12 and does not demonstrate 2026 calibration.
- **Figure:** two panel (a) tick labels changed. Data and encodings are unchanged; the figure files were regenerated.
- **Repository gap fixed:** `figures/e14_yearswap_null.pdf` was previously excluded by `.gitignore` and is now committed.
