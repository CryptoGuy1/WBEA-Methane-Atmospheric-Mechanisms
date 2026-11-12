# E13 deviations from EXPERIMENT_PLAN.md
| # | When | What | Effect |
|---|---|---|---|
| D1 | Before any seasonal statistic | Test fixture corrected: the wraparound test used a random matrix whose count columns were not integers, while the fast routine (from E12) rounds count columns. The fixture is now a genuine moment matrix | Test only; no analysis code changed |
| D2 | After results | Figure layout only (two-line titles, shared x label, label placement) | Presentation; no numbers changed |
No configuration, partition, shift range, weighting rule, interpretation rule or pair rule was changed after results were seen. All pre-registered configurations (R0, C1-w, C1-f, C2-w, C2-f, C4) are reported.
| D3 | After results (found by the full combined test run) | The repository seal test (`tests/test_seal.py`) flagged E13 for reading `sealed/e08_panel`. A narrow, named exemption for `experiments/E13_h2_seasonal_shift_sensitivity` was added, mirroring the existing E08 exemption | The read was explicitly authorised (post-confirmation exploratory); the guard itself is kept for all other development code. No analysis code or result changed |
