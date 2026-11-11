# Methods notes (moved out of Table 2 at the editorial revision)
These rules belong in the Methods text (Section 3), not in Table 2:
- **Missing values:** hours flagged Z (zero/span), C (calibration) or '.' (invalid, including maintenance) are treated as missing, never as zero. No imputation.
- **Station eligibility:** stations with fewer than 50% valid hourly CH4 values in the confirmation period are excluded (AMS 2: 41.2%). No exclusion was applied in the development period.
- **Pair eligibility:** station pairs within 30 km; pairs with fewer than 100 wind-eligible hours in either flow direction are dropped (none in 2026; 21 pairs).
- **Wind:** 10 m sensor when valid, otherwise 20 m; converted from km/h to m/s.
- **Comparison windows:** where development and confirmation years are compared, matching 1 January - 30 September windows are used.
- **ERA5:** used as an independent stability proxy (boundary-layer height) and for descriptive sensitivity analyses only.
