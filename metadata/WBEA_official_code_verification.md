# Official verification of WBEA data codes and timestamp convention (2026-11-10)

## Sources
1. WBEA, *Monthly Ambient Air Quality Monitoring Report, September 2024* (dated 31 Oct 2024), https://wbea.org/wp-content/uploads/2024/10/WBEA-202409.pdf. AMS01 Fort McKay - Bertha Ganter, **"Summary of Hour Averages, Methane (CH4) - ppm", page 1-40**; the same legend appears on every hourly table: **"Z - zerospan  C - Calibration  M - Maintenance"**. Table header: **"Hourly Period Ending At (MST)"**.
2. WBEA Glossary, https://wbea.org/glossary/, entry "Zero/Span": daily cycle, usually in the early hours of the morning; about 20 minutes of zero air, then span gas, then about 10 minutes of recovery before readings are accepted. Entry "Baseline Correction": daily zero data are used to correct raw measurements.
3. WBEA SOP-ANA-008 NMHC (2013): daily zero/span cycle flagged as calibration (recorded earlier, D-53).

## What is established
- `Z` = zero/span hour (official WBEA code). Z-coded hours remain excluded from valid ambient CH4.
- `C` = calibration (official). `M` = maintenance (official in reports; **not carried in the CSV export**, where such hours appear as `.`).
- Timestamps are **hour-ending MST** (official table header). This upgrades decision D-02 from data-inferred to officially documented.

## Export consistency check (development data, AMS 1 CH4, September 2024)
| Item | CSV export | Official report |
|---|---|---|
| Z hours (day, hour-ending) | 30 of 30 identical | 1 per day, hours 01-06 rotating |
| C hours | 9 Sep 10:00-14:00 | same |
| M hours | `.` at 24 Sep 13:00-14:00 | M at the same hours |
| Valid hours | 683 | 683 |
| Values | 3.315, 2.766, 3.152, 1.919 ppm | 3.3, 2.8, 3.2, 1.9 ppm (0.1 ppm reporting precision) |

## What is NOT established (relevant to X2)
- Whether the 01:00-06:00 placement and the ~25 h rotation are deliberately scheduled (the glossary says "usually in the early hours", which describes but does not explain).
- Whether the timing is adjustable under WBEA's procedures or AMD requirements.
- Whether the code convention verified for one station-month holds for all stations and years (the 25 h pattern and token counts in E02 are consistent with it).

## Other information in the same report (recorded, not used to change results)
- CH4 analyser replaced at AMS 05 Mannix on 11 Sep 2024 and at AMS 23 Fort Hills on 25 Sep 2024 (instrument history, RB-10).
- Final 5-min values are baseline-corrected by subtracting interpolated daily zero responses.
- A CH4 response below the expected 1.8 ppm background triggers an analyser investigation.
