# Reproducibility gaps, dependencies and open items
Status labels: **OPEN** (unresolved; requires a decision or external information), **KNOWN** (documented limitation), **FIX** (presentation or documentation correction before writing).

## A. Branch dependencies (OPEN)
| Branch | Contains | Missing |
|---|---|---|
| GitHub `main` (`aa9556d`) | E01-E11, E08, the audit, E12, E13 (merged via PRs #1 and #2) | E14, E15, manuscript figures, this audit |
| `research/e15-h2-matched-pair-comparability` | everything experimental | the audit directory and the manuscript figures |
| `manuscript/section2-figures-tables` | the publication figures (Figs. 1-7, regime heatmap) | E12-E15 |

**Consequence:** no single branch holds the full publication source. Before the Supplement is built, E14, E15, the manuscript branch and this audit branch must be merged into `main` (researcher authorisation required), or the Supplement build must read from several pinned commits. The local `main` (`d61f8ea`) is behind GitHub `main` (`aa9556d`); it was not modified by this audit.

## B. Data restrictions (KNOWN / OPEN)
- WBEA hourly data are not in the repository (`data/dev/`, `sealed/` are untracked), so every experiment figure is reproducible only with authorised WBEA access. SHA-256 manifests allow independently obtained copies to be verified.
- `manuscript/data/section4/fig04a_partial_residuals.csv.gz` (40,334 hourly derived values) is deliberately **uncommitted**, pending a decision on redistribution (OPEN). Without it, the main-text Fig. 4a cannot be regenerated from GitHub alone; the extraction script regenerates it from WBEA data.
- The repository is **public** on GitHub. Confirm this is compatible with WBEA terms (OPEN). The GitHub token used in this project should be revoked (OPEN).

## C. Missing or superseded provenance (FIX)
- **E01-E13 figure PDFs are not committed** (gitignored). SVG is the vector source; publication PDFs must be regenerated.
- **`figureS2_detectability`** shows the superseded mask-gated model (D-39). Regenerate.
- **E03 result file `q6_manski_bounds_by_hour.csv`** keeps the superseded "Manski" name in its filename (D-43). Keep the file; relabel in tables and captions.
- **No saved 2026 per-pair bootstrap CIs**, no per-bin 2026 lag-centroid intervals, and no 2026 contemporaneous joint-model CI. These cannot appear in any table.
- **E15 analysis A6 is not evaluable** (undefined surrogates for AMS 2 pairs; DEVIATIONS D2).

## D. Documentation-implementation discrepancies (FIX: disclose in S7)
1. **"H1 total association" not computed.** Protocol section 4 lists it among the descriptive outputs; `descriptive_results.json` does not contain it.
2. **Reduced-network development benchmark not computed by E08.** The protocol contingency table says it "is recomputed on the same reduced network for a like-for-like descriptive comparison". E08 produced no such output; E15 (A5, A5y) provides it post hoc.
3. **Two registered H3 share values** to different precision: 0.011018334786 (`e08_results.json`, authoritative) vs 0.011018148677 (`h3_weight_concentration.json`, recomputed from the 6-decimal CSV).
4. **Two 2026 H1 next-day intervals:** -0.0268 to -0.0051 (registered, 2,000 replicates; authoritative) vs -0.0265 to -0.0036 (post-confirmation diagnostic, 300 replicates).
5. **Development pooled D** saved as 0.1285, shown as 0.129 in the E05 figure and written 0.128 in reports.
6. **E12 report:** N2a Wilson lower bound written 0.033; the saved value is 0.032465.
7. **E11 H1 range:** leave-one-core-station-out estimates span 0.0432-0.0572 (7 rows); the 0.0343 value in the same file is the expanded 11-station response, not a leave-one-out estimate.

## E. External information still missing (OPEN)
- WBEA meanings of missing-data codes Z and '.' (E02).
- Cause of the AMS 2 outage from May 2026 (RB-29).
- Station relocation history for 10 of 12 stations (only AMS 1 and AMS 23 verified).
- Final validated 2026 data (WBEA annual review) and the pre-declared E08 re-run.
- `netmech` licence decision.
- The current Overleaf manuscript (main-text duplication status is UNVERIFIED for every figure).

## F. Citations required in the Supplement
- **Data:** ERA5 (Hersbach et al., 2020); NASA FIRMS VIIRS NOAA-20 collection 2 active-fire product; Natural Earth; WBEA data and SOP-ANA-008.
- **Methods:**
  - Wilson score interval (Wilson, 1927);
  - moving/stationary block bootstrap (Kunsch, 1989, or equivalent);
  - max-T family-wise adjustment (Westfall and Young, 1993);
  - Mantel test (Mantel, 1967);
  - Kitagawa (1955);
  - random-forest meteorological normalisation (Grange et al., 2018; Grange and Carslaw, 2019);
  - extreme missing-outcome scenarios (cite Manski only if the bounds interpretation is retained; D-43 says it is not).
