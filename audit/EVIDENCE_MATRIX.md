# Integrated evidence matrix (final audit, 2026-11-11)
Status key: **DEV** = development finding (2021-2025; exploratory, informed method choices); **CONF** = registered confirmation (E08, 2026 Jan-Sep, frozen at `protocol-freeze` 2b7c79e, executed once); **POST** = post-confirmation exploratory (2026 data or synthetic; cannot change any registered decision). Every number below was cross-checked against saved result files (`audit/crosscheck_results.csv`).

| Question | Evidence | Status | Result (exact) | Verdict |
|---|---|---|---|---|
| **H1** stability association | E04 | DEV | 0.048 ppm/SD (0.041-0.052); 5/5 years positive; next-day control 0.000 (-0.005 to 0.003) | Development gate passed |
| | E08 | CONF | **0.052 (0.039-0.069)**, n = 4,472 h; control b_nc -0.0187 (-0.0268 to -0.0051), ratio -0.34 (-0.51 to -0.09) | **Confirmed** (criterion b not triggered: abs ratio < 0.5) |
| | E08 descriptive | CONF (descriptive) | ERA5 proxy 0.058; CR1 SE 0.0078 | Supports |
| | H1 diagnostic | POST | 2026 within-cell corr(S, S+24) = 0.146 (development 0.060-0.299); corr(CH4, S+24) = -0.043 (development +0.030 to +0.133) | Covariance explanation **not supported**; anomaly **unexplained** |
| **H2** directional coupling | E05 | DEV | D = 0.128 (0.108-0.155), 27/27 pairs positive | Development gate passed |
| | E08 | CONF | **D = 0.2879, p = 1/247 (floor), K = 246**, 21 pairs; +/-1 h: 0.294/0.257; centroids 0.13-1.12 h, rho 1.0 | **Confirmed** |
| | E08 descriptive | CONF (descriptive) | 14/21 pairs family-wise p < 0.05 (max-T) | Broad support |
| | E12 null calibration | POST (synthetic) | Rejection 4.6% / 5.4% / 4.8% / 4.6% (N0, N1a, N2a, N3) | **Inconclusive** by rule (N1a upper bound 0.077 > 0.075); no inflation observed |
| | E12 seasonal confounding | POST (synthetic) | N2b: **23.8% (20.3-27.7%)**; within-season shift 5.2% | Whole-period shift **sensitive** |
| | E12 power | POST (synthetic) | 100% at D 0.07-0.20; **0% at 3 h true lag** (median D -0.040); D >= 0.21 not testable | Adequate within tested range; blind spot at long lags |
| | E12 falsification | POST (synthetic) | Advected shared signal, no methane transport: **100% rejection**, median D 0.132 | H2 rejection **does not identify methane transport** |
| | E13 seasonal shifts | POST (2026) | Quarters: 0/63 >= obs (p = 1/64); halves: 0/93 (p = 1/94); per quarter D = 0.347/0.216/0.201, all at floor | Result **robust** to seasonal shift construction ("strengthens", pre-registered rule) |
| **Transport timing** (quantitative) | E06 kernel criterion | DEV | Centroids 0.25/0.39/0.73/1.11/1.51 h; inside A = 3 reference in **1 of 5** bins (required 4) | **FAILED** (pre-registered) |
| | E06 continuous-source correction | DEV | For tau > 1.5 h, lags 25-30% shorter than 10 m-wind transit | **Unresolved** |
| | E09 / E09-r1 elevated wind | DEV | Delta SSE 0.294 (-0.122 to 0.741) | **Inconclusive** |
| | E08 descriptive kernel | CONF (descriptive) | SSE vs mask-gated 0.19, vs continuous 1.12; long-transit lags still short | Shortfall **replicated** |
| **H3** weather-mix share | E07 | DEV | 0.027 (-0.040 to 0.126); Jan-Sep 0.026 | **Not supported** |
| | E08 | CONF | **0.011 (-0.020 to 0.043)**, 55 contrasts | **Not confirmed** |
| | H3 weight diagnostic | POST | AMS 18 = **92.9%** of estimator denominator (development 39.0%); excluding AMS 18: -0.085 (point only) | Registered estimate dominated by one station |
| **Episodes** | E10 typology | DEV | Wind-shift placebo not met (0.122 vs 0.148 at 95th percentile) | **Not supported** |
| | F5 regimes | DEV / CONF descriptive | Stable low wind enrichment 2.73 (DEV), 2.46 (2026) | Descriptive, replicated |
| **Network** | E03 distance decay | DEV | Spearman -0.82 (-0.86 to -0.73) | Descriptive |
| | E11 station contribution | DEV | H1 0.043-0.057; H2 0.121-0.143 leaving one station out | No single station drives H1/H2 |
