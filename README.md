# A Falsification-Oriented Framework for Atmospheric Stability and Wind-Conditioned Methane Dependence in Monitoring Networks

This repository contains the analysis code, frozen confirmation protocol, archived results and reproducibility records for a study of hourly methane (CH₄) observations from the Wood Buffalo Environmental Association (WBEA) monitoring network in the Athabasca oil sands region of Alberta, Canada.

The study evaluates three statistical questions:
- **Stability:** whether methane anomalies are associated with near-surface atmospheric stability.
- **Directional dependence:** whether station pairs show wind-conditioned directional dependence.
- **Weather regimes:** whether changes in meteorological-regime frequency account for year-to-year changes in methane excursions.

Its methodological contribution is to separate three kinds of evidence that are often conflated:
1. **Independent temporal confirmation:** pre-specified tests applied once to held-out data.
2. **Statistical-null calibration:** whether the test behaves as intended when no effect is present.
3. **Physical-specificity testing:** whether a positive result could arise without the mechanism it suggests.

> **Scope.** All results are statistical associations in monitoring data. They are not emission estimates, source attributions, or evidence that methane travelled between stations.

## Contents
- [Study at a glance](#study-at-a-glance)
- [Main findings](#main-findings)
- [Research workflow](#research-workflow)
- [Repository navigation](#repository-navigation)
- [Reproducibility and installation](#reproducibility-and-installation)
- [Data availability and provenance](#data-availability-and-provenance)
- [Experiment index](#experiment-index)
- [Archived versions and safeguards](#archived-versions-and-safeguards)
- [Citation and licence](#citation-and-licence)

---

## Study at a glance

| | Question | Estimator |
|---|---|---|
| **H1** | Is network methane higher when the near-surface atmosphere is more stable? | Adjusted regression of the network CH₄ anomaly on the AMS 5 tower temperature gradient (T₉₀ − T₂₀) |
| **H2** | Do nearby station pairs show lead-lag asymmetry that depends on wind direction along the pair? | Pooled lagged-correlation contrast D (aligned vs reversed winds), tested against shifted-wind surrogates |
| **H3** | How much of the year-to-year change in excursion frequency reflects changing weather regimes? | Projection share from a regime-composition decomposition |

**Data periods:**
- **Development (2021–2025):** exploratory; methods were built and tested on these data.
- **Independent confirmation (January–September 2026):** the protocol and code were frozen before these data were opened, then applied once.
- **Post-confirmation diagnostics:** synthetic calibration, physical-specificity falsification and sensitivity analyses. These are exploratory and cannot alter the registered decisions.

---

## Main findings

### Registered confirmation, January–September 2026 (frozen protocol, run once)

| Hypothesis | Estimate | 95% CI / test | Registered decision |
|---|---|---|---|
| H1 Stability association | 0.052 ppm per reference SD | 0.039 to 0.069 | Confirmed |
| H2 Wind-conditioned directional dependence | pooled D = 0.288 | finite-shift p = 1/247 ≈ 0.0040 (minimum attainable) | Registered criteria met |
| H3 Regime composition | share = 0.011 | −0.020 to 0.043 | Not confirmed |

Source: [`e08_results.json`](experiments/E08_confirmation/confirmation_2026/e08_results.json) at tag [`e08-confirmation`](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/e08-confirmation).

### Essential limitations
- **H1:** the 2026 next-day negative control was nonzero (−0.019; 95% CI −0.027 to −0.005). It did not breach the registered decision rule but remains unexplained.
- **H2 calibration:** under constructed seasonal confounding, the whole-period shifted-wind test rejected in 23.8% of simulations rather than about 5%. Calibration across four null scenarios was classified as inconclusive.
- **H2 physical specificity:** a wind-advected shared driver with no inter-station methane transfer produced directional dependence and was detected in 200 of 200 simulations. A positive H2 result is therefore statistical directionality, not evidence of methane transport.
- **H3:** one station (AMS 18) contributed 92.9% of the estimator's weight in 2026.
- **Development criterion:** the pre-registered quantitative lag-kernel criterion failed during development (1 of 5 transit classes in range; 4 required).
- **Network:** AMS 2 was excluded from the 2026 analysis under the pre-specified coverage rule (41.2% valid methane hours).

Confirmation of a statistical pattern, limited calibration under a chosen reference, and the absence of physical attribution are compatible conclusions; the study reports all three.

---

## Research workflow

```text
1. Exploratory development (2021–2025)
   Methods built and tested; development gates, failures and decisions logged.
                         │
                         ▼
2. Protocol freeze ──► Independent confirmation (Jan–Sep 2026)
   Code and rules frozen     Frozen H1–H3 procedures applied once to held-out data
   before 2026 data opened   → registered decisions
                         │
                         ▼
3. Post-confirmation diagnostics
   Synthetic calibration and falsification, season-restricted references,
   cross-year negative controls, matched-pair comparability (decisions unchanged)
```

**Key records:**
- **Frozen protocol:** [`PROTOCOL_E08_DRAFT_v2.md` at `protocol-freeze`](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/blob/protocol-freeze/PROTOCOL_E08_DRAFT_v2.md)
- **Freeze record:** [`FREEZE_RECORD.md`](experiments/E08_confirmation/FREEZE_RECORD.md)
- **Confirmation results:** [`confirmation_2026/`](experiments/E08_confirmation/confirmation_2026)
- **Post-confirmation evidence:** see the [experiment index](#experiment-index).
- **Methods figure:** a workflow flowchart prepared for publication is available on the publication branch: [`fig03_flowchart.pdf`](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/blob/publication/supplementary-assets/publication/fig03_methods/fig03_flowchart.pdf).

---

## Repository navigation

| Resource | Location |
|---|---|
| Registered confirmation protocol | [`PROTOCOL_E08_DRAFT_v2.md`](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/blob/protocol-freeze/PROTOCOL_E08_DRAFT_v2.md) (authoritative at tag `protocol-freeze`) |
| Confirmation results | [`experiments/E08_confirmation/confirmation_2026/`](experiments/E08_confirmation/confirmation_2026) |
| Core analysis code | [`src/wbea/`](src/wbea) |
| Data-processing scripts | [`src/build/`](src/build) |
| Parameters, seeds and frozen rules | [`config/project.toml`](config/project.toml) |
| Tests | [`tests/`](tests) and each experiment's `tests/` folder |
| Reproducibility manifests (SHA-256) | [`manifests/`](manifests) |
| Synthetic calibration and falsification | [`experiments/E12_h2_synthetic_null_calibration/`](experiments/E12_h2_synthetic_null_calibration) |
| Sensitivity analyses | [E13](experiments/E13_h2_seasonal_shift_sensitivity) (on `main`); [E14](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/research/e14-h2-empirical-yearswap-null/experiments/E14_h2_empirical_yearswap_null) and [E15](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/research/e15-h2-matched-pair-comparability/experiments/E15_h2_matched_pair_comparability) (on their branches) |
| Supplementary figures, tables and manifests | [`publication/supplementary/`](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/publication/supplementary-assets/publication/supplementary) (branch `publication/supplementary-assets`) |
| Main-text figures | [`manuscript/figures/`](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/manuscript/section2-figures-tables/manuscript/figures) (branch `manuscript/section2-figures-tables`) |
| Experiment reports | `experiments/<ID>/REPORT.md` (see the [experiment index](#experiment-index)) |
| Research decision history | [`DECISION_LOG.md`](DECISION_LOG.md); review records in [`reviews/`](reviews) and [`REVIEW_BACKLOG.md`](REVIEW_BACKLOG.md) |
| Final experimental audit | [`audit/`](audit) |

---

## Reproducibility and installation

**Environment.** The archived confirmation run used Python 3.12.3. Package versions are pinned in [`requirements.txt`](requirements.txt).

```bash
git clone https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms.git
cd WBEA-Methane-Atmospheric-Mechanisms
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

> **Viewing is not reproducing.** Checking out a tag (for example `git checkout e08-confirmation`) gives the exact archived code and outputs. It does not re-execute any analysis, and re-execution needs the restricted WBEA data described below. Frozen records should be inspected, not modified.

### Level 1: Inspect archived outputs (no restricted data)
Every experiment's saved results, figures and reports are in the repository and can be read directly. Their integrity can be checked against the checksum files (for example [`confirmation_2026/SHA256SUMS.txt`](experiments/E08_confirmation/confirmation_2026/SHA256SUMS.txt) and the manifests in [`manifests/`](manifests)).

### Level 2: Run tests
Tested on a clean copy of `main` with no WBEA data present:

| Test suite | Without WBEA data |
|---|---|
| `tests/` | 35 pass; 4 fail because they require the development panel or raw exports |
| `experiments/E12_h2_synthetic_null_calibration/tests` | 7 pass |
| `experiments/E13_h2_seasonal_shift_sensitivity/tests` | 4 pass; 2 skip (sealed 2026 panel absent) |

```bash
python -m pytest -q tests experiments/E12_h2_synthetic_null_calibration/tests experiments/E13_h2_seasonal_shift_sensitivity/tests
```

### Level 3: Reproduce development analyses (authorised data required)
1. Obtain the WBEA hourly exports and ERA5 file listed in [`DATA_PROVENANCE.md`](DATA_PROVENANCE.md), and verify them against [`manifests/`](manifests).
2. Build the development panel with [`src/build/build_dev_panel.py`](src/build/build_dev_panel.py), then verify it against [`manifests/dev_panel_SHA256SUMS.txt`](manifests/dev_panel_SHA256SUMS.txt).
3. Run an experiment, for example `python experiments/E04_stability_elasticity/run_e04.py`, and compare its outputs with the archived `results/`.

**Note:** the builders and `config/project.toml` contain absolute input paths from the original analysis environment. Point them at your local copies before running.

### Level 4: Frozen independent confirmation
- **Archived record:** the frozen implementation is at tag [`protocol-freeze`](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/protocol-freeze); the single registered run and its outputs are at tag [`e08-confirmation`](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/e08-confirmation).
- **What a genuine rerun needs:**
  - authorised 2026 WBEA data, processed by [`src/build/build_e08_panel.py`](src/build/build_e08_panel.py);
  - the development panel (reference quantities come from 2021–2023);
  - the pinned environment.
- **Guard:** [`run_e08.py`](experiments/E08_confirmation/run_e08.py) runs in confirm mode only from the `protocol-freeze` commit on a clean working tree. A dry-run mode applies the same methods to 2025 development data.

A rerun is a verification of the archived result, not a new confirmation.

### Level 5: Synthetic post-confirmation experiments (no restricted methane data)
The synthetic calibration experiment ([E12](experiments/E12_h2_synthetic_null_calibration)) generates its own data from committed parameter files (`synthetic_params.json`, `p1_amplitudes.json`) and station coordinates. Its entry point runs without WBEA data:

```bash
cd experiments/E12_h2_synthetic_null_calibration
python run_e12.py --help
```

The parameters were originally estimated from development data (`estimate_params_from_development.py`); re-estimating them requires the development panel. The full production run is computationally intensive and was not re-executed when this README was written.

---

## Data availability and provenance

- **Not redistributed.** WBEA hourly observations are not included in this repository and must be obtained from WBEA ([continuous monitoring data](https://wbea.org/data/continuous-monitoring-data/)), subject to its conditions. Derived summaries and scripts do not grant permission to redistribute the observations.
- **Provenance.** Sources, export dates and archive checksums are recorded in [`DATA_PROVENANCE.md`](DATA_PROVENANCE.md) and [`manifests/`](manifests).
- **Auxiliary data:**
  - ERA5 reanalysis (Copernicus Climate Data Store): 100 m winds and boundary-layer height for specific analyses.
  - NASA FIRMS VIIRS active-fire detections: a wildfire sensitivity flag.
- **2026 data status.** The 2026 observations are WBEA monthly validated records and remain subject to WBEA's annual validation.
- **Data seal.** Confirmation-period data were kept separate from development work under [`SEALED_DATA_POLICY.md`](SEALED_DATA_POLICY.md): designated builders, a code test that fails if development scripts reference sealed paths, and recorded checksums. The seal is procedural and code-enforced, not cryptographic.

---

## Experiment index

### Development and feasibility (2021–2025, exploratory)

| ID | Topic | Outcome | Report |
|---|---|---|---|
| E00 | Feasibility | Archived | [report](experiments/E00_feasibility_v2/REPORT.md) |
| R1 | Readiness checks | Complete | [report](experiments/R1_readiness/REPORT.md) |
| E01 | Network geometry and instrumentation | 66 pairs; 27 within 30 km form the H2 family | [report](experiments/E01_geometry_instrumentation/REPORT.md) |
| E02 | Data quality and missingness | Methane 90.6–94.2% valid per station | [report](experiments/E02_data_quality/REPORT.md) |
| E03 | Excursion patterns | Night and winter peaks; co-excursion declines with distance | [report](experiments/E03_excursion_patterns/REPORT.md) |
| E04 | H1 stability association | 0.0475 ppm/SD (0.0411–0.0520); development gate passed | [report](experiments/E04_stability_elasticity/REPORT.md) |
| E05 | H2 directional dependence | D = 0.1285 (0.1084–0.1553); development gate passed | [report](experiments/E05_directional_coupling/REPORT.md) |
| E06 | Detectability and lag kernel | **Kernel criterion failed** | [report](experiments/E06_detectability_kernel/REPORT.md) |
| E07 | H3 composition | **Not supported** (0.027; −0.040 to 0.126) | [report](experiments/E07_composition_decomposition/REPORT.md) |
| E09 | Alternative-height (ERA5 100 m) wind | **Inconclusive** | [report](experiments/E09_elevated_wind/REPORT.md) |
| E10 | Episode typology | **Not supported** (placebo criterion failed) | [report](experiments/E10_episode_typology/REPORT.md) |
| E11 | Station contributions | No single station drives H1 or H2 | [report](experiments/E11_station_contribution/REPORT.md) |
| PRE_E08 | Pre-confirmation benchmarks | Complete | [report](experiments/PRE_E08/REPORT.md) |

### Frozen confirmation (January–September 2026, registered)

| ID | Topic | Outcome | Record |
|---|---|---|---|
| E08 | H1–H3 confirmation | H1 confirmed; H2 registered criteria met; H3 not confirmed | [results](experiments/E08_confirmation/confirmation_2026); [freeze record](experiments/E08_confirmation/FREEZE_RECORD.md) |

### Post-confirmation diagnostics (exploratory; registered decisions unchanged)

| ID | Topic | Outcome | Report |
|---|---|---|---|
| E08 post | H1 negative-control and H3 weighting diagnostics | Covariance explanation not supported; AMS 18 dominance | [readme](experiments/E08_post_confirmation_exploratory/README.md) |
| E12 | Synthetic calibration and falsification | Null calibration inconclusive; seasonal confounding inflates rejection; advected driver detected | [report](experiments/E12_h2_synthetic_null_calibration/REPORT_FOR_MANUSCRIPT_AI.md) |
| E13 | Season-restricted shift references | Observed D exceeded all 63 and all 93 surrogates (sensitivity only) | [report](experiments/E13_h2_seasonal_shift_sensitivity/E13_REPORT_FOR_MANUSCRIPT_AI.md) |
| E14 | Cross-year empirical negative controls | 1/20, 2/20 and 0/20 rejections; dependent, descriptive | [report](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/blob/research/e14-h2-empirical-yearswap-null/experiments/E14_h2_empirical_yearswap_null/REPORT.md) (branch) |
| E15 | Matched-pair comparability | Development–2026 gap not explained by pairs, window or reference; weight-sensitive | [report](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/blob/research/e15-h2-matched-pair-comparability/experiments/E15_h2_matched_pair_comparability/REPORT.md) (branch) |

---

## Archived versions and safeguards

| Reference | Role |
|---|---|
| [`protocol-freeze`](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/protocol-freeze) | Code, configuration and protocol frozen before the 2026 data were opened |
| [`e08-confirmation`](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/e08-confirmation) | The single registered confirmation run and its outputs |
| Development tags (`e00-feasibility` … `e11-x3`) | Milestones of the development experiments, including failed and unsupported outcomes |
| [`e12-null-calibration`](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/e12-null-calibration), [`e13-seasonal-reference-sensitivity`](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/e13-seasonal-reference-sensitivity), [`e14-crossyear-negative-control`](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/e14-crossyear-negative-control), [`e15-matched-pair-comparability`](https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/e15-matched-pair-comparability) | Archived states of the post-confirmation experiments |
| SHA-256 manifests | Checksums of raw archives, derived panels and frozen outputs, recorded in [`manifests/`](manifests) and per-experiment manifest files |

Post-confirmation work (E14, E15 and the publication assets) is developed on separate branches and has not been merged into `main`.

---

## Citation and licence

**Citation.** The associated manuscript is in preparation and has not been published. A formal citation will be added when a publication record is available. Until then, please cite this repository by its URL and the specific tag or commit used.

**Licence.** No licence has been granted for this repository. A proposed MIT licence for `software/netmech` is marked as pending approval and not in force.
