# Supplement evidence audit
**Scope:** provenance, figure and table inventory, and evidence verification for one integrated Supplementary Information document (EMS).
**Nature:** non-mutating audit: no experiment, result, frozen file, manuscript file or bibliography was changed.
**Location:** branch `publication/supplement-evidence-audit`, created from the E15 head `1788301`.
**Sources:** `SOURCE_SNAPSHOT.md`.

## 1. Summary
- **Figures:** 23 distinct experiment figures (E01-E07, E09, E10, E12-E15; none in E08, E11, post-confirmation folders or the audit branch). All are accounted for and assigned provisional numbers S1-S23. A separate category, the publication figures on the manuscript branch (Figs. 1-7, regime heatmap and archived versions), is inventoried in section 4 and not counted among the 23.
- **Corrections needed:** 21 of 23 figures need regeneration in publication style.
  - 9 have content or labelling corrections that matter scientifically (`FIGURE_QA_REPORT.md`), including one superseded model (E06 detectability) and one rounding mismatch (E05, 0.129 vs 0.1285).
  - E14 and E15 are publication-ready.
- **Tables:** 14 candidate supplementary tables, all with existing authoritative sources.
- **Evidence:** 30 key numerical findings were re-read from their authoritative files and all agree (`evidence_manifest.csv`).
- **Discrepancies:** 7 documentation-implementation discrepancies, none affecting a registered decision (`REPRODUCIBILITY_GAPS.md` section D), including two protocol descriptive outputs that E08 never produced.
- **Branches:** GitHub `main` now holds E12, E13 and the audit (PRs #1 and #2), but not E14, E15 or the manuscript figures, so no single branch is a complete publication source.
- **Readiness:** the evidence package is **ready for scientific writing of the Supplement text**, with the open items in section 9 tracked. Building the final Supplement *files* additionally requires figure regeneration and a branch-integration decision.

## 2. Experiment-by-experiment provenance
All values verified against the files listed (branch `research/e15-h2-matched-pair-comparability` unless stated).

| Exp. | Question | Period / status | Primary result (verified) | Outcome | Authoritative source | Figures |
|---|---|---|---|---|---|---|
| E01 | Network geometry, instrumentation, H2 pair family | 2021-2025, development | 66 station pairs; 27 within 30 km form the H2 family | descriptive | `E01.../results/pairwise_geometry.csv`, `h2_family_eligibility.csv` | S1 |
| E02 | Data quality, missingness timing | development | CH4 valid 90.6-94.2% per station; zero/span code concentrated at hours ending 01-06 | descriptive; code meanings OPEN | `E02.../results/q1_...csv`, `q2_monthly_completeness.csv` | S2 |
| E03 | Excursion structure | development | lift vs distance Spearman -0.821 (-0.861 to -0.730); core-only -0.642 | descriptive | `E03.../results/addendum_distance_dependence_uncertainty.csv` | S3-S5 |
| E04 | H1 stability association | development (gate) | 0.04752 ppm/SD (0.0411-0.0520); next-day control -0.00004 | gate passed | `E04.../results/h1_estimates.csv` | S6, S7 |
| E05 | H2 directional coupling | development (gate) | pooled D 0.1285 (0.1084-0.1553); 21/27 family-wise | gate passed | `E05.../results/h2_pooled.csv`, `h2_pair_statistics.csv` | S8, S9 |
| E06 | Detectability and lag kernel | development | 1/5 bins inside reference (4 required); continuous-source detection 83% (A = 0.4, 180 min) | **kernel criterion FAILED** | `E06.../results/e06_observed_vs_reference_kernel.csv`, `review_continuous_detectability.csv` | S10, S11 |
| E07 | H3 regime composition | development | share 0.0269 (-0.0396 to 0.1264); Jan-Sep 0.0261 | **NOT SUPPORTED** | `E07.../results/h3_sensitivity.csv`; `PRE_E08/results/h3_jan_sep_benchmark.csv` | S15, S16 |
| E08 | Registered confirmation | Jan-Sep 2026 | H1 0.05204 (0.0391-0.0695), **confirmed**; next-day -0.01872 (-0.0268 to -0.0051), unexplained. H2 D 0.2879317085, p = 1/247, **confirmed**. H3 0.0110 (-0.0199 to 0.0428), **not confirmed** | registered | `E08_confirmation/confirmation_2026/e08_results.json` (tag `e08-confirmation`) | none |
| E08-PC | H1/H3 post-confirmation diagnostics | post-confirmation | 2026 corr(S, S+24) 0.146 (development range); AMS 18 = 92.93% of H3 denominator (development 39.05%) | exploratory | `E08_post_confirmation_exploratory/results/*` | none (tables) |
| E09 | Elevated-wind transit | development | Delta SSE 0.294 (-0.122 to 0.741) (r1) | **INCONCLUSIVE** | `E09.../results/r1_decision.csv` | S12, S13 |
| E10 | Episode typology | development | wind-shift placebo 0.122 vs 95th percentile 0.148 | **NOT SUPPORTED** | `E10.../results/e10_decision.csv` | S14 |
| E11 | Station contributions | development | H1 leave-one-core-station-out 0.0432-0.0572; H2 leave-one-station-out 0.1206-0.1432 | descriptive | `E11.../results/x3_*` | none |
| F5 | Regime at excursion onset | development / 2026 descriptive | stable low-wind enrichment 2.728 (2.531-2.939) | descriptive | `PRE_E08/results/f5_dev_regime_distribution_pooled.csv` | none (heatmap is a manuscript figure) |
| E12 | Synthetic calibration and falsification | post-confirmation | nulls 4.6/5.4/4.8/4.6% (**inconclusive** overall); seasonal confounding 23.8%; advected driver 100%; 3 h lag power 0% | exploratory | `E12.../results/summary_by_scenario_method.csv`, `verdicts.json` | S17-S19 |
| E13 | Season-restricted references | post-confirmation | 0/63 (quarters), 0/93 (Jan-Apr/May-Sep) surrogates >= observed | exploratory (strengthens robustness to reference only) | `E13.../results/e13_summary.csv` | S20, S21 |
| E14 | Cross-year negative control | post-confirmation | 1/20, 2/20, 0/20 rejections (frozen rule) | exploratory; **not** calibration | `E14.../results/summary.csv`, `replicates.csv` | S22 |
| E15 | Matched-pair comparability | post-confirmation | non-period steps +0.009; period +0.150 among the same 21 pairs; equal-weight gap 0.086 | descriptive | `E15.../results/comparison_table.csv`, `weight_sensitivity.csv` | S23 |

**Scientific safeguards preserved in all manifests and captions:**
- **H1:** confirmed, with the unexplained negative-control anomaly reported.
- **H2:** confirmed statistically, with no transport or emission inference.
- **E06:** kernel failure retained; the ordering rule is not kernel agreement.
- **E09:** inconclusive. **E10:** not supported.
- **H3:** not confirmed, with the AMS 18 weighting retained.
- **E12:** nulls, confounding, resolution, power and falsification are kept distinct; the advected driver is not a Type-I error.
- **E13:** sensitivity only.
- **E14:** dependent cross-year negative controls; 1/20, 2/20 and 0/20 retained without a calibration claim.
- **E15:** descriptive, not causal; dependent pairs and weights.

## 3. Figure inventory
`figure_manifest.csv` holds one row per figure, with path, branch, commit, formats, PNG size and dpi, SVG SHA-256, generating script, status, supersession, conclusion, caption caveats, placement, caption outline and required corrections.

| S | Figure (experiment) | Section | Status | Placement |
|---|---|---|---|---|
| S1 | figure01_network_geometry (E01) | S1 | dev | Supplement (wind roses unique) |
| S2 | figure02_coverage_and_gap_timing (E02) | S1 | dev | Supplement (panel b unique) |
| S3 | figure03_excursion_phenotype (E03) | S2 | dev | Supplement |
| S4 | figureS4_episode_definition_sensitivity (E03) | S2 | dev | Supplement |
| S5 | figureS1_network_correlation_by_stability (E03) | S2 | dev | Supplement |
| S6 | figure04_stability_elasticity (E04) | S3 | dev | archival reproduction (RF panel unique) |
| S7 | figure05_h1_robustness (E04) | S3 | dev | Supplement |
| S8 | figure06_directional_coupling (E05) | S4 | dev | archival reproduction |
| S9 | figure08_residualisation_sensitivity (E05) | S4 | dev | Supplement |
| S10 | figure07_kernel_shape (E06) | S5 | dev | Supplement (lag profiles unique) |
| S11 | figureS2_detectability (E06) | S5 | dev | after regeneration (superseded model) |
| S12 | e09_centroids_by_wind (E09) | S5 | dev | Supplement (may combine with S13) |
| S13 | e09_r1_centroids (E09) | S5 | dev | Supplement |
| S14 | e10_typology (E10) | S5 | dev | Supplement |
| S15 | figure09_composition_decomposition (E07) | S6 | dev | Supplement |
| S16 | figureS3_baseline_comparison (E07) | S6 | dev | Supplement |
| S17 | e12_null_rejection_rates (E12) | S8 | post-confirmation | archival reproduction |
| S18 | e12_null_pvalue_cdf_and_D (E12) | S8 | post-confirmation | Supplement |
| S19 | e12_power (E12) | S8 | post-confirmation | archival reproduction |
| S20 | e13_fig1_reference_distributions (E13) | S9 | post-confirmation | Supplement |
| S21 | e13_fig2_per_season (E13) | S9 | post-confirmation | Supplement |
| S22 | e14_yearswap_null (E14) | S9 | post-confirmation | Supplement (ready) |
| S23 | e15_comparability (E15) | S9 | post-confirmation | Supplement (ready) |

"Archival reproduction" marks figures whose content a manuscript-branch figure redraws. Whether those manuscript figures are in the current Overleaf version is **UNVERIFIED**.

## 4. Publication figures on the manuscript branch (separate from the 23)
- **Current:** `fig01_wbea_network`, `fig02_ch4_availability`, `fig03_framework` (v3, equation-led; the researcher later adopted an externally produced framework graphic: Overleaf status UNVERIFIED), `fig04_stability_results`, `fig05_directional_coupling_results`, `fig06_meteorological_composition`, `fig07_h2_calibration_falsification`, `fig_meteorological_regime_heatmap`.
- **Archived:** earlier versions in `archive_*` folders.
- **Not candidates for the Supplement**, except where the Supplement reuses a figure deliberately.

## 5. Table inventory
`table_manifest.csv` covers 14 candidate tables:
- TS1 completeness;
- TS2 pairs and eligibility;
- TS3 episode sensitivity (combine or archive);
- TS4 H1 development estimates;
- TS5 H2 development pairs;
- TS6 transport diagnostics (combined failed/inconclusive/unsupported results);
- TS7 H3 development;
- TS8 E08 full statistics;
- TS9 2026 H2 pairs with max-T;
- TS10 post-confirmation H1/H3 diagnostics;
- TS11 E12 all scenarios;
- TS12 E13;
- TS13 E14 all combinations;
- TS14 E15 comparisons and shared pairs.

Not proposed as tables: intermediate CSVs (null matrices, surrogate lists, bootstrap draws). These remain archival in the repository.

**Limitations that each table must carry:**
- **TS9:** no 2026 pair CIs exist.
- **TS11:** the falsification scenario must be labelled as such.
- **TS13:** dependent combinations; nominal intervals.
- **TS14:** A6 not evaluable; descriptive weights.
- **TS7:** relabel the Manski rows; mark the deweathering baseline as unvalidated.

## 6. Supplement structure
See `SUPPLEMENT_OUTLINE.md`. The provisional ten sections are retained with three adjustments:
1. E10 moves to S5;
2. S7 is table-only;
3. the post-confirmation H2 analyses (E13-E15) are merged into S9, and S10 becomes software, reproducibility and data availability.

**Estimated length:** about 30-40 pages, with S5 and S9 the largest.

## 7. Proposed publication directory (to be created at the writing stage; not created now)
```
publication/supplementary/
  README.md                  provenance, build instructions, data restrictions
  supplementary.tex          (future)  + supplementary.pdf (future)
  figures/                   S1-S23: regenerated PDF (vector) + 600 dpi PNG; generating scripts reference experiment results by path
  tables/                    TS1-TS14 LaTeX sources generated from authoritative CSVs (scripts, not copies)
  figure_manifest.csv  table_manifest.csv  evidence_manifest.csv   (carried forward from this audit)
  scripts/                   regeneration scripts reading experiments/*/results only
```
- **Original experiment files** remain untouched.
- **No WBEA raw or derived hourly data** are copied. Figures that need hourly data (e.g. main Fig. 4a residuals) document the dependency instead.
- **Every publication file** records its source path and commit.

## 8. Quality-control results
| Check | Result |
|---|---|
| All distinct experiment figures accounted for | **23/23** |
| Formats grouped correctly | SVG+PNG (E01-E13), PDF+SVG+PNG (E14, E15) |
| Missing figures in the plan | none |
| Duplicate supplementary numbers | none (asserted) |
| Confidence intervals | only saved intervals are referenced; absent intervals stated explicitly (2026 pair CIs, per-bin centroids, joint contemporaneous CI) |
| Significance statements | only registered decisions or saved classifications; no new claims |
| Development vs confirmation labels | explicit in every manifest row (`experiment_status`) |
| Negative / inconclusive results identified | E06 failed; E07 and E10 not supported; E09 inconclusive; H3 not confirmed; E12 calibration inconclusive; E14 not calibration; E15 A6 not evaluable |
| E14 and E15 in the source branch | yes (E15 branch) |
| Frozen confirmation unchanged | yes (0-line diffs vs tags) |
| Numbers checked against artifacts | 30/30 evidence values re-read |
| Regression tests | 70 passed |

## 9. Open items before or during writing
These are **OPEN** and must not be guessed (detail in `REPRODUCIBILITY_GAPS.md`):
1. Branch integration, which requires researcher authorisation.
2. The current Overleaf manuscript content (duplication status UNVERIFIED).
3. The redistribution decision for the Fig. 4a residual file, and the repository's public visibility.
4. WBEA missing-code meanings.
5. The AMS 2 outage cause.
6. Station relocations.
7. Final 2026 validation and the pre-declared re-run.
8. The `netmech` licence.
9. The decision on regenerating or relabelling S11.

## 10. Recommendation
**Proceed to writing the Supplement text.** The evidence base is complete, internally consistent and verified. The writers should:
- use `evidence_manifest.csv` values only;
- follow the caption caveats in `figure_manifest.csv`;
- disclose the protocol descriptive-output gaps in S7.

Figure regeneration (publication style, label corrections, S11 model) and branch integration should be completed before the Supplement PDF is built.
