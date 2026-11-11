# E13 Manuscript handoff
**Branch:** https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/research/e13-h2-seasonal-shift-sensitivity (from E12 head 0ebdff7; not merged).
**Commits:** plan 2d7227c (pre-registration, before any seasonal 2026 statistic) · implementation and tests babd0bd · results and reports: see `RESULTS_COMMIT.txt` and the branch head.
**Unchanged:** E08 (`protocol-freeze` 2b7c79e, `e08-confirmation` 4c011a8) and E12 (0ebdff7), test-verified.

## Verdict
**Strengthens** (pre-registered rule): the 2026 H2 statistic remains extreme under season-restricted shift references (quarters: 0/63 surrogates >= observed; cold/warm halves: 0/93; each quarter separately: 0/63, 0/64, 0/65). It addresses the seasonal-exchangeability concern from E12. It does **not** strengthen a transport interpretation.

## Use in the paper
- **Main or SI figure:** `figures/e13_fig1_reference_distributions` (frozen vs C1 vs C2 reference distributions).
- **SI:** `figures/e13_fig2_per_season`; tables from report sections 5.1 and 5.2.
- **Text:** report section 8 wording.

## Safe claims
- The result is not an artefact of mixing seasons in the shift reference.
- The observed D (0.288) exceeds every surrogate under every tested reference (maximum 0.101).
- The effect is present in each quarter (D = 0.35, 0.22, 0.20).

## Do not claim
- That the season-restricted p-values are exact, or that they rank against 1/247 (they are at different floors).
- That E13 confirms transport, transit times or emissions.
- That per-quarter D values compare across seasons.
- That E13 re-tests or changes the registered decision.

## Open decisions
1. Merge E12 and E13 into `main` (your approval needed).
2. Optional: a second alternative boundary set (for example snowmelt-date blocks), only if reviewers request it. Not run, to avoid boundary selection.
