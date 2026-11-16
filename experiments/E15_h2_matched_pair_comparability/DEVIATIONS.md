# E15 deviations and documented actions
- **D1 (seal-test exemption, before the run):** E15 reads the sealed 2026 panel (already opened by the registered confirmation) for analyses A1 (recomputed environment), A6 and A7. `tests/test_seal.py` gains a named exemption for `experiments/E15_h2_matched_pair_comparability`, mirroring E13's. No other test or frozen file is changed.
