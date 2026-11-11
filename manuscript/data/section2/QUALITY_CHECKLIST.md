# Scientific-quality checklist (Section 2 outputs)

## Data and analysis
| Check | Status |
|---|---|
| Coordinates equal official 2024 metadata (12 stations) | PASS (automated) |
| Pair list equals frozen E08 output and the <= 30 km rule (21 pairs) | PASS (automated) |
| 2026 completeness recomputed from hourly indicators equals frozen summary | PASS (max diff 4e-5; frozen stored to 4 dp) |
| Hour-ending MST day assignment; 24 h per station-day; hour accounting | PASS (automated) |
| Missing never treated as zero; no CH4 <= 0 | PASS (automated) |
| No inference, p-values, hypothesis outcomes or experiment IDs in tables | PASS (automated) |

## Figure production
| Check | Status |
|---|---|
| Vector PDF/SVG with embedded fonts and no raster images; PNG at 600 dpi | PASS (automated; pdffonts/pdfimages) |
| Colour-blind-friendly palette (blue/orange, sequential classes); no significance colours; no transport arrows | PASS (visual) |
| Overlaps, clipping, label legibility at 180 mm (Fig. 1, 2, S1) and 90 mm (Fig. 2 variant) | PASS (visual inspection of renders) |
| Projection appropriate (EPSG:3978 regional, UTM 12N local), scale bars, north arrow | PASS |

## Known limitations
- No polygon for the "Athabasca oil sands region": an official boundary was not obtained.
- Station relocations before 2024 not verified.
- Font is DejaVu Sans, not Arial/Helvetica.
- No single-column version of Fig. 1.
