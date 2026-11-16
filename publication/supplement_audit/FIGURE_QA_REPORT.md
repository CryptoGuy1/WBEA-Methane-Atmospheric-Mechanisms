# Figure QA report: 23 distinct experiment figures
**Method:** every figure was opened and visually inspected as a PNG during this audit session. E01 and E02 were inspected in this audit; the other 21 were inspected earlier in the same session (Results-structure review and figure-production tasks), and the conclusions are re-stated here. Plotted values were checked against the saved results named in `figure_manifest.csv`.
**Formats:** E01-E13 are committed as SVG and 300-dpi PNG. Their PDFs are excluded by `.gitignore`, so the **SVG is the vector publication source**. E14 and E15 are committed as PDF, SVG and 600-dpi PNG.
**Style:** none of E01-E13 is in final publication style: in-panel titles, bare "a"/"b" labels, variable widths. All need regeneration for the Supplement. That is a presentation task, not a numerical one.

## Corrections required, by severity
**Must correct (content or scientific labelling)**
1. **S11 `figureS2_detectability` (E06):** shows the **superseded mask-gated** injection model. Decision D-39 makes the continuous-source model primary (45%/83% detection at A = 0.2/0.4, memory 180 min). Regenerate from `review_continuous_detectability.csv`, or show both models clearly labelled.
2. **S8 `figure06_directional_coupling` (E05):** panel (b) states "Pooled D = 0.129"; the saved value is 0.1285 (other documents say 0.128). Use 0.1285 and state that the development reference was 1,000 random shifts.
3. **S15 `figure09_composition_decomposition` (E07):**
   - panel (a) uses "Manski lower/upper" (renamed "extreme missing-outcome scenarios", D-43);
   - it shows the machine-learning deweathering share 0.213 without stating that it was **not validated out of sample** (D-44; `r1_deweathering_forward_validation.csv`).
4. **S4 `figureS4_episode_definition_sensitivity` (E03):** "Manski bounds" label (D-43).
5. **S7 `figure05_h1_robustness` (E04):** "smoke hours excluded" (renamed to potential wildfire-influenced periods, PWIP; D-31).
6. **S14 `e10_typology` (E10):** the "isolated" category (70.3% of episodes) mixes two different things: episodes with **no assessable upstream pair** (55.5% of all episodes; `addendum_assessability_split.csv`) and assessable episodes with no lead pattern. Split or relabel it. The caption must state that the typology was **not supported** (placebo 0.122 vs 0.148).
7. **S20 `e13_fig1_reference_distributions` (E13):** titles "Frozen E08" and "cold/warm halves (C2)". Use "calendar-based blocks (Jan-Apr/May-Sep)" per the E13 closure (`a0f4e9f`); remove experiment codes.
8. **S18 `e12_null_pvalue_cdf_and_D` (E12):** panel (b) overlays the registered 2026 D on simulated null distributions. This invites a magnitude comparison the simulations do not support. Remove the line or add a caveat.
9. **S17-S19 (E12) and S12-S13 (E09):** internal scenario codes (N0, N1a, N1b, N2a, N2b, N3, P1, P1T; W0, W4_full, X4a) must become descriptive labels. N1b must be labelled a **physical-specificity falsification**, not a null.

**Should correct (presentation)**
10. **S2 `figure02_coverage_and_gap_timing` (E02):**
    - the colour scale begins at 50%, so lower months saturate (state this or extend to 0%);
    - the footnote "meanings of Z and '.' not yet confirmed by WBEA" is an **OPEN** item.
11. **S1 `figure01_network_geometry` (E01):** internal "R1" note; panel (b) compressed.
12. **S16 `figureS3_baseline_comparison` (E07):** legend contains "E04".
13. **S19 `e12_power`:** low information density (six points at 100%). Compact it.
14. **All E01-E13 figures:** remove in-panel titles; use (a), (b), … labels; full CAS width (174.5 mm) or single column; embed fonts.

**No correction needed:** S22 `e14_yearswap_null` (v3) and S23 `e15_comparability`. Both are vector, 174.5 mm and caption-ready.

## Checks performed
| Check | Result |
|---|---|
| Units and axis labels | present on all figures; D marked dimensionless where shown (E12 axes say "pooled D" without a dimension note; fix during regeneration) |
| Panel consistency | E09 two figures overlap in content (S13 authoritative for the decision); S12 and S13 may combine |
| Text overlap | none found at native size; E01 panel (b) cramped |
| Legends and annotations | internal codes as listed above |
| Agreement with saved tables | all plotted headline values agree with saved results (`evidence_manifest.csv`, 30/30 verified), except the "0.129" label (item 2) and the superseded detectability model (item 1) |
| Overstated conclusions | none in the figures themselves. Captions must carry: failed (E06 kernel), inconclusive (E09), not supported (E07, E10), negative control not calibration (E14), descriptive not causal (E15) |
| Failed and inconclusive findings identified | yes, provided the captions follow `figure_manifest.csv` (`caption_caveats`) |
| Colour-blind accessibility | E01-E13 use matplotlib defaults (tab10 blue/orange/green/red); a red-green pair occurs in E12 power and a red-orange pair in E06 detectability (grey/blue/orange/red by amplitude). Use the cividis/viridis or blue-orange scheme of Figs. 4-7 during regeneration. E14 and E15 are compliant |
| Vector versions | SVG for all 23; PDF committed for E14 and E15 only |
