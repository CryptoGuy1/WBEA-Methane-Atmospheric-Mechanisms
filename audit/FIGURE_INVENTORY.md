# Figure and table inventory for the EMS manuscript (final audit)
Experiment figures are committed as SVG/PNG; PDFs are gitignored outside `manuscript/` but regenerate from each experiment's script. All Results figures were made in development style and **must be re-rendered in manuscript style**: 174.5 mm, no internal titles, labelled panels allowed in Results. That is a presentation task using saved results only.

## Main text
| Proposed | Content | Source (branch: path) | Status |
|---|---|---|---|
| Fig. 1 | Study area and network (3 maps, 21 pairs) | manuscript: `manuscript/figures/section2/fig01_wbea_network.*` | Final |
| Fig. 2 | CH4 availability (monthly/daily 2021-2025; daily 2026) | manuscript: `manuscript/figures/section2/fig02_ch4_availability.*` | Final |
| Fig. 3 | Framework / workflow (development -> freeze -> confirmation -> post-confirmation) | to be drawn | **Missing** (schematic) |
| Fig. 4 | H1: stability association and robustness | main: `experiments/E04_stability_elasticity/figures/figure04_*`, `figure05_*` | Re-render |
| Fig. 5 | H2: directional coupling by pair, stability strata | main: `experiments/E05_directional_coupling/figures/figure06_*` | Re-render |
| Fig. 6 | Detection limits and lag kernel (including the failed criterion) | main: `experiments/E06_detectability_kernel/figures/figure07_kernel_shape.*` (+ `figureS2_detectability`) | Re-render |
| Fig. 7 | H3 composition decomposition | main: `experiments/E07_composition_decomposition/figures/figure09_*` | Re-render |
| Fig. 8 | **Development vs confirmation estimates (H1-H3)** | values in `experiments/E08_confirmation/confirmation_2026/development_vs_confirmation.csv` | **Missing figure** (E08 produced no figure) |
| Fig. 9 | Validation of the H2 reference: E12 null rates and falsification; E13 seasonal reference distributions | e12: `.../figures/e12_null_rejection_rates.*`; e13: `.../figures/e13_fig1_reference_distributions.*` | Re-render as one labelled figure |
| Table 1 | Station characteristics | manuscript: `manuscript/tables/section2/table01_station_characteristics.tex` | Final |
| Table 2 | Datasets and temporal design | manuscript: `manuscript/tables/section2/table02_data_sources_temporal_design.tex` | Final |
| Table 3 | Registered confirmation | audit: `audit/manuscript_tables/table03_registered_confirmation.tex` | Ready (CAS 0 overfull) |
| Table 4 | Validation and sensitivity | audit: `audit/manuscript_tables/table04_validation_sensitivity.tex` | Ready (CAS 0 overfull) |

## Supplementary Material
| Item | Source |
|---|---|
| Network geometry; data quality and gap timing | main: E01 `figure01_*`, E02 `figure02_*` |
| Excursion phenotype; correlation by stability; episode-definition sensitivity | main: E03 `figure03_*`, `figureS1_*`, `figureS4_*` |
| H2 residualisation sensitivity | main: E05 `figure08_*` |
| Detectability by injection | main: E06 `figureS2_*` |
| H3 baseline comparison | main: E07 `figureS3_*` |
| Elevated-wind transit (inconclusive) | main: E09 `e09_centroids_by_wind`, `e09_r1_centroids` |
| Episode typology (not supported) | main: E10 `e10_typology` |
| E12 p-value CDFs, D distributions, power | e12: `e12_null_pvalue_cdf_and_D`, `e12_power` |
| E13 per-quarter reference distributions | e13: `e13_fig2_per_season` |
| Table S: negative, failed and inconclusive findings | audit: `audit/manuscript_tables/tableS_negative_inconclusive.tex` |
| Table S: H1 negative-control covariance by period | main: `experiments/E08_post_confirmation_exploratory/results/h1_nc_covariance_by_period.csv` |
| Table S: H3 denominator by station | main: `experiments/E08_post_confirmation_exploratory/results/h3_2026_denominator_by_station.csv` |
