# Publication asset QA: Supplementary Figures S1-S23 and Tables TS1-TS14
## Figures
| Check | Result |
|---|---|
| All 23 figure families produced | yes: S1-S23, each as PDF, SVG and 600 dpi PNG (69 files) |
| Width / fonts / vector | 174.5 mm (S19: 104.7 mm); fonts embedded in every PDF; 0 raster images except the S6 hexbin density layer (by design) |
| Text inside page | automated `pdftotext -bbox` check: all 23 pass |
| Visual inspection | every figure inspected. Fixed during QA: rose-label collisions (S1), longitude ticks (S1), legend over data (S4, S12, S13, S17, S18), clipped labels (S2, S15, S16, S18, S20), annotation over bars (S20, S21), fractional count ticks (S21), near-invisible category (S14) |
| Numerical annotations | embedded assertions against saved files, e.g. pooled D 0.1285 (S8), 27/66 pairs (S1), 1/5 kernel classes (S10), continuous detection 0.8333 (S11), 7,951 episodes and 4,412 without an assessable pair (S14), H3 share 0.0269 (S15), r = 0.94 (S16), surrogate counts K (S20, S21), H1 n = 40,334 (S6, S7) |
| Units and labels | D dimensionless; rates in %; ppm and pp stated; transit classes in h; descriptive labels only (no experiment or scenario codes) |
| Colour accessibility | blue/orange/grey palette; cividis/viridis sequential; no red-green contrasts |
| Panel ordering | (a)-(e) in reading order |
| Captions | caption caveats per figure in `figure_manifest.csv` (`caption_caveats`); captions themselves are written at the Supplement stage |

## Tables
| Check | Result |
|---|---|
| All 14 tables produced | TS1-TS14 (`tables/*.tex`; generator `scripts/make_tables.py`) |
| LaTeX quality | compiled in an Elsevier CAS harness (not the Supplement): **0 errors, 0 overfull boxes**, 15 pages; pages inspected visually |
| Content | title, period and status line in every caption; footnotes on methods, units, intervals and sources |
| Intervals | only saved intervals are shown. Missing ones are marked n/a or "not saved" (e.g. the 2026 joint contemporaneous H1 CI; no 2026 pair CIs), never computed |
| Registered vs exploratory | stated in every caption (development / registered confirmation / post-confirmation exploratory) |
| Negative and inconclusive outcomes | retained: kernel FAILED, typology NOT SUPPORTED, elevated wind INCONCLUSIVE (TS6); H3 not supported or not confirmed (TS7, TS8); calibration inconclusive and falsification (TS11); cross-year controls not calibration (TS13); E15 A6 not evaluable (TS14) |
| Corrections during QA | TS1 wind variable selection; TS4 duplicate E11 rows removed (identical values at 4-dp rounding, verified); TS6 'nan' cell; negative zeros; column widths; harness shell-escape bug (the harness only, not the tables) |

## Documentation errors from REPRODUCIBILITY_GAPS.md: resolution in the publication assets
- **Development pooled D:** 0.1285 used everywhere (S8, TS5).
- **E12 N2a Wilson lower limit:** 3.2465% printed (TS11), with the earlier report's rounding noted.
- **E11 H1 range:** TS4 note explains that E11 re-tabulates the E04 estimates (rounded); no separate range is claimed.
- **Registered H3 share and 2026 next-day CI:** authoritative values used (TS8); the diagnostic versions are labelled as such (TS10).
- **Protocol descriptive-output gaps:** disclosed in the TS8 notes.
- **Superseded terminology** (Manski, smoke hours, isolated, cold/warm halves): replaced in all assets.
- **Experiment reports themselves were not edited:** experiment directories must remain byte-identical.

## Integrity
- Regression suite (repository, E12, E13, E14, E15): **70 passed**.
- `src/wbea`, `config`, protocol and E08 runner vs `protocol-freeze`: **0** changed lines.
- E08 confirmation outputs vs `e08-confirmation`: **0**.
- All `experiments/` vs pinned source `1788301`: **0** changed lines; no untracked files.
- Audit directory vs `9cc8672`: **0**.
- No WBEA hourly data added. The only new data file is aggregate wind-rose sector frequencies (`data/figS01_windrose_sectors.csv`).

## OPEN (not resolvable without external input or authorisation)
1. WBEA meanings of missing-data codes Z and '.' (S2, TS1).
2. Redistribution decision for the S6 / main Fig. 4a residual file; repository visibility.
3. Branch integration (E14, E15, manuscript and publication branches are unmerged; `main` lacks them).
4. Overleaf manuscript content (duplication status UNVERIFIED).
5. AMS 2 outage cause; station relocations; final validated 2026 data and the pre-declared re-run; `netmech` licence.
