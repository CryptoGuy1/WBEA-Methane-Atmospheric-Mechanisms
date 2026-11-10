# E02 Data completeness, calibration gaps and measurement quality

**Status:** exploratory (development data 2021-01-01 01:00 to 2025-12-02 00:00 MST). Decision criterion met: yes (data adequate for E03-E07).

## Questions and estimands
| Q | Question | Estimand |
|---|---|---|
| Q1 | Completeness of each hypothesis variable | % valid hours, station x year |
| Q2 | Months failing Alberta's 90% operational criterion (AMD DQ 4-C) | count of station-months, QA hours excluded and included |
| Q3 | Timing and simultaneity of gaps | share of station-hours missing by code and hour; gap run lengths |
| Q4 | Is the nightly Z gap ignorable given hour and month? | mean of (CH4[t-1]+CH4[t+1])/2 at Z hours minus the same quantity at non-Z hours with the same hour and month; 14-day block bootstrap, 1,000 reps |
| Q5 | Usable hours for H1 | hours meeting the frozen station rule with S and AMS 5 wind valid |

## Results
- **Q1.** CH4 90.6-94.2% overall. Composite wind 91.6-100% per station-year. AT2 >= 98.7%. AMS 5 tower S (T90 - T20) 99.1-100%. AMS 1 dT (10-2 m) 96.5-100%. **AMS 14 dT and AT10 are empty (all '.') in every year**, so AMS 14 cannot serve as a stability proxy. PM2.5 92.8-99.8% at 9 stations.
- **Q2.** Of 720 station-months, 48 fall below 90% after excluding QA hours (AMS 1: 0; AMS 5 and AMS 18: 7 each) and 19 fall below 75% of all hours. The worst episodes are AMS 5 and AMS 11 in mid-2021 and AMS 18 in January 2024.
- **Q3.** Z occupies 16.2-16.4% of station-hours in each hour ending 01-06 and none elsewhere. C peaks at 3.1% at hour 12. '.' rises from 2.2% at night to 3.5% at midday. Z is never simultaneous at all stations: 1,849 hours have 5 stations in Z at once, 503 have 6, 16 have 7, none more. 92-95% of gaps are single hours; the longest gap is 542 h (AMS 5, 2021).
- **Q4.** The bracketing CH4 at Z hours differs from comparable non-Z hours by -0.009 to +0.005 ppm. All 12 bootstrap intervals include zero (widest -0.032 to +0.014, AMS 23). **The Z gap is consistent with missing at random given hour and month.** It is not consistent with gaps preferentially removing high or low concentrations.
- **Q5.** H1 core rule: 40,334 of 43,104 hours usable (93.6%). Expanded rule (>= 8 of 11): 39,219.
- **NMHC.** 27-86% of valid NMHC values are exactly zero (left-censored under AMD DQ 4-J). NMHC can only be used as a censored, descriptive variable.

## Interpretation
The Z gap removes about one-sixth of station-hours in the hours ending 01-06, which is the period of strongest nocturnal accumulation. Q4 shows it does not bias concentrations conditional on hour and month. Analyses that condition on hour (all H1 models, all H3 regimes) can therefore use complete cases without bias from Z. Unconditional statistics such as raw exceedance counts are biased in level: they under-count night hours, and E07 bounds this.

## Limitations
- Q4 tests one form of non-ignorability (bracketing values). A gap that coincides with a brief spike shorter than an hour would not be detected.
- The meaning of Z remains unconfirmed by WBEA; the result concerns its statistical behaviour, not its cause.
- Monthly completeness uses this export; WBEA's official figures exclude QA periods by their own rules.

## Decisions
D-13, D-14 and D-15 in DECISION_LOG.md.

## Figure
`figures/figure02_coverage_and_gap_timing.{png,svg,pdf}`, main Figure 2.
