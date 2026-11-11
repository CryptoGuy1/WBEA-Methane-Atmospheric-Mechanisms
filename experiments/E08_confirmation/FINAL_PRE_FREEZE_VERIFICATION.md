# E08 Final pre-freeze verification report (2026-11-10)

**Status: complete verification package for final scientific review.** Not frozen: no `protocol-freeze` tag; confirmation mode disabled in both runners; the 2026 splitter has not been run; no 2026 methane value has been opened. Supersedes `PRE_FREEZE_VERIFICATION.md` (preserved).

## 1. Code, sources and environment
| Item | Value |
|---|---|
| Code + dry-run outputs commit | `dc66622096722878ffca42a8210eae37a77c00ca` |
| Python | 3.12.3 |
| `requirements.txt` | 25ecaa8fab6b9985f3ca6d9f9b7691bf9e41dc1d6ae14b37fc9b76d6573dd3fe |
| `config/project.toml` | 609c894b2b8d7d637c94a55b0ee14b21754d30f36a8d52e1f125ea3d6a6e80db |
| `PROTOCOL_E08_DRAFT_v2.md` | 9fae852d1c1d3c7dd5d6168871968cade8b59088eee94715831a88803cff6a87 |
| `src/wbea/e08.py` | 502b2d073e0bf11975fa9ca385fdb09fa9591e5107633b31dcff901c53b3e455 |
| `src/wbea/h2.py` | dd1e2dce836061c52cdb35a1c6388219d5b1ea778232ee7bd55f58cb9f465fa6 |
| `src/build/build_e08_panel.py` | 2d135e4d21a87d0a64dd09ddbc6b4621ec428ac6c25d12d2d74f1a14d9e03da7 |
| `run_e08.py` | e88a092f03ce9e526744a1fdff198b5d59c05d318dc7fdf4f3a637b247eb3321 |
| `run_e08_descriptive.py` | 5581fdc905d99fa279efcd7e229924e49380eba0b512ac88b89fa94dd7e6430a |
| Source workbooks (12) | full SHA-256 in `PROTOCOL_E08_DRAFT_v2.md` section 1 and `manifests/station_exports_2021_2026_manifest.csv`; all 12 verified by the splitter in the dry run |
| Seeds | base 20261190; H1 +1; H2 centroid +2; H3 +3; ERA5 proxy +5; six-regime +6; F5 +7 |

## 2. Tests: 38 of 38 pass
Full list in `dryrun_2025_final/test_results.txt`. The 33 earlier tests are preserved. Five were added:
- max-T and inverse-null-variance pooling;
- H3 core with **four and five** development years (synthetic);
- H3 empty-regime handling under 18 single cells (non-estimable) and the six-regime grouping (estimable);
- both runners refuse `--mode confirm` with "not authorised";
- the descriptive runner contains no decision-rule call and carries the primary-output hash guard.

## 3. Implementation cross-check on common development inputs (`crosscheck_dev.py`)
| Hypothesis | E08 implementation | Established implementation | Difference and reason |
|---|---|---|---|
| H1 association, full development period | 0.047521 | E04 primary 0.04752 | none |
| H1 negative-control coefficient | -0.0000385 | E04 -0.00004 | rounding of stored value |
| H2 per-pair D, 27 pairs | - | E05 | max 5.0e-6 (E05 CSV stored to 5 decimals) |
| H2 pooled D using E05 weights | 0.12851 | E05 0.128 | rounding of stored null SDs. E08 itself uses weights from all admissible finite shifts (D-48), not E05's 1,000 random shifts, so the E08 pooled value on the same data would differ slightly by design |
| H3, 2025 vs 2021-2024, 48 contrasts | share -0.00737 | E07-r3 same contrasts -0.00715 | composition terms differ by at most 3.1e-5, totals by at most 1.8e-4; merge groups identical 48/48. Cause: E07-r3's Jan-Sep window included the hour ending 1 Jan 00:00 (which belongs to 31 Dec); E08 starts at 01:00 as specified |

Reference quantities (2021-2023 medians, thresholds, S standardisation, tercile cuts) are identical in both code paths. Inference settings differ only where v2 changed them (finite shifts; one joint confirmation-year draw for H3).

## 4. Primary dry run (development data 2025-01-01 01:00 to 2025-10-01 00:00; NOT a confirmation)
Splitter: 78,624 rows (12 x 6,552); no station excluded. Re-run after refactoring: all H1, H2 and H3 values identical to the first dry run (pooled D differs by 5.6e-17, floating-point summation order).

| Test | Result | Rule outcome |
|---|---|---|
| H1 primary coefficient | 0.048 (0.032 to 0.064), n = 6,187, S coverage 100% | (a) met |
| H1 joint model: contemporaneous b1_joint / next-day b_nc | 0.049 / 0.0002 (-0.0094 to 0.0070); ratio 0.003 (-0.18 to 0.15), paired bootstrap | (b) not flagged; not proof of absence of confounding |
| H2 pooled D | 0.184; p = 0.0040 (floor, K = 246); 27/27 pairs | (i) met |
| H2 +/-1 h wind shift | 0.169 / 0.153 | (ii) met |
| H2 ordered lag-centroid trend | 0.30, 0.31, 0.51, 1.31, 1.43 h; rho 1.0; c_last - c_first CI lower 0.37 | (iii) met |
| H2 hours | wind-eligible 75,852; complete-methane hours in the statistic 59,143 | both reported |
| H3 share (48 contrasts) | -0.007 (-0.084 to 0.124); 0% non-estimable replicates | not met |

## 5. Descriptive dry run (no pass/fail; `dryrun_2025_final/descriptive/`)
| Output | Result |
|---|---|
| H2 verification | Null matrix and D identical to primary; weights = normalised inverse null variances; complete-methane counts: library = independent direct count for all pairs |
| H2 per-pair max-T | 7 of 27 pairs family-wise p < 0.05 (`h2_pairs_maxT.csv`) |
| H1 intervals | percentile 0.032-0.064 (reproduces primary); basic 0.032-0.065; CR1 0.032-0.065 (SE 0.0083) |
| H1 ERA5 proxy (-log BLH, AMS 5 cell) | 0.056 (0.042 to 0.070) |
| Kernel vs references (SSE) | mask-gated A = 0.3: 0.131; continuous source A = 0.3, 50 replicates: 0.498 |
| H3 per-station shares | `h3_per_station_shares.csv`; six-regime share -0.018 (-0.130 to 0.174) |
| F5 regime distribution | stable-low-wind enrichment 3.14 (2.77-3.57); intermediate 1.29; advective 0.23 (0.17-0.29) |
| X4 centroids, W0 vs ERA5 100 m transit | W0: 0.30, 0.31, 0.51, 1.31, 1.43; ERA5: 0.16, 0.48, 0.55, 0.89, 1.21 (bin sizes differ, `x4_centroids.csv`) |
| E10 typology | lead assessable (n = 423): advection-compatible 31%, accumulation-compatible 6%, mixed 11%, isolated 52%; **no assessable pair (n = 809; not physically isolated)**: accumulation-compatible 21%, isolated 79% |

**Guard evidence:** on the first descriptive attempt the hash guard aborted the run, because my shell command was writing the descriptive log into the primary output folder. The runner itself modified nothing. The log is archived (`descriptive/guard_trigger_log_first_attempt.txt`); the run was repeated with the log inside `descriptive/`, and the guard passed.

## 6. Development-only workflow
The splitter, primary runner and descriptive runner ran end to end on development files only. The splitter stops at the first row after the window end (unit-tested with an out-of-order row placed after the end). ERA5 for the window is read from the reanalysis file (meteorology, not a methane outcome).

## 7. Limitations and items for the reviewer
1. **Dry-run outcomes verify code only.** The 2025 data were analysed repeatedly during development.
2. **E10 window standardisation:** the descriptive typology standardises upstream residual changes within the analysis window, whereas E10 standardised over 2021-2025. Disclosed here; the typology is descriptive and unsupported in any case.
3. **ERA5 recency:** ERA5 for the 2026 window comes from the same reanalysis file; recent months may be preliminary ERA5T. It is used only in descriptive outputs.
4. **Code corrections during this phase:** (a) refactoring with identical results; (b) one test tightened so the primary runner's confirm refusal is actually exercised (it had passed through an argument error); (c) typo fix in the cross-check script. No decision rule or threshold was changed.
5. **No deviation from v2 decision rules.** H3 in the dry run uses four development years by design.

## 8. Remaining steps (require separate authorisation)
1. Researcher final authorisation of v2 and this package.
2. Enable `--mode confirm` (remove the guard lines only), commit, record hashes, tag `protocol-freeze`.
3. Re-verify source hashes; run the 2026 splitter; run E08 primary and descriptive once; commit all outputs unchanged.
