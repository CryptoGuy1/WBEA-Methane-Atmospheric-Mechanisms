# Final integrated experimental audit: WBEA methane study (2026-11-11)

**Scope:** E08 (registered confirmation), E12 (synthetic calibration), E13 (seasonal-shift sensitivity), the E06 transport diagnostics and the post-confirmation H1/H3 investigations.

**Nature:** an audit only. No experiment was rerun, no threshold or parameter was changed, no branch was merged and no frozen file was modified. The audit is recorded on branch `audit/final-experimental-audit` (from `main`).

## 1. Integrity of the frozen record
| Item | Value | Verified |
|---|---|---|
| `protocol-freeze` | 2b7c79e259ea1fbc957998da9f921db8abdf38ea | Identical locally and on GitHub |
| `e08-confirmation` | 4c011a8928d5e0b343c3727bea9c5c99cfc5ce51 | Identical locally and on GitHub |
| `main` | d61f8eae8eaae2b62d6695b63ba7137d74136389 | Local = remote |
| `research/e12-h2-null-calibration` | 0ebdff79e625c760ae3ad56ddfb153c14637e1bf | Local = remote |
| `research/e13-h2-seasonal-shift-sensitivity` | 17083f5818f19cedba34170b2a98c5b7bf3cbcc4 | Local = remote |
| `manuscript/section2-figures-tables` | 16c013b24c80733976f30564652b18e0698dc5c5 | Local = remote |
| Frozen code, config, protocol, E08 outputs | Empty diff against both tags on every branch | Enforced by tests on every branch |

## 2. Test suites (each branch in an isolated worktree, untracked data linked read-only)
| Branch | Result |
|---|---|
| main | **39/39 pass** |
| E12 | **46/46 pass** (incl. full 246-shift parity with the frozen H2 pipeline) |
| E13 | **52/52 pass** (incl. exact reproduction of E08 pooled D and p) |
| manuscript | **39/39 pass**; Section 2 validator 24/24 |

## 3. Numerical cross-check (`audit/audit_crosscheck.py` -> `audit/crosscheck_results.csv`)
**131 of 132 reported values match their saved result files** at the precision reported:
- E08 primary 34/34; E08 descriptive 8/8; post-confirmation 6/6;
- E13 33/33; E13 definitions 5/5; E13 vs E08 3/3; E06 1/1;
- E12 41/42.

- **E13 reproduces E08 exactly:** pooled D 0.2879317084641316, p = 1/247, K = 246.
- **The E13 seasonal configurations match their pre-registered definitions in code:** calendar-quarter blocks of 2,160/2,184/2,208 h with shifts 14-76 d (K = 63); cold/warm blocks of 2,880/3,672 h with shifts 14-106 d (K = 93).
- **E06 criterion:** confirmed failed from the saved file. Only the 0-0.5 h bin (observed 0.247 h; reference 0.170-0.298 h) lies within its reference range: 1 of 5, where 4 were required.
- **The one mismatch (erratum, not material):** E12 report Table 5.1 gives the N2a Wilson lower bound as 0.033; the saved value is 0.032465 (0.032). The classification (calibrated) is unchanged. The E12 report was not edited (outside this audit's authority); the correction is listed here.

## 4. Sealed-data safeguards
- Confirmation data entered E08 only through the release-guarded runners after the freeze (verified in E08 records).
- Post-confirmation readers: `experiments/E08_post_confirmation_exploratory/` (authorised), E13 (authorised, named exemption), and `manuscript/scripts/section2/prepare_data.py`/`validate.py` (authorised descriptive availability).
- **Safeguard gap (documentation/safeguard, not material):** `tests/test_seal.py` scans only `src/` and `experiments/`. It does not scan `manuscript/`, and its E08 exemption is a prefix match (`experiments/E08*`). No unauthorised access was found, but the test is narrower than its name implies. Recommendation: extend its scope, with named exemptions, when the branches are merged.

## 5. Evidence summary
See `audit/EVIDENCE_MATRIX.md`, which states the status of every row (development, confirmation or post-confirmation).
- **Confirmed (registered):** H1 (0.052, 0.039-0.069); H2 (D = 0.288, p = 1/247).
- **Not confirmed:** H3 (0.011, -0.020 to 0.043).
- **Failed, inconclusive or unsupported (reported without softening):**
  - E06 kernel criterion (failed);
  - long-transit lag shortfall (unresolved);
  - E09 elevated wind (inconclusive);
  - E10 typology (not supported);
  - E07 and E08 H3 (not supported / not confirmed);
  - E12 null calibration (inconclusive by margin);
  - E12 seasonal confounding (whole-period shift sensitive);
  - E12 3 h lag (0% power);
  - E12 falsification (H2 cannot identify methane transport);
  - H1 2026 next-day control anomaly (unexplained);
  - H3 estimator dominated by AMS 18 (92.9%).
- **Strengthening (post-confirmation):** E13. The 2026 H2 statistic exceeds all season-restricted surrogates (0/63, 0/93, 0/63-65).

## 6. Unresolved issues, classified
| Issue | Could it change a registered result? | Classification |
|---|---|---|
| WBEA 2026 annual validation (due about March 2027) may revise the 2026 data | **Yes, in principle** (numbers, possibly decisions) | **Potentially material; pre-declared.** The frozen protocol already specifies one re-run after the review. State as a limitation now; run when data are final |
| Station relocations 2021-2026 unverified for 10 of 12 stations | Only if a station moved enough to change pair eligibility (30 km) or transit weights; AMS 1 (est. 1997) and AMS 23 (est. 2017) predate the study | **Potentially material, low likelihood.** Verify from *Volume III Continuous Data 2025* before submission |
| H2 exchangeability across seasons | Addressed: E12 shows the risk, E13 shows the 2026 result is robust to it | Resolved for this result (post-confirmation) |
| H2 does not discriminate methane transport from advected shared signals (E12 N1b) | No (decision unchanged) | **Material to interpretation:** wording must remain "directional coupling compatible with transport" |
| H1 2026 next-day control negative, unexplained | No (rule not triggered) | **Material to interpretation:** report prominently; no causal reading of H1 |
| H3 dominated by AMS 18 | No (registered estimate retained) | **Material to interpretation:** the H3 conclusion is estimand-specific |
| p-value floor 1/247 | No | Limitation of resolution |
| E12 N2a rounding erratum | No | Documentation |
| Protocol file header still reads "DRAFT ... Not frozen" (tagged version) | No | Documentation: explain in Methods/SI |
| Reference period ends 31 Dec 2023 23:00 (the hour-ending 00:00 value is excluded) | No | Documentation (Methods) |
| Seal-test scope gap | No | Safeguard documentation |
| E08 has no figure; experiment figures in development style | No | Presentation (Results phase) |
| GitHub token exposed in chat | No | Security: revoke |

**No reproducibility failure or numerical error was found that would invalidate any experimental result.**

## 7. Recommendation
**Experimentation can be closed for the purpose of writing Methods, Results and Discussion.** The evidence base is complete, internally consistent and reproducible. Before submission, two non-experimental actions remain:
1. The pre-declared post-annual-review re-run of E08 when WBEA finalises 2026, with frozen code and criteria; report both runs if anything differs.
2. Station-relocation verification from WBEA documentation.

No further sensitivity or exploratory experiments are recommended. X2 and full X3 remain not started, as decided.

## 8. Reproducibility commands
```
git clone https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms && cd WBEA-Methane-Atmospheric-Mechanisms
# WBEA data (not in git): place data/dev/ and sealed/e08_panel/ as described in DATA_PROVENANCE.md and verify the SHA-256 manifests
git checkout main                                        && python -m pytest -q tests
git checkout research/e12-h2-null-calibration            && python -m pytest -q tests experiments/E12_h2_synthetic_null_calibration/tests
git checkout research/e13-h2-seasonal-shift-sensitivity  && python -m pytest -q tests experiments/E12_h2_synthetic_null_calibration/tests experiments/E13_h2_seasonal_shift_sensitivity/tests
git checkout manuscript/section2-figures-tables          && python -m pytest -q tests   # then see manuscript/scripts/section2/README.md
git checkout audit/final-experimental-audit              && python audit/audit_crosscheck.py   # 131/132; 1 rounding erratum
# Regenerate (optional): E08 primary/descriptive via experiments/E08_confirmation/run_e08*.py (--mode confirm needs the protocol-freeze commit);
# E12: make -C experiments/E12_h2_synthetic_null_calibration production analysis; E13: python experiments/E13_h2_seasonal_shift_sensitivity/run_e13.py
```

## 9. Deliverables (this branch)
`audit/FINAL_AUDIT_REPORT.md`, `audit/EVIDENCE_MATRIX.md`, `audit/FIGURE_INVENTORY.md`, `audit/audit_crosscheck.py`, `audit/crosscheck_results.csv`, and `audit/manuscript_tables/` (`table03_registered_confirmation.tex`, `table04_validation_sensitivity.tex`, `tableS_negative_inconclusive.tex`, plus the CAS compile check: 0 errors, 0 overfull).
