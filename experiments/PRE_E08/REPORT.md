# PRE_E08 development tasks (2026-11-10)
Development data only; no 2026 methane value read.

| Task | Result |
|---|---|
| F3 (D-47) H3 benchmark, Jan-Oct window (E07-r2) | share 0.019 (CI -0.035 to 0.117); 120 contrasts; median 12 effective regimes. Original Jan-Nov 0.027 retained. H3 remains not supported |
| F4 (D-48) finite-shift null | 342-day confirmation length gives K = 315 admissible shifts (min p 0.0032); with the F2 eligible window of 303 days, K = 276 (min p 0.0036). Verified on the last 342 development days: pooled D 0.182, p = 0.0032 (at the floor), 27 pairs estimable, 11 family-wise < 0.05, runtime 11 s |
| F5 (D-50) development benchmark | Stable-low-wind: 7.4% of hours, 20.3% of P95 onsets, enrichment 2.73 (2.53-2.94); intermediate 1.30 (1.26-1.34); advective: 38.0% of hours, 8.9% of onsets, 0.23 (0.21-0.26); 155 onsets unclassified. Descriptive only |
| X4 variable availability | AMS 5 WS/WD 45, 75, 90 m: 97.4-98.5% valid; ERA5 u100/v100: complete. Median speed ratio to 20 m at AMS 5: 1.35 (45 m), 1.50 (75 m), 1.56 (90 m); ERA5 100 m vs AMS 1 10 m: 1.95 |
| F2 eligibility | See metadata/E08_data_eligibility.md: primary set 2025-12-02 to 2026-09-30 |

Note (X4): the E06 lag shortfall (25-30%) corresponds to an effective speed about 1.3-1.4 times the 10 m wind, similar to the 45 m / 20 m ratio. This is a hypothesis for X4, not a result.
