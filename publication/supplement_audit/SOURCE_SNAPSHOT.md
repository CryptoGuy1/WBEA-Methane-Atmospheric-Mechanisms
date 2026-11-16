# Source snapshot (audit run 2026-11-15)
## Branch heads used (local; verified against GitHub)
| Branch | Commit | GitHub |
|---|---|---|
| research/e15-h2-matched-pair-comparability (**primary experiment source**) | `17883015a4ed7e998701cf67a77a4a7c1c2754a4` | identical |
| research/e14-h2-empirical-yearswap-null | `7c4b53a510a61678ea691fb65efcba4985b4e140` | identical |
| research/e13-h2-seasonal-shift-sensitivity | `a0f4e9fee2ec8f1022ca592d440734ab93033056` | identical |
| research/e12-h2-null-calibration | `0ebdff79e625c760ae3ad56ddfb153c14637e1bf` | identical |
| audit/final-experimental-audit | `7c83767cf81f2b70a8f316410a43c22f59d2be8d` | identical |
| manuscript/section2-figures-tables (publication figures) | `b61ffbfd35f9cc97626d8f92840e52ac4f7e74ad` | identical |
| main (local) | `d61f8eae8eaae2b62d6695b63ba7137d74136389` | **behind**: GitHub main = `aa9556d36be83c2964ef19fdf89afc937b766d0e` (merges of PR #1 audit and PR #2 E13/E12); frozen paths untouched by those merges |

**Ancestry:** E15 contains main (`d61f8ea`), E12, E13 and E14. It does not contain the audit or manuscript branches.

## Frozen tags (peeled commits; identical locally and on GitHub)
- `protocol-freeze` -> `2b7c79e259ea1fbc957998da9f921db8abdf38ea`
- `e08-confirmation` -> `4c011a8928d5e0b343c3727bea9c5c99cfc5ce51`

## Integrity checks run (non-mutating)
- Regression suite on this branch (repository tests + E12, E13, E14, E15): **70 passed**.
- Frozen code, config, protocol and E08 runner vs `protocol-freeze`: **0 lines** changed.
- E08 confirmation outputs vs `e08-confirmation`: **0 lines** changed.
- Experiment directories on this branch vs the E15 head: **0 files** changed.
- Evidence values re-read from authoritative files: **30/30 verified** (`evidence_manifest.csv`).
- Figures: **23/23** catalogued with SVG SHA-256 (`figure_manifest.csv`).
- Tables: **14/14** authoritative sources exist (`table_manifest.csv`).

## Audit output checksums (SHA-256)
- `build_manifests.py`: `be0a2fe7a5ee7c205cdcfefce09655409b64b7386f90fae8ff3b29197d895174`
- `figure_manifest.csv`: `81ae1fc2fdf0860ed946a6fd4f343f852079ab44d69fba078460299e4f69c43c`
- `table_manifest.csv`: `0c286cb8345fec9ade4fac7e5d6c32fcb0c27a73f3e075192cd75a1a6872e660`
- `evidence_manifest.csv`: `b08b2d0250aa5fc072c25bc890eab36cf5d33dd69d9cf0d2ea4efc97fd2e1b2f`
- `FIGURE_QA_REPORT.md`: `fb878da7d9ab5124ad10356c59dc625410aa13445d6900148745b64430b7dd2c`
- `SUPPLEMENT_OUTLINE.md`: `e7cd647164b8fb7cccea8d057234db19b3ab0d997d9bddc026717882233f3d96`
- `REPRODUCIBILITY_GAPS.md`: `a998f095bcec74fbbf64136cb5fc089608c18f074904f2805e69c3f1b3c9ec9d`
- `SUPPLEMENT_EVIDENCE_AUDIT.md`: `7e2651c183cc885fcdebc131becf99c343e1e4cdfbfa19295fb03deb9a3f65c2`
