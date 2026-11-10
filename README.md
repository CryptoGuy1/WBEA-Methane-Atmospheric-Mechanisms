# WBEA Methane Atmospheric Mechanisms

Observational study of atmospheric stability, direction-dependent inter-station coupling, and the
meteorological composition of methane-exceedance reporting in the WBEA monitoring network
(Athabasca oil sands, Alberta), 2021-2025 development data with a sealed 2026 confirmation set.

## Status
| Milestone | Tag | State |
|---|---|---|
| Feasibility check of protocol v2.0 | `e00-feasibility` | archived |
| R1 research readiness | `r1-readiness` | complete |
| E02 data quality | `e02-data-quality` | complete (exploratory) |
| E03 excursion patterns | `e03-excursion-patterns` | complete (exploratory) |
| E01 geometry and instrumentation | `e01-geometry` | complete |
| E04 H1 stability elasticity (gate) | `e04-h1-gate-passed` | gate passed (exploratory) |
| E05 H2 directional coupling | `e05-h2-gate-passed` | gate criteria 1-2 passed (exploratory) |
| E06 detectability and kernel shape | `e06-kernel-criterion-failed` | criterion 3 failed as pre-registered; revised for E08 |
| E05+E06 joint review | `review-e05-e06` | no material error |
| E07 composition decomposition | `e07-h3-not-supported` | H3 not supported as pre-registered (exploratory) |
| Integrated review E02-E07 | - | next (before E08 freeze) |
| E08 confirmation | - | **sealed** (see SEALED_DATA_POLICY.md) |

All development results are **exploratory**. Only E08 produces confirmatory results.

## Layout
| Path | Contents |
|---|---|
| `config/project.toml` | All parameters, seeds, frozen rules |
| `src/wbea/` | Shared library (guarded loader, geometry, wind, statistics, solar, smoke) |
| `src/build/` | One-time builder of the development panel from raw exports (stops at cutoff) |
| `experiments/<ID>/` | One directory per experiment: script, `results/`, `figures/`, `REPORT.md`, `run_metadata.json` |
| `manifests/` | SHA-256 of every raw archive/file and of the development panel |
| `metadata/` | Station coordinates, flag dictionary, temporal split |
| `tests/` | Unit and seal tests (`python -m pytest -q tests`) |
| `DECISION_LOG.md` | Every methodological decision, with the evidence available at the time |
| `literature/references.bib` | Reference list (PDFs are kept outside git) |

## Reproduce
```
pip install -r requirements.txt
# place the development panel in data/dev/ (rebuild with src/build/build_dev_panel.py from raw exports)
python -m pytest -q tests
python experiments/E02_data_quality/run_e02.py
python experiments/E03_excursion_patterns/run_e03.py
```
Data are not in git: WBEA exports are marked "For authorized use only". See DATA_PROVENANCE.md.
