# Review backlog

Policy (D-34): material issues (data integrity, mathematical validity, statistical inference, reproducibility,
downstream dependence) are fixed immediately and recorded here; non-critical issues wait for the integrated
review after E07. Original results are never overwritten; corrections are amendments or addenda.

Severity: **M** material (fixed now) · **N** non-critical (deferred) · **I** information only.

| ID | Raised | Severity | Experiments | Issue | Proposed resolution | Decision / status |
|---|---|---|---|---|---|---|
| RB-01 | 2026-11-10 (researcher review) | M | E02, E03, E04, E07 | E02 overstated the Z-gap test as showing missing-at-random; the test only compares neighbouring observed hours and cannot detect a spike confined to a Z hour | Reword as "no systematic difference in neighbouring observed concentrations"; treat conditional MAR as a working assumption; add a sensitivity that does not rely on it | **Fixed.** E02 and E03 amended (original wording preserved); E04 sensitivity with hours 01-06 excluded: 0.048 (0.041-0.054), unchanged; D-30. E07 must report Manski bounds |
| RB-02 | 2026-11-10 (researcher review) | M | E03 | Co-occurrence vs distance interpreted beyond description; pairs share stations; no dependence-aware uncertainty | Keep as descriptive; joint block bootstrap of all 66 lifts; Mantel permutation of station labels; leave-one-station-out | **Fixed.** Addendum: Spearman -0.82 (-0.86 to -0.73); Mantel p = 0.0001; LOSO -0.86 to -0.76; core-only -0.64; interpretation restricted (D-32) |
| RB-03 | 2026-11-10 (researcher review) | N | E03, E04, E07 | "Smoke" label overstates what FIRMS + PM2.5 measure | Rename to "potential wildfire-influenced period" (PWIP) | **Fixed in documentation** (D-31); archived file and variable names kept |
| RB-04 | 2026-11-10 (E04 review) | N | E04, E08 | Percentile bootstrap intervals asymmetric around estimates | Report CR1 cluster-robust interval alongside | Deferred to manuscript; CR1 and bootstrap SE agree (0.0028 vs 0.0029), so no inferential problem (D-33) |
| RB-05 | 2026-11-10 (E04 review) | N | E04 | AMS 1 T10 - T2 proxy much weaker (0.013/SD) than tower or ERA5 | Discuss layer depth and siting; no new analysis unless reviewers ask | Deferred to integrated review |
| RB-06 | 2026-11-10 (E04 review) | N | E04 | Seasonal heterogeneity (JJA 0.038 vs MAM 0.056) not part of the pre-registered estimand | Descriptive season x S interaction in the manuscript, labelled exploratory | Deferred to integrated review |
| RB-07 | 2026-11-10 | N | E05, E08 | Per-pair p-values at the 1/1,001 floor | 5,000 shifts in E08 (D-29) | Resolved for E08; development unchanged |
| RB-08 | 2026-11-10 | N | E05 | Hour sets use wind at the receptor hour only; wind may change during transit | Sensitivity with wind averaged over t-l..t | Deferred to E05+E06 joint review |
| RB-09 | 2026-11-10 | N | E05 | AMS 9 and AMS 18 alternate 10/20 m wind sensors | Height-stratified D for AMS 9 pairs | Deferred to E05+E06 joint review |
| RB-10 | 2026-11-10 | N | E01, all | Relocation and instrument histories unverified for 11 stations | Parse WBEA Volume III site documents when supplied | Open; awaiting documents |
| RB-11 | 2026-11-10 | N | E02, all | Official meanings of Z, SP and "." not confirmed | WBEA QAP or provincial code table | Open; awaiting documents |
| RB-12 | 2026-11-10 | I | all | `run_metadata.json` written before the author rewrite cites pre-rewrite hashes | Mapping in HISTORY_REWRITE.md | Resolved |
| RB-13 | 2026-11-10 | N | all | pandas FutureWarnings (concat sorting, object dtypes) in logs | Code hygiene pass before E08 freeze | Deferred to integrated review |
| RB-14 | 2026-11-10 | I | all | GitHub Issues not used: the access token has Contents permission only | Backlog kept as this file | Resolved |
