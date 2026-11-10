# Data provenance
| Source | Content | Period | Acquired | Checksums | Status |
|---|---|---|---|---|---|
| WBEA continuous data export (Final Data, 1 h), 13 stations | CH4, NMHC, THC, meteorology | 2021-01-01 to 2026-11-09 | exported 2026-11-09 | manifests/station_exports_2021_2026_manifest.csv | raw; contains sealed period |
| WBEA export, AMS 5 and AMS 6 | as above, AMS 5 tower 20-90 m | same | exported 2026-11-09 | same manifest | raw; contains sealed period |
| Earlier 8-station exports (prior audit) | as above | 2021-01-01 to 2025-12-02 | before 2026-11-09 | prior audit | identical values on overlap (R1) |
| ERA5 single levels time series (Copernicus CDS) | u/v10, u/v100, fg10, t2m, d2m, blh, sp, tp | 2021-01-01 00Z to 2026-11-04 23Z; 55.5-57.5N, 112-110.75W | 2026-11-10 | manifests/archives_sha256.csv | accepted |
| ERA5 (first two downloads) | wrong longitude sign / small box | - | 2026-11-09/10 | manifests/archives_sha256.csv | rejected / superseded |
| NASA FIRMS VIIRS NOAA-20 C2 archive + NRT | active fire detections, Alberta | 2021-01-01 to 2026-11-09 | 2026-11-10 | manifests/archives_sha256.csv | accepted (sensitivity) |
| WBEA 2024 site documents | coordinates (12 stations), AMS 5 equipment | 2024 | researcher-verified | metadata/stations_official_2024.csv | relocation history pending |
| Alberta AMD Chapter 6 (2014) | validation-code rules | - | web | metadata/flag_dictionary.csv | official, provincial |

Development panel: `data/dev/*.parquet`, built by `src/build/build_dev_panel.py`, SHA-256 in
`manifests/dev_panel_SHA256SUMS.txt`; 12 stations x 43,104 hours; raw tokens preserved in `<variable>__token` columns.
