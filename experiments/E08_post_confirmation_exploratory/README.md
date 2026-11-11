# Post-confirmation exploratory analyses (v1, 2026-11-10)

**Everything in this folder is POST-CONFIRMATION EXPLORATORY.** It reads saved E08 outputs only. It does not change, rerun or replace any frozen result in `experiments/E08_confirmation/` (tags `protocol-freeze`, `e08-confirmation`). The registered E08 decisions stand: H1 confirmed, H2 confirmed, H3 not confirmed.

| File | Content |
|---|---|
| `h3_weight_concentration.py` | Denominator decomposition of the registered H3 projection estimator from the saved 2026 contrasts |
| `results/h3_weight_concentration.json` | AMS 18 = 92.9% of sum(t^2) in 2026 (39.0% in development Jan-Sep); AMS 18 mean abs total 42.6 pp vs 2.8 pp elsewhere; point share without AMS 18 = -0.085 (50 contrasts; no interval computed); station-averaged point share 0.031 |
| `results/h3_2026_denominator_by_station.csv` | Per-station denominator and share |
