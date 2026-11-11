# Post-confirmation exploratory analyses (v1, 2026-11-10)

**Everything in this folder is POST-CONFIRMATION EXPLORATORY.** It reads saved E08 outputs only. It does not change, rerun or replace any frozen result in `experiments/E08_confirmation/` (tags `protocol-freeze`, `e08-confirmation`). The registered E08 decisions stand: H1 confirmed, H2 confirmed, H3 not confirmed.

| File | Content |
|---|---|
| `h3_weight_concentration.py` | Denominator decomposition of the registered H3 projection estimator from the saved 2026 contrasts |
| `results/h3_weight_concentration.json` | AMS 18 = 92.9% of sum(t^2) in 2026 (39.0% in development Jan-Sep); AMS 18 mean abs total 42.6 pp vs 2.8 pp elsewhere; point share without AMS 18 = -0.085 (50 contrasts; no interval computed); station-averaged point share 0.031 |
| `results/h3_2026_denominator_by_station.csv` | Per-station denominator and share |
| `h1_nc_covariance_diagnostic.py` | Item C: within-cell correlation of S(t) and S(t+24) by Jan-Sep period (2021-2026) with the frozen estimator. Result: 2026 correlation 0.146 lies inside the development range (0.060-0.299); no relation to b_nc across periods (Spearman 0.14). The changed-covariance explanation is not supported. The within-cell correlation of the CH4 level with next-day stability is positive in every development year (0.030-0.133) and negative in 2026 (-0.043); 2026 b_nc (-0.019) lies outside every single-year development estimate (-0.002 to 0.003). Cause unexplained. Registered H1 result unchanged |
