# WBEA Methane Atmospheric Mechanisms

**A falsification-tested framework for atmospheric stability and directional methane coupling in environmental monitoring networks.**

This repository contains the complete, version-controlled research record behind a study of hourly methane observations from the Wood Buffalo Environmental Association (WBEA) monitoring network in the Athabasca oil sands region of Alberta, Canada. It holds the analysis code, the frozen confirmation protocol, every experiment's saved results and reports, and the publication assets for the manuscript prepared for *Environmental Modelling & Software*.

> **What this study does and does not claim.** The analyses test *statistical associations* in monitoring data. They do not estimate emissions, attribute sources, or prove that methane travelled between stations.

---

## Contents
1. [Study design in one minute](#study-design-in-one-minute)
2. [Main results](#main-results)
3. [How to navigate the repository](#how-to-navigate-the-repository)
4. [Branches and tags](#branches-and-tags)
5. [Experiment index](#experiment-index)
6. [Repository layout](#repository-layout)
7. [Reproducing the analyses](#reproducing-the-analyses)
8. [Data access and integrity safeguards](#data-access-and-integrity-safeguards)
9. [Authors and contact](#authors-and-contact)

---

## Study design in one minute

The study tests three pre-specified hypotheses on a 12-station network:

| | Hypothesis | Question |
|---|---|---|
| **H1** | Stability association | Are network methane anomalies higher when the near-surface atmosphere is more stable (AMS 5 tower temperature gradient)? |
| **H2** | Directional coupling | After removing regional variation, do nearby station pairs show a lead-lag asymmetry that depends on whether the wind blows along or against the pair? |
| **H3** | Regime composition | How much of the year-to-year change in methane excursion frequency is associated with changes in how often meteorological regimes occur? |

The work proceeded in three strictly separated stages:

1. **Development (2021-2025, exploratory).** Methods were built and tested on five years of data (experiments E00-E11).
2. **Frozen confirmation (January-September 2026).** The protocol and code were frozen and tagged *before* the 2026 data were opened, then run once (experiment E08).
3. **Post-confirmation diagnostics.** Additional analyses examine how far the directional statistic can be trusted and compared (experiments E12-E15). They are labelled exploratory and cannot change the registered decisions.

---

## Main results

### Registered 2026 confirmation (frozen protocol, run once)

| Hypothesis | Estimate (95% interval) | Registered decision |
|---|---|---|
| H1 stability association | 0.052 ppm per SD of stability (0.039 to 0.069), 4,472 hours | **Confirmed** |
| H2 directional coupling | pooled D = 0.288, finite shifted-wind p = 1/247 (the smallest possible), 21 station pairs | **Confirmed** |
| H3 regime composition | share = 0.011 (-0.020 to 0.043), 55 contrasts | **Not confirmed** |

Important qualifications, reported with the results rather than hidden:
- **H1:** the next-day negative control was unexpectedly negative in 2026 (-0.019; -0.027 to -0.005). It did not breach the registered decision rule, but it remains unexplained.
- **H2:** synthetic tests show the statistic also responds to a wind-carried shared driver *without* any station-to-station methane transfer. A positive H2 result is therefore statistical directionality, not proof of transport.
- **H3:** one station (AMS 18) supplied 92.9% of the estimator's weight in 2026.
- **Network:** AMS 2 was excluded in 2026 (41.2% valid methane hours), leaving 11 stations.

### Development and diagnostic findings (exploratory)

| Finding | Outcome |
|---|---|
| H1 in development | 0.0475 ppm/SD (0.0411 to 0.0520); positive in every year, season and station-exclusion check |
| H2 in development | pooled D = 0.1285 (0.1084 to 0.1553); 21 of 27 pairs family-wise significant |
| Pre-registered lag-kernel criterion | **Failed** (1 of 5 transit classes in range; 4 required) |
| H3 in development | **Not supported** (0.027; -0.040 to 0.126) |
| ERA5 100 m vs 10 m wind transit | **Inconclusive** |
| Episode typology | **Not supported** (placebo criterion failed) |
| Synthetic null calibration of H2 | Null rejection 4.6-5.4% (overall **inconclusive** by the pre-set precision rule); a constructed seasonal confounder inflates rejection to 23.8% |
| Season-restricted shift references | 2026 statistic exceeded all 63 and all 93 surrogates (sensitivity only) |
| Cross-year negative controls | 1 of 20 rejections; descriptive, not a Type-I error estimate |
| Development vs 2026 comparability | About 94% of the gap persists among the same 21 pairs and months; unexplained, weight-sensitive, and not evidence of a physical change |

Negative, failed and inconclusive outcomes are kept in the record on purpose.

---

## How to navigate the repository

| If you want to… | Go to |
|---|---|
| Understand the decisions behind every method | `DECISION_LOG.md` |
| See the frozen confirmation protocol | `PROTOCOL_E08_DRAFT_v2.md` at tag `protocol-freeze` |
| See the registered 2026 results | `experiments/E08_confirmation/confirmation_2026/` at tag `e08-confirmation` |
| Read any experiment's findings | `experiments/<ID>/REPORT.md` |
| Check the full evidence audit | `audit/` (branch `audit/final-experimental-audit`) |
| Get publication figures and tables | `publication/supplementary/` (branch `publication/supplementary-assets`) |
| Understand data restrictions | `DATA_PROVENANCE.md` and `SEALED_DATA_POLICY.md` |

**Where the latest work lives.** E12 and E13 are on `main`. E14, E15 and the publication material are on their own branches (below) until they are merged.

To view a branch on GitHub, use the branch selector, or open, for example:
`https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/research/e15-h2-matched-pair-comparability`

---

## Branches and tags

Every branch head carries a tag, so any state of the project can be retrieved exactly (`git checkout <tag>`).

| Branch | Purpose | Tag at branch head |
|---|---|---|
| `main` | Development experiments E00-E11, frozen confirmation E08, E12, E13, audit | `repository-guide-v1` |
| `research/e12-h2-null-calibration` | E12: synthetic calibration, power and falsification of H2 | `e12-null-calibration` |
| `research/e13-h2-seasonal-shift-sensitivity` | E13: season-restricted shift references for H2 | `e13-seasonal-reference-sensitivity` |
| `research/e14-h2-empirical-yearswap-null` | E14 (Experiment B): cross-year empirical negative controls | `e14-crossyear-negative-control` |
| `research/e15-h2-matched-pair-comparability` | E15 (Experiment A): matched-pair comparability; contains E12-E14 | `e15-matched-pair-comparability` |
| `audit/final-experimental-audit` | Final experimental audit, evidence matrix, figure inventory | `final-experimental-audit` |
| `manuscript/section2-figures-tables` | Main-text figures (Figs. 1-7, regime heatmap) and their scripts | `manuscript-figures-v1` |
| `publication/supplement-evidence-audit` | Evidence inventory for the Supplementary Information | `supplement-evidence-audit` |
| `publication/supplementary-assets` | Final Supplement figures S1-S23, tables S1-S14, manifests; contains E12-E15 | `supplementary-assets-v2` |

**Frozen-record tags (never moved):**
- `protocol-freeze` (`2b7c79e`): code and protocol frozen before the 2026 data were opened.
- `e08-confirmation` (`4c011a8`): the single registered confirmation run.

Milestone tags for each development experiment (`e00-feasibility` … `e11-x3`) are listed in the experiment index.

---

## Experiment index

| ID | Topic | Stage | Outcome | Tag |
|---|---|---|---|---|
| E00 | Feasibility of protocol v2.0 | development | archived | `e00-feasibility` |
| E01 | Network geometry and instrumentation | development | 66 pairs; 27 within 30 km form the H2 family | `e01-geometry` |
| E02 | Data quality and missingness | development | methane 90.6-94.2% valid per station | `e02-data-quality` |
| E03 | Excursion patterns | development | night and winter peaks; co-excursion falls with distance | `e03-excursion-patterns` |
| E04 | H1 stability association | development | gate passed | `e04-h1-gate-passed` |
| E05 | H2 directional coupling | development | gate passed | `e05-h2-gate-passed` |
| E06 | Detectability and lag kernel | development | kernel criterion **failed** | `e06-kernel-criterion-failed` |
| E07 | H3 composition decomposition | development | **not supported** | `e07-h3-not-supported`, `e07-r1` |
| PRE_E08 | Pre-confirmation benchmarks | development | complete | `pre-e08-tasks` |
| E08 | Frozen 2026 confirmation | **registered** | H1 confirmed, H2 confirmed, H3 not confirmed | `protocol-freeze`, `e08-confirmation` |
| E08 post | H1 negative-control and H3 weighting diagnostics | post-confirmation | covariance explanation not supported; AMS 18 dominance | (on `main`) |
| E09 | Alternative-height (ERA5 100 m) wind | development | **inconclusive** | `e09-x4-inconclusive`, `e09-r1` |
| E10 | Episode typology | development | **not supported** | `e10-typology-not-supported` |
| E11 | Station contributions | development | no single station drives H1 or H2 | `e11-x3` |
| E12 | Synthetic calibration and falsification | post-confirmation | calibration inconclusive; confounding and falsification demonstrated | `e12-null-calibration` |
| E13 | Season-restricted references | post-confirmation | robust to shift reference | `e13-seasonal-reference-sensitivity` |
| E14 | Cross-year negative controls (Experiment B) | post-confirmation | 1/20, 2/20, 0/20 rejections; descriptive | `e14-crossyear-negative-control` |
| E15 | Matched-pair comparability (Experiment A) | post-confirmation | gap not explained by network, window or reference | `e15-matched-pair-comparability` |

Each experiment folder contains its plan or protocol, code, `results/`, `figures/`, `REPORT.md` and a manifest of checksums.

---

## Repository layout

| Path | Contents |
|---|---|
| `config/project.toml` | All parameters, random seeds and frozen rules |
| `src/wbea/` | Shared library: guarded data loader, geometry, wind, H2 statistic, statistics, wildfire flag |
| `src/build/` | One-time builders of the development and confirmation panels from raw exports |
| `experiments/<ID>/` | One folder per experiment (see index above) |
| `tests/` | Unit, regression and data-seal tests |
| `manifests/` | SHA-256 checksums of raw archives and derived panels |
| `metadata/` | Station coordinates, flag dictionary, temporal split |
| `audit/` | Final experimental audit (on `main` and the audit branch) |
| `reviews/` | Internal review records |
| `literature/references.bib` | Reference list (PDFs are kept outside git) |
| `DECISION_LOG.md` | Every methodological decision, with the evidence available at the time |
| `REVIEW_BACKLOG.md` | Review items and their resolution |
| `PROTOCOL_E08_DRAFT_v2.md` | The frozen confirmation protocol (authoritative version at tag `protocol-freeze`) |
| `DATA_PROVENANCE.md`, `SEALED_DATA_POLICY.md` | Data sources, restrictions, and how the 2026 data were sealed |
| `HISTORY_REWRITE.md` | Old-to-new commit hash map from the 2026-11-10 author-identity rewrite (file contents unchanged) |

---

## Reproducing the analyses

```bash
git clone https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms.git
cd WBEA-Methane-Atmospheric-Mechanisms
pip install -r requirements.txt

# run the test suite (does not need WBEA data for most tests)
python -m pytest -q tests

# with authorised WBEA data placed in data/dev/ (see DATA_PROVENANCE.md):
python experiments/E04_stability_elasticity/run_e04.py
```

- **Exact states:** use the tags. For example, `git checkout e08-confirmation` reproduces the registered confirmation code and outputs.
- **Determinism:** all random seeds are fixed in `config/project.toml`. Saved results can be checked against each experiment's manifest checksums.
- **Post-confirmation experiments** are on their branches: `git checkout research/e15-h2-matched-pair-comparability`.

---

## Data access and integrity safeguards

- **Data are not in this repository.** WBEA hourly exports are marked for authorised use only. Obtain them from WBEA (https://wbea.org/data/continuous-monitoring-data/) and verify them against the SHA-256 manifests.
- **2026 data status.** The 2026 observations are WBEA's monthly validated records and are preliminary pending WBEA's annual validation.
- **Sealed confirmation data.** The 2026 data were kept outside the analysis environment until the protocol was frozen. A seal test fails if any development script reads them. Named post-confirmation exemptions (E13, E15) are documented.
- **Frozen record.** The frozen code and the registered E08 outputs are verified unchanged against their tags in every subsequent experiment.
- **No outcome-driven changes.** Post-confirmation analyses were planned and committed before being run, and never alter the registered H1-H3 decisions.

---

## Authors and contact

Benjamin C. Nweke and Soheil Saraji, University of Wyoming.
Contact: bnweke@uwyo.edu

*Licence: to be added before publication. Until then, all rights are reserved by the authors.*
