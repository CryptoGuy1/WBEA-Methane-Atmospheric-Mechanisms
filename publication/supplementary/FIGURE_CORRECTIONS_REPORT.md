# Figure corrections report: Supplementary Figures S1-S23
**Scope:** publication versions of all 23 experiment figure families from `publication/supplement_audit/figure_manifest.csv`.
**Originals:** preserved unchanged in their experiment directories (git diff of `experiments/` against the pinned source `1788301`: 0 files).
**Data:** every plotted value is read from committed result files (pinned commits recorded per input in `figure_manifest.csv`). Scripts carry embedded assertions on key values.

## Common changes (all redrawn figures, S1-S21)
- **Styling:** in-panel titles removed; bold (a), (b) … panel labels; 174.5 mm width (S19: 104.7 mm); DejaVu Sans 6-8 pt; colour-blind-safe palette (grey, blue, orange; cividis/viridis); fonts embedded.
- **Labels:** descriptive labels replace internal experiment and scenario codes.
- **Formats:** PDF and SVG (vector) plus 600 dpi PNG. The only raster element is the hexbin density in S6, which is rasterised by design.
- **S22 and S23 (E14, E15):** copied byte-for-byte from the accepted versions; not regenerated.

## Figure-by-figure
| S | Original (experiment) | Publication file | Transformation | Corrections applied |
|---|---|---|---|---|
| S1 | `figure01_network_geometry` (E01) | `figS01_network_geometry_wind` | redrawn; wind-rose sectors re-extracted (aggregate only) by extract_e01_windrose_sectors.py, identical n to original | titles removed; (a)-(e) labels; 'R1' note dropped; longitudes in degrees W; colour-blind palette |
| S2 | `figure02_coverage_and_gap_timing` (E02) | `figS02_coverage_missing_codes` | redrawn from saved results | colour scale extended to 0-100% (no saturation); vector colour bar; titles removed; code meanings left as raw codes (OPEN) |
| S3 | `figure03_excursion_phenotype` (E03) | `figS03_excursion_structure` | redrawn from saved results | titles removed; cividis; 'lift' axis label |
| S4 | `figureS4_episode_definition_sensitivity` (E03) | `figS04_episode_definition_missing_outcomes` | redrawn from saved results | 'Manski bounds' relabelled 'extreme missing-outcome scenarios' (D-43); titles removed |
| S5 | `figureS1_network_correlation_by_stability` (E03) | `figS05_correlation_by_stability` | redrawn from saved results | vector matrices and colour bar; titles moved to axis labels |
| S6 | `figure04_stability_elasticity` (E04) | `figS06_h1_functional_form` | redrawn; residual density from the authorised plotting-only extraction (verified n = 40,334, beta 0.04752) | titles removed; RF panel retained |
| S7 | `figure05_h1_robustness` (E04) | `figS07_h1_robustness` | redrawn from saved results | 'smoke hours' relabelled potential wildfire-influenced periods (D-31); title removed |
| S8 | `figure06_directional_coupling` (E05) | `figS08_h2_development_pairs` | redrawn; null band = 2.5/97.5 percentiles of saved replicates (as original) | pooled D corrected to 0.1285; reference stated (1,000 random shifts); titles removed |
| S9 | `figure08_residualisation_sensitivity` (E05) | `figS09_h2_residualisation` | redrawn from saved results | title removed; descriptive legend |
| S10 | `figure07_kernel_shape` (E06) | `figS10_lag_kernel_criterion` | redrawn from saved results | titles removed; reference labelled signal-dominated (A = 3), not a CI |
| S11 | `figureS2_detectability` (E06) | `figS11_detectability_models` | REDESIGNED: aggregate detection by amplitude for both models (per-pair continuous-source results were not saved) | superseded mask-gated model shown only alongside the authoritative continuous-source model (D-39), labelled |
| S12 | `e09_centroids_by_wind` (E09) | `figS12_elevated_wind_centroids` | redrawn; original CI and reference bands NOT reproduced (not saved); observed and reference means only | internal codes replaced by descriptive variant names |
| S13 | `e09_r1_centroids` (E09) | `figS13_elevated_wind_revised` | redrawn; original 2.5/97.5% reference bands NOT reproduced (replicates not saved) | internal codes replaced |
| S14 | `e10_typology` (E10) | `figS14_episode_typology` | redrawn; station shares re-tabulated from the saved episode file (7,951 episodes) | 'isolated' split into no assessable upstream pair (55.5%) vs assessable without lead pattern |
| S15 | `figure09_composition_decomposition` (E07) | `figS15_h3_development_decomposition` | redrawn from saved results | 'Manski' relabelled; deweathering marked not validated out of sample (D-44); internal D-16 code removed |
| S16 | `figureS3_baseline_comparison` (E07) | `figS16_baseline_comparison` | redrawn from saved results | 'E04' code removed from legend |
| S17 | `e12_null_rejection_rates` (E12) | `figS17_null_rejection_rates` | redrawn from saved results | scenario codes replaced; advected driver labelled falsification; 5% and 7.5% lines labelled |
| S18 | `e12_null_pvalue_cdf_and_D` (E12) | `figS18_null_pvalues_and_D` | redrawn from saved replicate files | 2026 comparison line REMOVED; codes replaced |
| S19 | `e12_power` (E12) | `figS19_power` | redrawn from saved results | compact width; codes replaced; no curve |
| S20 | `e13_fig1_reference_distributions` (E13) | `figS20_season_restricted_references` | redrawn from saved surrogates | 'cold/warm halves' -> calendar-based blocks; 'E08' removed |
| S21 | `e13_fig2_per_season` (E13) | `figS21_per_quarter_references` | redrawn from saved surrogates | titles removed; integer count axes |
| S22 | `e14_yearswap_null` (E14) | `figS22_cross_year_negative_control` | copied byte-for-byte (accepted v3) | none |
| S23 | `e15_comparability` (E15) | `figS23_matched_pair_comparability` | copied byte-for-byte (accepted) | none |

## Required corrections (FIGURE_QA_REPORT items 1-9): status
1. **E06 detectability (S11):** done. Both models shown and explicitly labelled; continuous-source authoritative (D-39). Per-pair continuous-source results were never saved, so the figure shows aggregate detection by amplitude rather than per-pair scatter. This is a disclosed redesign, not new analysis.
2. **E05 pooled D (S8):** done. 0.1285; reference (1,000 random shifts) stated.
3. **E07 (S15):** done. Manski terminology replaced; deweathering marked not validated out of sample (D-44).
4. **E03 episode figure (S4):** done. "Manski bounds" replaced.
5. **E04 robustness (S7):** done. "Smoke hours" replaced.
6. **E10 (S14):** done. "Isolated" split into *no assessable upstream pair* (4,412 of 7,951 episodes) and *assessable, no lead pattern*.
7. **E13 (S20):** done. Calendar-based blocks; experiment codes removed.
8. **E12 (S18):** done. The 2026 comparison line is removed from the null D panel.
9. **E12 and E09 codes (S12, S13, S17-S19):** done. Descriptive labels; the advected driver labelled a falsification scenario.

## Disclosed limitations of the redrawn figures
- **S12 and S13 (E09):** the original confidence and reference bands were computed at plot time and never saved. Only observed centroids and reference means (plus Monte Carlo SDs) exist, so the publication figures show means without bands. The bands were not recomputed.
- **S1 wind roses:** the sector frequencies were computed at plot time in E01. They were re-extracted with the original code verbatim (aggregates only; identical n = 42,415 / 42,568 / 42,802 hours) to `data/figS01_windrose_sectors.csv`.
- **S6:** depends on the authorised partial-residual extraction file, which is not committed (WBEA redistribution decision OPEN). It can be regenerated from WBEA data with `manuscript/scripts/section4/extract_fig04a_partial_residuals.py`.
- **S2:** missing-data codes Z, '.' and C are shown as raw codes. Their WBEA meanings remain **OPEN**.
- **S16(a)** repeats the H1 functional-form curves of S6(b). This is retained because the original E07 figure presented them as a baseline comparison; it may be dropped at writing time.

## Provenance defect found and corrected during this task
The audit package's `figure_manifest.csv`, `table_manifest.csv` and `evidence_manifest.csv` had **empty `source_commit` fields** (23/23, 14/14, 30/30). The audit builder ran `git log -- <path>` from a subdirectory, where paths are resolved relative to the working directory. The publication manifests recompute every commit from the repository root, so all fields are now populated. The audit files are left unchanged as a historical record and are superseded by `publication/supplementary/*_manifest.csv`.
