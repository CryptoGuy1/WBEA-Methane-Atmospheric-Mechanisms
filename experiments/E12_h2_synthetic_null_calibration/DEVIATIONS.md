# E12 deviations from EXPERIMENT_PLAN.md

| # | When | What | Why | Effect on pre-registered design |
|---|---|---|---|---|
| D1 | Before pilot and production | Generator bug fix: the Markov sector index is now clamped to 0-7 inside the loop; previously it was clamped only after the loop, so a floating-point cumulative sum slightly below 1 could produce index 8 and crash | Implementation error found when the pilot crashed | None on the design. The tests were re-run after the fix |
| D2 | Before production | The evaluator applies the E08 station-coverage rule (stations with < 50% valid CH4 excluded before pairing), as `run_e08.py` does | Fidelity to the frozen pipeline; found by the missingness edge-case test | None on the design; makes the implementation match E08 |
