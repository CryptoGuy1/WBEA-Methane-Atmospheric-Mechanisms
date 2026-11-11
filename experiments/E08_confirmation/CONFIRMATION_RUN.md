# E08 confirmation run record (single execution)

| Item | Value |
|---|---|
| Frozen commit (tag `protocol-freeze`) | 2b7c79e259ea1fbc957998da9f921db8abdf38ea (local = remote; clean tree verified; release guard passed in both runners) |
| Source workbooks | 12 of 12 SHA-256 match the acquisition manifest (`confirmation_2026/source_hash_verification.txt`) |
| Splitter | 2026-01-01 01:00 to 2026-10-01 00:00 MST hour-ending; 12 stations x 6,552 rows = 78,624; output SHA-256 in `confirmation_2026/SHA256SUMS.txt`; panel stored outside git (`sealed/e08_panel/`) |
| Primary run | `run_e08.py --mode confirm`, once; runtime 11.6 s; log `confirmation_2026/e08_primary_run_log.txt` |
| Descriptive run | `run_e08_descriptive.py --mode confirm`, once; primary-output guard passed; log `confirmation_2026/descriptive/descriptive_run_log.txt` |
| Contingency triggered | AMS 2 excluded (41.2% valid CH4 < 50%); H1 core 6 stations (minimum 6 met); H2 21 pairs; H3 55 contrasts |
| Execution errors | none; no code changed after the freeze |
| Results committed | unchanged, in `confirmation_2026/`; comparison in `development_vs_confirmation.csv` |
