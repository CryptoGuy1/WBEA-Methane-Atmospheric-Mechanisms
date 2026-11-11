# E13: Post-confirmation seasonal-shift sensitivity of the 2026 H2 result
**POST-CONFIRMATION EXPLORATORY.** It does not change E08 (code, results, protocol, decision, tags) or E12 (verified by tests).
| File | Purpose |
|---|---|
| `EXPERIMENT_PLAN.md` | Pre-registered plan (commit 2d7227c, before any seasonal 2026 statistic) |
| `e13.py` | Data loading (frozen inputs), within-block circular shifts, per-season analysis, summaries |
| `tests/test_e13.py` | Block boundaries, wraparound, weight invariance, exact reproduction of frozen 2026 H2 (D = 0.287931708, p = 1/247), determinism, non-modification of E08/E12 |
| `run_e13.py` | Runs all configurations; writes `results/` |
| `make_figures.py` | Figures from saved results |
| `results/` | `e13_summary.csv`, `e13_per_season.csv`, `e13_pairs_C1.csv`, `e13_pairs_C2.csv`, `e13_surrogates_*.csv`, `e13_results.json` |
| `figures/` | `e13_fig1_reference_distributions`, `e13_fig2_per_season` (PNG/SVG/PDF) |
| `E13_REPORT_FOR_MANUSCRIPT_AI.md`, `E13_MANUSCRIPT_HANDOFF.md` | Report and handoff |
Reproduce (requires the sealed 2026 panel in `sealed/e08_panel/`, which is not in git, and the development panel): `python3 -m pytest -q tests && python3 run_e13.py && python3 make_figures.py` (about 1 min).
