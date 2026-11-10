# Methodological decision log
Status labels: DEV = development decision (2021-2025 data); FROZEN = applies to confirmation.

| ID | Date | Decision | Reason | Evidence available at the time | Status |
|---|---|---|---|---|---|
| D-01 | 2026-11-10 | Development cutoff 2025-12-02 00:00 MST hour-ending | Matches all prior analyses; researcher decision | Researcher instruction | FROZEN |
| D-02 | 2026-11-10 | Working timestamp convention: hour-ending MST (UTC-7, no DST) | ERA5 t2m averaged over the represented hour fits hour-ending better at 12/12 stations (r 0.952-0.972 vs 0.919-0.957); no DST discontinuity | results/R1/era5_cells_and_timestamp_test.csv | DEV; replace with WBEA documentation when available |
| D-03 | 2026-11-10 | Composite station wind: 10 m where valid, else 20 m; AMS 5 and AMS 14 use 20 m; height recorded per hour | AMS 9 and AMS 18 switch between 10 m and 20 m sensors by year; single-height rule loses up to 58% of hours | composite_wind_*.csv | DEV; height-stratified sensitivity required |
| D-04 | 2026-11-10 | H2 family rule unchanged (all pairs <= 30 km); membership recomputed on 12 stations: 27 pairs | Rule pre-specified in v2.0; membership follows mechanically from official coordinates | pairwise_geometry_66_pairs.csv | FROZEN rule; 12 pairs involve stations never analysed (AMS 9, 30) |
| D-05 | 2026-11-10 | Exclude AMS 15, 32, 503 (no valid data 2021-2025). Keep AMS 14 and 18 for H1/H3; they have no H2 pair (nearest 38 km and 92 km) | No development baseline possible | ch4_completeness_station_year.csv | FROZEN |
| D-06 | 2026-11-10 | ERA5: nearest 0.25 deg cell per station; treated as a regional proxy | Cells are shared (AMS 1/13/23/30; AMS 2/5/11; AMS 6/7) and offsets reach 14 km | era5_cells_and_timestamp_test.csv | DEV |
| D-07 | 2026-11-10 | Coordinates: official 2024 site documents (researcher-verified) | Replace provisional script coordinates; AMS 11 moved ~0.7 km vs provisional | WBEA_12_station_official_2024_coordinates.csv | DEV until relocation history checked |
| D-08 | 2026-11-10 | Z, C, SP, '.' all treated as missing; Z additionally modelled as non-random missingness (01:00-06:00) | Official WBEA definitions not yet obtained; do not infer meaning from timing | data/meta/flag_dictionary.csv | DEV |
| D-09 | 2026-11-10 | NMHC zeros treated as left-censored | Alberta AMD DQ 4-J sets valid negatives to 0 | flag_dictionary.csv | DEV |
| D-10 | 2026-11-10 | H1 primary response keeps the pre-registered v2.0 station set (AMS 1, 2, 6, 7, 11, 13, 23; Kmin 5); the 11-station expanded set is a sensitivity | Expanded network must not change the estimand after the fact; AMS 14 and 18 lie 40-150 km south | R1 only (no H1 results on new stations) | FROZEN |
| D-11 | 2026-11-10 | Smoke flag for sensitivity: FIRMS >=10 non-persistent vegetation detections (nominal/high) within 100 km of 57.0N 111.5W on the day, OR network-median PM2.5 > 30 ug/m3 in the hour | Remove persistent industrial pixels found in R1; PM2.5 covers short-range smoke | R1 FIRMS inventory; no methane-smoke relation examined | DEV |
| D-12 | 2026-11-10 | Repository: data and PDFs kept outside git; checksums in manifests; guarded loader + seal tests | WBEA data "for authorized use only"; reproducibility | - | FROZEN |
| D-13 | 2026-11-10 | Drop AMS 14 as a stability proxy; H1 alternative proxies are AMS 1 dT (10-2 m) and ERA5 BLH | AMS 14 AT10 and AT_Delta are 100% missing in the export | E02 Q1 | DEV |
| D-14 | 2026-11-10 | Treat Z gaps as missing at random given hour and month (revises D-08 wording); complete-case analysis allowed in hour-conditioned models; Manski bounds still reported for unconditional rates | Bracketing CH4 at Z hours equals that at matched non-Z hours (12/12 CIs include 0) | E02 Q4 | DEV |
| D-15 | 2026-11-10 | No station-month exclusion in primary analyses; station-months < 75% valid excluded as a sensitivity | Avoid data-dependent exclusion; 19 of 720 station-months affected | E02 Q2 | FROZEN |
