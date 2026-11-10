# Integrated development-stage scientific review, E01-E07 (2026-11-10)

Full review: Claude Doc "Integrated Development-Stage Scientific Review: WBEA Methane Study (E01-E07)".
This file records its verdict and the decisions it requests. No 2026 methane value was accessed.

## Verdict
The development programme is sound and ready for the E08 freeze once items F1-F5 are decided. No error invalidates a completed result.

| Hypothesis | Development result |
|---|---|
| H1 stability raises network CH4 level | Supported: 0.048 ppm/SD (0.041-0.052); all gate criteria met |
| H2 direction-dependent coupling | Supported: pooled D 0.128 (0.108-0.155), p <= 0.001, 27/27 positive |
| H2 kernel shape | Failed as pre-registered; long-transit lags about 25-30% shorter than 10 m-wind transport |
| H3 meteorology mix | Not supported: 0.027 (-0.040 to 0.126); 6-regime 0.032 |

## Corrections made during the integrated review
1. E06 interpretation amended (lags consistent with 10 m-wind transport only for short-transit bins); original wording preserved.
2. E07-r1: "Manski bounds" renamed extreme missing-outcome scenarios; deweathering validated forward-year (year effect not identified out of sample); merge structure documented; regime-resolution sensitivity (6 regimes 0.032).

## Items requiring researcher decision before the E08 freeze
| # | Item | Recommendation |
|---|---|---|
| F1 | H2 kernel criterion (RB-19) | 3(i) monotone centroid confirmatory; 3(ii) descriptive against both reference models; no envelope widening |
| F2 | 2026 validation status | Primary set = WBEA-confirmed final months; one pre-declared re-run after WBEA's 2026 annual review |
| F3 | H3 confirmation design | 2026 vs each development year, common 1 Jan - 31 Oct window, 60 contrasts; same estimator; no new confirmatory estimand |
| F4 | Frozen reference quantities and settings | All 2021-2023 references, pair family, kernel rule, 5,000 shifts on [14 d, N - 14 d], blocks, seeds, code and environment hashes |
| F5 | Optional operational analysis (JEM framing) | Pre-specify now or omit |

## Journal recommendation (development stage)
Environmental Modelling & Software primary; Journal of Environmental Management alternative (would need a pre-specified operational analysis, F5).

## Freeze checklist
- [ ] Decisions F1, F3, F5 recorded in DECISION_LOG.md
- [ ] WBEA confirmation of 2026 final months (F2)
- [ ] E08 protocol and code committed; tag `protocol-freeze`
- [ ] SHA-256 of 2026 exports re-verified
- [ ] Split, open, single run, results committed unchanged
