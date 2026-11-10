# E08 confirmation-data eligibility (F2), 2026-11-10

## Official evidence
- WBEA Continuous Monitoring Data page (wbea.org/?p=6009, accessed 2026-11-10): data there are WBEA's final data, validated and available 30 days after the end of the calendar month in which they were collected.
- WBEA Monthly reports page (wbea.org/?p=7805): monthly reports use validated datasets, available 30 days after month end.
- WBEA data-management page: Level 2 data are quality controlled, processed monthly with baseline correction; Level 3 independent review.
- Alberta AMD Chapter 6 (2014), DQ 4-Q: an annual post-final validation review precedes the annual report; validated data may still be revised then.

## Consequence for the exports made 2026-11-09
| Period | Status at export | E08 role |
|---|---|---|
| 2025-12-02 01:00 to 2026-09-30 24:00 (303 days) | Final (more than 30 days after month end) | **Primary confirmation set** |
| 2026-10-01 to 2026-10-31 | Not yet final (final after 2026-11-30) | Excluded from primary; usable only after a re-export of final data |
| 2026-11-01 to 2026-11-09 | Not final | Excluded |
| All of 2026 | Subject to WBEA's annual post-final review (expected about March 2027) | One pre-declared sensitivity re-run after the annual report |

## Consequences for other frozen settings (decisions needed)
- H2 finite-shift null on 303 days: K = 276 admissible whole-day shifts (14 to 289 days); smallest attainable p = 1/277 = 0.0036.
- H3 Jan-Oct window (D-47) needs October 2026. Options: (a) re-export after 2026-11-30 and hash October separately before opening; (b) change the common window to Jan-Sep for both development benchmark and confirmation. Decision required before freeze.

## Calibration flag evidence (RB-11, partial)
WBEA SOP-ANA-008 NMHC (2013, osmdatacatalog.alberta.ca) for the Thermo 55i CH4/NMHC analysers: a zero/span cycle is required every day; zero air 20 min, span 20 min, and the remaining 20 min flagged "Ambient Return"; the data system flags the hour as calibration rather than sample data. Monthly multipoint calibration and annual provincial audit are separate. This is consistent with the observed one-hour 'Z' token about every 25 h. The SOP does not name the token letter or the clock time; both remain inferred from the data pattern and should be confirmed with WBEA.
