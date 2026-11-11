# E12: Synthetic calibration of the frozen H2 shifted-wind test

**Post-confirmation exploratory methodological study.** It does not modify E01-E11, the frozen E08 code, results, decisions or tags, and it uses no 2026 methane data. The registered H2 decision stands; E12 only informs how the finite-shift p-value is characterised.

| File | Purpose |
|---|---|
| `EXPERIMENT_PLAN.md` | Pre-registered design (commit c45f8ef, before any implementation output) |
| `DEVIATIONS.md` | All departures from the plan, with timing and reasons |
| `estimate_params_from_development.py`, `synthetic_params.json` | Wind-generator parameters from development wind only (no methane, no 2026) |
| `e12/generator.py` | Synthetic 11-station network, scenarios N0, N1a, N1b, N2a, N2b, N3, P1/P1T |
| `e12/fast_h2.py` | Exact fast evaluation of the frozen H2 statistic over all 246 shifts (FFT), alternative nulls, ungated baseline |
| `tests/test_e12.py` | Parity with the frozen pipeline (incl. full 246-shift pooled D and p), determinism, shift counts, null/positive distinction, missingness, non-modification of frozen files |
| `pilot_p1_amplitudes.py`, `pilot_p1t_amplitudes.py`, `p1_amplitudes.json` | Effect-size pilots and final power configurations (fixed before production) |
| `run_e12.py`, `run_all.sh` | Runner and production script (seeds per plan section 6) |
| `analyze_e12.py` | Summaries, Wilson intervals, pre-registered classifications, figures |
| `results/` | Raw per-replicate CSVs, summaries, verdicts, logs |
| `figures/` | Generated figures (PNG, SVG, PDF) |
| `REPORT_FOR_MANUSCRIPT_AI.md`, `MANUSCRIPT_HANDOFF.md` | Scientific report and manuscript handoff |

## Reproduce
```
pip install -r requirements.txt
make test          # 7 tests, about 10 s
make production    # 4,100 replicates, about 40 min on one CPU
make analysis
```
Requires the repository's `src/wbea` (frozen H2 functions) and `metadata/stations_official_2024.csv` (public station coordinates). No WBEA monitoring data are needed.
