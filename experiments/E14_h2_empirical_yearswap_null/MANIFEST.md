# E14 artifact manifest
Branch `research/e14-h2-empirical-yearswap-null` (from `research/e13-h2-seasonal-shift-sensitivity` at `a0f4e9f`). Plan commit `05440d4`; implementation commit `666e7e8`; results commit in `RESULTS_COMMIT.txt`.

Tests: `python -m pytest tests experiments/E12_h2_synthetic_null_calibration/tests experiments/E13_h2_seasonal_shift_sensitivity/tests experiments/E14_h2_empirical_yearswap_null/tests`: 60 passed (8 new in E14).

Reproduce: `python run_e14.py && python analyze_e14.py` (development data in `data/dev/`; about 1 min).

| File | SHA-256 |
|---|---|
| `EXPERIMENT_PLAN.md` | `c2c616ed80a2f6ba11caf526d89cab310855fc96d9712550b3dd5c80fe8a4d05` |
| `REPORT.md` | `fabbbbd59c05eb4b354380e6d03b8e8053feadbcf76c9e5d5cd01b4e3fa525fb` |
| `e14.py` | `be7a77c39cf0365e2d1ede57ce59bff25c8e58d93d8f08ff64f593f9ac3275a7` |
| `run_e14.py` | `fd8e25f2b42445ed7812594c99b8216b75031b900daa0ba6dd5640b7eba5c86d` |
| `analyze_e14.py` | `b963470502f86dd60a8f936cde216d5f5a9ff093c7fa0c148fd53142de0188c5` |
| `tests/test_e14.py` | `0a57d18d6e25bcdd81ea0f2a8fead316b57867b523b4f5c46225a67732320f53` |
| `results/replicates.csv` | `d815894c7ccb9fbe553b373114ce9d92366b35d69b7cd52fa8cd9a07fb61d8ec` |
| `results/summary.csv` | `f751fe8a759119763808e3a7815b6df779fe9a4581ed27ab91d63f3790c9b309` |
| `results/secondary_stats.json` | `c1f806dcea014217028cd549eef88df509b39ac5cf7b6c9adb21e089139bbefc` |
| `results/seasonal_recurrence.json` | `8097c4bcad28df9c85e9dd1da81e0fb04bc806fda05e7cd21299eb890877ecee` |
| `results/run_log.json` | `07b6a2bd537a927e7eb83d48c0997921bdb8a4748687e86dba73aa3b6b26415b` |
| `results/null_pooled_coverage_rule.npz` | `7508f073cb72a5f93b44ccdf887e57321c765cae5943cee1f8325d22dea88f2d` |
| `results/null_pooled_confirmation_network.npz` | `7feafc15055d4517fe3ca745e6b2da3b20f1484b330f6e8f7de3550f00d23c41` |
| `figures/e14_yearswap_null.pdf` | `b5024c0ce7a0f2c44ccfc7324b44e5b2b1db2a052fa3a0f4b4e493bc03bbcd09` |
| `figures/e14_yearswap_null.svg` | `49403dc2cbb81a795d22afb8fae5ce0ed334c39f91f21b9132f6ab18f3483751` |
| `figures/e14_yearswap_null.png` | `86527d49ec240e264e65da639c0aa4a1a13df5bb02d42e6e5389892b4103b44a` |
