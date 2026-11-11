# E08 pre-freeze verification report (2026-11-10)

**Status:** implementation and development dry run complete. **NOT frozen. No `protocol-freeze` tag. The 2026 splitter has not been run; no 2026 methane value has been opened; E08 has not been executed.** `run_e08.py --mode confirm` is hard-disabled until the freeze.

## Code and environment
| Item | Value |
|---|---|
| Implementation commit | `ff57f65` (library, splitter, runner, tests) |
| Dry-run outputs commit | this commit (see `git log`) |
| Python | 3.12.3 |
| `requirements.txt` SHA-256 | 25ecaa8fab6b9985f3ca6d9f9b7691bf9e41dc1d6ae14b37fc9b76d6573dd3fe |
| `config/project.toml` SHA-256 | 609c894b2b8d7d637c94a55b0ee14b21754d30f36a8d52e1f125ea3d6a6e80db |
| `PROTOCOL_E08_DRAFT_v2.md` SHA-256 | 9fae852d1c1d3c7dd5d6168871968cade8b59088eee94715831a88803cff6a87 |
| `src/wbea/e08.py` | 97852a99da70b1387f6ec4f4d16946cca0a1be7034f9deb1baeb39236362884a |
| `src/build/build_e08_panel.py` | 2d135e4d21a87d0a64dd09ddbc6b4621ec428ac6c25d12d2d74f1a14d9e03da7 |
| `experiments/E08_confirmation/run_e08.py` | 04e4ef7a06d6f562733b69e1309ac86fb0c3886fe9a35540211f460e2f3a3084 |
| Seeds | base 20261190; H1 +1, H2 +2 (centroid bootstrap), H3 +3 |

## Unit tests: 33 of 33 pass (`python -m pytest -q tests`)
New E08 tests (`tests/test_e08.py`):
- finite-shift K = 246 for 273 days and the p formula with ties;
- H1 rule, 6 cases, including "large NC point estimate with CI containing 0 is not flagged" and "exactly 50% is flagged";
- centroid rule: strict increase, one adjacent inversion (rho 0.9, met), two inversions (rho 0.8, not met with 5 bins), ties, 4-bin thresholds, three not-evaluable cases, CI including 0;
- Kitagawa identity and empty-group non-estimability;
- merge rules (dense, one sparse cell, all sparse);
- non-estimable replicate fraction at 10% (evaluable) and 15% (not evaluable);
- splitter on synthetic workbooks: inclusive boundaries, tokens preserved, an out-of-order row placed **after** the end time is never read, checksum mismatch and non-increasing timestamps raise;
- splitter on permitted 2025 development data reproduces the development panel exactly (AMS 1, 1-3 Mar 2025, values and tokens).

## Dry run (development data 2025-01-01 01:00 to 2025-10-01 00:00; NOT a confirmation)
Splitter: 12 stations x 6,552 hours = 78,624 rows; source hashes verified; output hashes in `dryrun_2025/SHA256SUMS.txt`. No station excluded. Runtime 14 s.

| Test | Result | Rule outcome (dry run) |
|---|---|---|
| H1 primary b1 (core median, cells, log wind) | 0.048 (0.032 to 0.064), n = 6,014 | (a) met |
| H1 joint model: b1_joint / b_nc | b_nc 0.0002 (-0.0094 to 0.0070) | (b) not flagged; this is not proof of no confounding |
| H2 pooled D | 0.184, p = 0.0040 (= 1/247, floor), K = 246, 27/27 pairs | (i) met |
| H2 +/-1 h wind shift | 0.169 / 0.153 | (ii) met |
| H2 lag centroids (h) | 0.30, 0.31, 0.51, 1.31, 1.43; 5 bins; rho 1.0; c_last - c_first CI lower 0.37 | (iii) met |
| H2 hours | wind-eligible 75,852; complete-methane hours used 59,143 | reported separately |
| H2 null by seasonal-offset tercile (mean / SD) | short -0.003 / 0.032; medium -0.018 / 0.032; long +0.003 / 0.038 | diagnostic; does not prove exchangeability |
| H3 share (2025 vs 2021-2024, Jan-Sep) | -0.007 (-0.084 to 0.124); 48/48 contrasts; 0% non-estimable replicates | not met |

These outcomes use development data already analysed many times; they verify the code path only. Methods were not changed in response to them.

## Deviations from v2 and items to complete before the freeze
1. **Dry-run design (expected):** H3 contrasts use 2021-2024 because 2025 plays the confirmation year; E08 uses 2021-2025.
2. **Descriptive outputs not yet implemented in the runner** (non-gating, protocol section 4): per-pair max-T p; H1 CR1 and basic intervals; ERA5 proxy; kernel comparison against both simulation references; per-station H3 shares and 6-regime sensitivity; F5 distribution; X4 centroids; E10 shares with assessability split. Proposal: implement as `run_e08_descriptive.py`, dry-run it on 2025 and commit **before** the freeze, so that all E08 code is frozen together.
3. **Wording:** outputs label rule results "confirmed"; in reports these will read "criterion met / not met", and only E08 outputs can be called confirmation.
4. No other deviation found. Code corrections during development: one test tolerance (Spearman 0.9999999999999999 vs 1.0); no change to any rule.
