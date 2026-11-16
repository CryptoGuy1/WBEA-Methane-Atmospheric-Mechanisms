# Proposed Supplement outline (provisional; no prose)
**Numbering:** Supplementary figures S1-S23 and tables TS1-TS14 follow section order. Experiment figure names (e.g. "figure06") are historical identifiers and are **unrelated** to main-manuscript numbering (Figs. 1-7 plus the regime heatmap on `manuscript/section2-figures-tables`). Main-text duplication against the current Overleaf manuscript is **UNVERIFIED**.

## Assessment of the provisional ten-section structure
- **S7 has no experiment figures** (the frozen confirmation produced only result files). It is kept as a short, table-led section, because full confirmation records belong in the Supplement.
- **S9 and S10 are merged** into one post-confirmation H2 section (E13, E14, E15), since all three examine the H2 reference or magnitudes. The final section becomes "Software, reproducibility and data availability", which needs no figures.
- **E10** (episode typology) moves to S5: its classes are advection- or accumulation-compatible, so it is a transport-interpretation question.
- **Largest sections:** S5 (5 figures, 1 combined table) and S9 (4 figures, 3 tables). S5 can be reduced by combining S12 and S13 (E09) into one figure.

## Sections, mappings and required technical content
| Section | Figures | Tables | Methods detail needed (not in main text) |
|---|---|---|---|
| S1 Network, data provenance and quality | S1 (E01), S2 (E02) | TS1 completeness, TS2 pairs and eligibility | WBEA export provenance and checksums; missing-code definitions (Z, '.', C; OPEN); composite wind rule; ERA5 and FIRMS processing; PWIP flag (D-11, D-31) |
| S2 Methane excursions and observational structure | S3, S4, S5 (E03) | TS3 (or archive) | P95 excursion and episode definitions R1-R5; co-occurrence lift; Mantel and block-bootstrap procedures; F5 regime definitions and enrichment |
| S3 Atmospheric stability (H1) | S6, S7 (E04) | TS4 (+E11 H1 rows) | spline and random-forest baselines; CR1 and ERA5-proxy definitions; negative-control rule; station-contribution procedure |
| S4 Wind-conditioned directional analysis (H2, development) | S8, S9 (E05) | TS5 | random-shift development reference vs finite confirmation reference; residualisation variants; max-T procedure |
| S5 Transport interpretation and detectability | S10, S11 (E06), S12, S13 (E09), S14 (E10) | TS6 | injection models (mask-gated vs continuous source, D-39); kernel criterion (D-35) and its replacement by the ordering rule; ERA5 100 m transit and Delta SSE; typology rules and validation criteria V1-V4 |
| S6 Meteorological-regime decomposition (H3) | S15, S16 (E07) | TS7 | regime definitions; merge rule; Kitagawa identity; deweathering baseline and its failed forward validation (D-44) |
| S7 Independent confirmation and diagnostics | none (tables only) | TS8, TS9, TS10 | freeze and release procedure; seal controls; dry run; descriptive-output list. Disclose that "H1 total association" and the reduced-network development benchmark (protocol section 4 and contingency table) were not produced by E08; E15 supplies the latter post hoc |
| S8 Synthetic calibration and falsification | S17, S18, S19 (E12) | TS11 | generator (Markov winds, scenario definitions N0-N3, N1b, N2b, P1, P1T); fast exact implementation and parity; Wilson intervals; classification rules |
| S9 Post-confirmation analyses of the H2 statistic | S20, S21 (E13), S22 (E14), S23 (E15) | TS12, TS13, TS14 | within-block shift definition; cross-year construction (calendar alignment, 29 Feb removal, dependence); pooled Jan-Sep construction; decomposition paths; fixed-weight sensitivity |
| S10 Software, reproducibility and data availability | none | none | branches and tags; test suites; checksums; data restrictions; `netmech` |

## Estimated length
- **Figures:** about 23 at roughly 0.4-0.6 page each, giving 10-13 pages (fewer if S12/S13 and S17/S19 are combined).
- **Tables:** 14, giving 8-11 pages (TS5, TS9, TS11 and TS13 are long).
- **Text:** methods detail and captions, about 12-16 pages.
- **Total:** about **30-40 pages**. S5 and S9 together are about 40% of the total.
