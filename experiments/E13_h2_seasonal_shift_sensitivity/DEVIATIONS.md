# E13 deviations from EXPERIMENT_PLAN.md
| # | When | What | Effect |
|---|---|---|---|
| D1 | Before any seasonal statistic | Test fixture corrected: the wraparound test used a random matrix whose count columns were not integers, while the fast routine (from E12) rounds count columns. The fixture is now a genuine moment matrix | Test only; no analysis code changed |
| D2 | After results | Figure layout only (two-line titles, shared x label, label placement) | Presentation; no numbers changed |
No configuration, partition, shift range, weighting rule, interpretation rule or pair rule was changed after results were seen. All pre-registered configurations (R0, C1-w, C1-f, C2-w, C2-f, C4) are reported.
