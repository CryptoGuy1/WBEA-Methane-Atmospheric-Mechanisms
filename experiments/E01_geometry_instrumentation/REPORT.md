# E01 Station geometry and instrumentation verification

**Status:** complete for geometry and sensor configuration; relocation and instrument history pending WBEA site documents (11 of 12 stations). Decision criterion (geometry verified or bounded before H2): met for geometry; history bounded by year-stratified sensitivity.

## Method
Official 2024 coordinates (researcher-verified), haversine distances and initial bearings for all 66 pairs, frozen H2 rule (<= 30 km), eligibility counts with the frozen parameters in `config/project.toml` (|U_par| >= 1 m/s, alignment cos >= 0.707, tau <= 3 h, >= 4 other stations). Composite station wind (D-03). This re-implements R1 with the repository library; eligibility counts match R1 exactly for all 27 pairs.

## Results
- 66 pairs; **27 in the H2 family** (2.7-27.3 km). Minimum eligible hours: 4,511 aligned, 2,660 reversed (AMS 1-9).
- 70% of family bearings lie within 30 deg of north-south (valley axis).
- AMS 14 and AMS 18 have no H2 pair (nearest 38 km and 92 km).
- Sensors: wind at 10 m (8 stations), 20 m (AMS 5, AMS 14), alternating 10/20 m (AMS 9, AMS 18). Stability proxies usable: AMS 5 tower T90 - T20 and AMS 1 T10 - T2 only (AMS 14 gradient empty, E02).
- AMS 5 (site document, March 2024): Thermo 55i THC/CH4/NMHC analyser installed 2021; all tower T/RH and ultrasonic wind sensors replaced 2022.
- Wind roses (Fig. 1): AMS 1 dominated by north and south flow along the valley; AMS 5 by south-south-east; AMS 7 (Athabasca valley in Fort McMurray) by south-east and north-west.

## Limitations
- Relocation and instrument histories unverified for 11 stations; 2024 coordinates are assumed valid for 2021-2025.
- Station heights above ground for gas inlets are known only for AMS 5.

## Figure
Main Figure 1 (`figures/figure01_network_geometry`).
