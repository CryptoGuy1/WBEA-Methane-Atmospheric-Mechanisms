# E14 artifact manifest (v2, interpretation correction)
Branch `research/e14-h2-empirical-yearswap-null`. Plan `05440d4`; implementation `666e7e8`; original results `cf84a8b` (recorded in `RESULTS_COMMIT.txt`); correction commit: this commit (see git log).

**v2 changes:** interpretation only (`REPORT.md` v2; plan addendum; two figure tick labels). All numerical outputs are byte-identical to `cf84a8b`. `REPORT_v1_superseded.md` is the original report, unchanged. The figure PDF is now committed (previously excluded by `.gitignore`).

Tests: `python -m pytest tests experiments/E12_h2_synthetic_null_calibration/tests experiments/E13_h2_seasonal_shift_sensitivity/tests experiments/E14_h2_empirical_yearswap_null/tests`.

| File | SHA-256 | v2 status |
|---|---|---|
| `EXPERIMENT_PLAN.md` | `de3f8715fb5332eb9c197050043268082a7b3b1ccfd457c02bfc57a897431503` | addendum appended |
| `REPORT.md` | `6b7d267bf5101657cc05f16dbe2d35b1c55ab21b5ce817be347fcbe87f7224f1` | new (v2) |
| `REPORT_v1_superseded.md` | `fabbbbd59c05eb4b354380e6d03b8e8053feadbcf76c9e5d5cd01b4e3fa525fb` | original v1, renamed |
| `e14.py` | `be7a77c39cf0365e2d1ede57ce59bff25c8e58d93d8f08ff64f593f9ac3275a7` | unchanged |
| `run_e14.py` | `fd8e25f2b42445ed7812594c99b8216b75031b900daa0ba6dd5640b7eba5c86d` | unchanged |
| `analyze_e14.py` | `d50e75263161971a47218806eb3396083eaf636c7a418b27b92bc2726debf339` | two labels changed |
| `tests/test_e14.py` | `0a57d18d6e25bcdd81ea0f2a8fead316b57867b523b4f5c46225a67732320f53` | unchanged |
| `results/replicates.csv` | `d815894c7ccb9fbe553b373114ce9d92366b35d69b7cd52fa8cd9a07fb61d8ec` | unchanged |
| `results/summary.csv` | `f751fe8a759119763808e3a7815b6df779fe9a4581ed27ab91d63f3790c9b309` | unchanged |
| `results/secondary_stats.json` | `c1f806dcea014217028cd549eef88df509b39ac5cf7b6c9adb21e089139bbefc` | unchanged |
| `results/seasonal_recurrence.json` | `8097c4bcad28df9c85e9dd1da81e0fb04bc806fda05e7cd21299eb890877ecee` | unchanged |
| `results/run_log.json` | `07b6a2bd537a927e7eb83d48c0997921bdb8a4748687e86dba73aa3b6b26415b` | unchanged |
| `results/null_pooled_coverage_rule.npz` | `7508f073cb72a5f93b44ccdf887e57321c765cae5943cee1f8325d22dea88f2d` | unchanged |
| `results/null_pooled_confirmation_network.npz` | `7feafc15055d4517fe3ca745e6b2da3b20f1484b330f6e8f7de3550f00d23c41` | unchanged |
| `figures/e14_yearswap_null.pdf` | `bc5b87ddbb9d25e56c6fd2d8a5a9c879e64c311f3976b66259886d1a2f94945f` | regenerated (labels) |
| `figures/e14_yearswap_null.svg` | `ccf73038851a7f7b7e379c81dddd1e00c6822fedc6926cfb57d3498a00f063e7` | regenerated (labels) |
| `figures/e14_yearswap_null.png` | `725215facf7b0e694955bbcdc549413d22e73058086f7d545d64d01764f0c8c0` | regenerated (labels) |
