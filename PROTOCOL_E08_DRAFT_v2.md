# E08 Independent confirmation protocol, DRAFT v2 (2026-11-10)

**Status: draft for final authorisation. Not frozen. No 2026 methane value opened.** v1 (`PROTOCOL_E08_DRAFT.md`) is preserved. This version answers review points 1-8. It becomes binding only when committed unchanged and tagged `protocol-freeze` after researcher authorisation.

## 1. Data and window
- **Window (all confirmatory tests):** 2026-01-01 01:00 to 2026-10-01 00:00 MST hour-ending (273 days, 6,552 hours). Final under WBEA's 30-day validation rule at the 2026-11-09 export (D-53, D-54). Timestamp convention officially documented as hour-ending MST (D-66).
- **Stations:** 12 usable (D-05). H1 core response: AMS 1, 2, 6, 7, 11, 13, 23. Stability: AMS 5 T90 - T20. H2: frozen 27-pair family. H3: all 12 stations.
- **Source files (SHA-256 at acquisition; re-verified before splitting; any mismatch stops E08):**

| Station | SHA-256 |
|---|---|
| AMS 1 | c2463a861529f015fff76a2d6d5ce43613d7893ca05c662eb9f423ed35d7b1df |
| AMS 2 | 6f8f3c36e0ebeea62fd9091adaf00c22d782941dfe13a709e6034a95af77cc62 |
| AMS 5 | e5a24f75e3663e6281b8941a6d4aa1cb114ff8adfcf364a59dd31d97ce1803e5 |
| AMS 6 | 3ebabe3f4055667ff2a8dda9e26e69e42acfe083e9e6718ecfb7420a21e5094c |
| AMS 7 | 7e1e140e1a575961e930905f1db12bd5e4e1281d81015035b9acee4ae23ce0e2 |
| AMS 9 | c3b2b0075fedba01d9879f835a759f1086ec7eeac5ae22e8b5da7247c087c6e5 |
| AMS 11 | a2fcbac9631b9291a161e413e32c4a2cc7c34c75b44ad085b6d9003a159a2831 |
| AMS 13 | 3852b6d2d0780b530ec90dbd141b9707c3b6c78f4da25218e4b999113b7e80df |
| AMS 14 | 73a9986b71e25ea8a02ef7675ec6a9177e4c8b523a6000e5dd3e8adb2af391f1 |
| AMS 18 | 1c81200dc6a4a89f77c5c9003002a37536877ca8b8a2fa7fc45e8eb323594254 |
| AMS 23 | 25c7f10ff8b3fbd7926b2479ec9bf45466a5bdaaaac74cc9fe23e5d1835fb00f |
| AMS 30 | eabd0557c7e0902661f68d112f3b1ac308fdfc86feacb5b29386534adffd4af4 |

Archive hashes: `manifests/archives_sha256.csv`. Z, C and `.` hours are missing (D-66).

## 2. Frozen reference quantities (2021-2023; never re-estimated on 2026)
Station CH4 medians and P95 thresholds; S mean and SD; stability tercile cuts (-0.6, 0.0 degC, ties upward, D-17); wind classes (<1, 1-2.5, >=2.5 m/s); composite-wind rule (D-03); E05 eligibility rules; R3 episode rule (D-18); solar day/night. Stored in `config/project.toml` and E03/E07 result files; hashed at freeze.

## 3. Confirmatory decision rules
### H1: wind-adjusted association between stability and the network CH4 level
- **Primary model:** core-network median anomaly on standardised S(t) and log(U5 + 0.5), year x month x hour cells (D-21, D-22).
- **Inference:** 14-day non-overlapping blocks, 2,000 replicates, percentile 95% CI. CR1 and basic intervals reported as secondary.
- **Negative-control model:** the same model with S(t), S(t+24) and log wind. Let b1 and b_nc be the coefficients on S(t) and S(t+24), estimated in the same bootstrap replicates.
- **H1 confirmed if all hold:** (a) primary CI lies entirely above 0. (b) It is not the case that both the 95% CI of b_nc excludes 0 and |b_nc| >= 0.5 x b1, using point estimates from the negative-control model. The ratio b_nc/b1 is reported with its bootstrap CI.
- **Interpretation:** passing (b) means no evidence of next-day confounding at the stated sensitivity. A CI of b_nc containing 0 is **not** evidence that confounding is absent. H1 is reported as an association, not a causal effect.

### H2: wind-dependent directional coupling compatible with transport
- **Statistic:** pooled D as in E05 (D-26). Weights are 1/variance of each pair's D over the K finite shifts.
- **Null:** all K = 246 admissible whole-day circular shifts of the wind series (14 to 259 days); p = (1 + #{pooled D_k >= observed}) / (K + 1); minimum p = 1/247 = 0.0040 (D-48).
- **Criterion (i):** p < 0.05.
- **Criterion (ii):** pooled D > 0 with wind shifted +1 h and -1 h relative to CH4.
- **Criterion (iii), ordered lag-centroid trend allowing limited inversions** (D-46; reconciled here; preserves the development intention of an increasing centroid without requiring strict monotonicity):
  - Transit bins: 0-0.5, 0.5-1, 1-1.5, 1.5-2, 2-3 h. A bin is estimable if it holds >= 500 aligned pair-hours and its positive-part lag profile sums to more than 0.
  - Centroid c_b = sum over l = 0..3 of l x max(r_bl, 0) / sum of max(r_bl, 0).
  - **Met if:** at least 4 bins are estimable, including the first; AND Spearman rho (bin midpoint vs c_b, average ranks for ties) >= 0.9 with 5 bins or >= 0.8 with 4 bins (each allows at most one adjacent inversion); AND c_last - c_first > 0 with a 14-day block-bootstrap 95% CI excluding 0 (1,000 replicates).
  - Tied centroids count as non-increasing. Fewer than 4 estimable bins makes the criterion not evaluable.
  - Development values: c = 0.25, 0.39, 0.73, 1.11, 1.51 h (rho = 1.0).
- **H2 confirmed if** (i), (ii) and (iii) all hold.
- **Interpretation:** wind-dependent directional coupling compatible with transport. No transport pathway, source identity or emission rate is observed.

#### Exchangeability of the wind-shift null (review point 4)
- **Assumption.** Under no wind-dependent coupling, the joint distribution of residual CH4 changes and the wind series is invariant to circular whole-day shifts of wind. Whole-day shifts preserve the diurnal phase, the CH4 series and its missingness exactly.
- **Limitation.** The 273-day window spans winter to early autumn. A shift pairs wind from one season with CH4 from another, and the wrap joins September to January. If seasonal wind-direction regimes co-vary with seasonal residual asymmetries unrelated to coupling, the null could be miscalibrated.
- **Development verification** (2025 Jan-Sep; `experiments/PRE_E08/verify_h2_null_jan_sep.py`):
  - K = 246.
  - Null pooled D is unrelated to seasonal offset: Spearman -0.016, p = 0.80. Tercile means -0.003, -0.018 and +0.003, each with SD about 0.03.
  - Eligible-hour totals are identical under shifts (preserved by construction).
  - The procedure runs on a dev window: pooled D 0.184, p = 0.004.
- **Reported in E08:** the null distribution by offset tercile, and the 40-background false-detection calibration (3.9%, E06) cited as supporting evidence.

### H3: meteorology-mix share
- **Estimand:** pooled projection share s = sum(c_k t_k) / sum(t_k^2) over contrasts k = 2026 vs each development year (2021-2025), Jan-Sep windows, 12 stations, so up to 60 contrasts (D-40, D-47, D-54).
- **Registered features unchanged:** regimes, 50 h merge rule (applied once on the full data per contrast, then fixed), and estimator.
- **Bootstrap:** 1,000 replicates.
  - In each replicate, the 2026 window's 14-day blocks are resampled once, and that **same 2026 resample is used for all 60 contrasts and all 12 stations jointly**.
  - Each development year's blocks are resampled within that year, jointly across stations (as in E07).
  - A replicate is non-estimable if any merged group in any contrast has zero hours in either year. The CI uses estimable replicates only, and the count is reported.
- **Confirmed if** the 95% CI excludes 0. Development benchmark (Jan-Sep): 0.026 (-0.028 to 0.124), not supported.

## 4. Descriptive outputs (no pass/fail; cannot alter H1-H3)
Per-pair D and max-T p; kernel comparison against both simulation references; H1 total association, ERA5 proxy and CR1; per-station H3 shares and 6-regime sensitivity; F5 regime distribution (D-50); X4 W0 vs ERA5 100 m centroids (D-62).

E10 typology shares are reported with the assessability split. **The typology is not supported. Episodes without an eligible upstream pair are "not assessable", not physically isolated** (D-63).

## 5. Contingencies (fixed before access)
| Rule | Threshold | Justification | Effect |
|---|---|---|---|
| Station excluded | < 50% valid CH4 in window | Development coverage is 90-94% per station (E02); below 50% indicates instrument failure, not normal operation | Station removed from all tests and listed; core Kmin stays 5 of the remaining core stations |
| H1 not evaluable | < 70% valid S hours, < 3,000 usable hours, or < 6 core stations | Development single-year fits used about 8,000 h with SE <= 0.0064. At 3,000 h the SE is about 0.010, so a CI half-width about 0.02 still resolves the development effect of 0.048. 70% S coverage keeps seasonal cells represented. | Reported "not evaluable", not failed |
| H2 pair dropped | < 100 eligible hours in either direction | A correlation from fewer than 100 hours has SE of about 0.1, comparable to typical pair D | Pair listed; pooled over the rest |
| H2 not evaluable | < 10 pairs remaining | Below 10 pairs, a few pairs dominate the pooled statistic | Reported "not evaluable" |
| H3 not evaluable | < 30 estimable contrasts, or > 10% non-estimable bootstrap replicates | Half of the planned contrasts; unstable intervals | Reported "not evaluable" |
| Reduced network | Any exclusion above | Estimands then refer to the reduced network | The development benchmark is recomputed on the same reduced network for a like-for-like descriptive comparison |
| Post-unblinding code error | Any | - | Fix, re-run once, report both runs and the diff; methods are never changed in response to results |

## 6. Seeds, environment, procedure
- **Seeds:** E08 base 20261190; H1 +1, H2 +2, H3 +3, descriptive +4.
- **Environment:** Python 3.12.3; `requirements.txt` pinned (numpy 2.5.4, pandas 3.0.6, scipy 1.18.1, scikit-learn 1.9.1, matplotlib 3.11.2, pyarrow 26.0.1, netCDF4 1.7.5.1.post1, openpyxl 3.1.5, pytest 9.2.0). Hash recorded at freeze.
- **Data splitting:**
  1. Re-verify all 12 source hashes.
  2. `src/build/build_e08_panel.py` streams each raw workbook and writes **only** rows with 2026-01-01 01:00 <= t <= 2026-10-01 00:00 to `sealed/e08_panel/*.parquet`, with raw tokens preserved.
  3. It writes nothing else and logs row counts and output SHA-256.
  4. The E08 analysis reads only these files plus the development panel (for Jan-Sep 2021-2025 H3 contrasts and frozen references).
- **Single run:** results committed unchanged, including failures; Figure 10 compares development and confirmation estimates.

## 7. Disclosures
Development-informed choices: D-18 (episode rule), D-21 (no same-day background), D-46 and this section (centroid criterion, reconciled after the failed E06 criterion), D-48 (finite shifts, replacing D-29), D-54 (Jan-Sep window). Prior 2026 exposure: AMS 2 valid-hour count (3,379); header rows; ERA5/FIRMS 2026 records loaded with their files (not methane outcomes). Full table in `SEALED_DATA_POLICY.md`.

## 8. Final freeze checklist
- [ ] Researcher authorises this protocol (v2) without further change
- [ ] Implement `src/build/build_e08_panel.py` and `experiments/E08_confirmation/run_e08.py` exactly as specified; unit-test them; **dry-run the full pipeline on the development window 2025-01-01 to 2025-10-01** with 2021-2023 references (no 2026 access); commit
- [ ] Record the code commit hash, `requirements.txt` SHA-256 and `config/project.toml` SHA-256 in this file; commit
- [ ] Tag `protocol-freeze`; push
- [ ] Re-verify the 12 source hashes; run the splitter; record output hashes
- [ ] Run E08 once; commit all outputs unchanged; push
