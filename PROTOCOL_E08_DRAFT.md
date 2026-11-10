# E08 Independent confirmation protocol: DRAFT for review (not frozen)

Status: draft, 2026-11-10. **Not authorised. No 2026 methane value has been opened.** Becomes binding only when committed unchanged under tag `protocol-freeze` after researcher approval.

## 1. Data
| Item | Specification |
|---|---|
| Confirmation window (primary, all hypotheses) | 2026-01-01 01:00 to 2026-10-01 00:00 MST hour-ending (273 days). Final under WBEA's 30-day validation rule at the 2026-11-09 export (D-53, D-54) |
| Sensitivity windows | (a) add 2025-12-02 to 2025-12-31 for H1/H2; (b) one re-run after WBEA's 2026 annual review (expected about March 2027) |
| Stations | 12 usable stations (D-05); H1 core response AMS 1, 2, 6, 7, 11, 13, 23 (Kmin 5); stability AMS 5 T90 - T20 |
| Source files (SHA-256 at acquisition) | AMS 1 c2463a86...b1df; AMS 2 6f8f3c36...cc62; AMS 5 e5a24f75...03e5; AMS 6 3ebabe3f...094c; AMS 7 7e1e140e...0e2; AMS 9 c3b2b007...c6e5; AMS 11 a2fcbac9...2831; AMS 13 3852b6d2...80df; AMS 14 73a9986b...91f1; AMS 18 1c81200d...4594; AMS 23 25c7f10f...b00f; AMS 30 eabd0557...f4af4. Full hashes: `manifests/station_exports_2021_2026_manifest.csv`. Hashes are re-verified before splitting; any mismatch stops E08 |
| ERA5, FIRMS | Used only for sensitivity and descriptive outputs; not needed for primary tests |

## 2. Frozen reference quantities (all from 2021-2023 development data; never re-estimated on 2026)
Station CH4 medians; station P95 thresholds; S mean and SD; stability tercile cut points (-0.6, 0.0 degC; ties upward, D-17); wind classes (<1, 1-2.5, >=2.5 m/s); composite-wind rule (D-03); hour-ending MST (D-02); 27-pair H2 family and E05 eligibility rules; R3 episode rule (D-18); solar day/night rule. Stored in `config/project.toml` and E03/E07 result files, hashed at freeze.

## 3. Confirmatory tests
| Hypothesis | Estimand | Inference | Confirmed if |
|---|---|---|---|
| **H1** wind-adjusted association | b1: change in core-network median CH4 anomaly (ppm) per SD of S, within year x month x hour cells, with log(U5 + 0.5) (D-21, D-22) | 14-day block bootstrap, 2,000 replicates (percentile); CR1 and basic intervals secondary (D-24, D-33) | 95% CI excludes 0 with b1 > 0, AND next-day negative control S(t+24) is not >= 50% of b1 with its CI excluding 0 |
| **H2** directional coupling compatible with transport | Pooled D (lags 1-3, leave-pair-out residuals, inverse null-variance weights), D-26 | All admissible whole-day circular wind shifts on the 273-day window: K = 246 (14 to 259 days), p = (1 + #{T_k >= T_obs}) / (K + 1); smallest attainable p = 0.0040 (D-48) | (i) p < 0.05; (ii) pooled D > 0 under +/-1 h wind-vs-CH4 shifts; (iii) lag centroid increases with transit bin, Spearman > 0 (D-46) |
| **H3** meteorology-mix share | Pooled projection share over 2026-vs-development-year contrasts, Jan-Sep windows, 12 stations x 5 contrasts = 60 (D-40, D-47, D-54) | 14-day blocks resampled within years, jointly across stations, 1,000 replicates | 95% CI excludes 0. Development benchmark (Jan-Sep): 0.026 (-0.028 to 0.124), not supported |

Secondary and descriptive outputs (no pass/fail): per-pair D with max-T; kernel comparison against both simulation references; H1 total association, ERA5 proxy and CR1 interval; per-station H3 shares and 6-regime sensitivity; F5 regime distribution (D-50); X4 W0 vs ERA5 100 m centroids (descriptive, D-62); E10 typology shares (descriptive only; typology not supported in development).

## 4. Contingency rules (fixed before data access)
- H1 not evaluable if S coverage < 70% or fewer than 3,000 usable hours; reported as such, not as a failure.
- H2: pairs with < 100 eligible hours in either direction are dropped from the pooled statistic; H2 not evaluable if fewer than 10 pairs remain.
- H3: contrasts with any empty merged regime are reported as not estimable; H3 not evaluable if fewer than 30 contrasts remain.
- A station with < 50% valid CH4 in the window is excluded from all tests and listed.
- Code errors found after unblinding: fix, re-run once, and report both runs with the diff. Methods are never changed in response to results.

## 5. Procedure
1. Researcher approves this protocol; commit unchanged; tag `protocol-freeze`; record commit hash and `requirements.txt` hash.
2. Re-verify source hashes. The splitter (to be written and committed before the tag) reads raw exports and writes only 2026-01-01 to 2026-10-01 rows to `sealed/e08_panel/`, with checksums.
3. Run E08 once (seed 20261190). Commit all outputs unchanged, including failures.
4. Report development vs confirmation for every estimand (Figure 10).

## 6. Disclosure of development-informed choices
All confirmatory specifications were chosen after inspecting 2021-2025 data, which earlier assistants and this project analysed repeatedly. Choices explicitly informed by development results: H1 response without same-day background (D-21); finite-shift null (D-48, replacing D-29); kernel criterion reduced to monotonic centroid (D-46, replacing D-36 after the failed E06 criterion); Jan-Sep window (D-54); R3 episode rule (D-18). Earlier exposure to 2026 information: a count of valid AMS 2 CH4 hours (3,379) in a prior audit; header rows of 2026 exports; ERA5 and FIRMS 2026 records loaded with their files (meteorology and fire data, not methane outcomes). Full table in `SEALED_DATA_POLICY.md`.
