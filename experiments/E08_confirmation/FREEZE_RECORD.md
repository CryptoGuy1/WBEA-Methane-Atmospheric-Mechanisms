# E08 protocol-freeze record

Frozen protocol: `PROTOCOL_E08_DRAFT_v2.md` (approved by the researcher, 2026-11-10). This file is part of the tagged commit; the commit SHA itself is recorded after tagging in `experiments/E08_confirmation/CONFIRMATION_RUN.md`.

## Release checks completed before the freeze
1. Descriptive E10 uses development-period (2021-2025) standardisation of upstream residual changes, as in E10. Unsupported development conclusion preserved.
2. ERA5 location configurable (`config/project.toml` [data]); checksum verified at runtime.
3. Confirm mode enabled in both runners behind an operational guard (HEAD must be the `protocol-freeze` commit; clean tree). No estimator, statistic, criterion, bootstrap rule, threshold or seed changed.
4. Tests: 39/39 pass. Primary 2025 dry run re-run: all 39 compared result fields identical to `dryrun_2025_final` (archived in `dryrun_2025_release`).

## File hashes (SHA-256)
| File | SHA-256 |
|---|---|
| `requirements.txt` | 25ecaa8fab6b9985f3ca6d9f9b7691bf9e41dc1d6ae14b37fc9b76d6573dd3fe |
| `config/project.toml` | 09d3c49acff0ae2fd8cf05709c1b1c21dc65eea8e22c20c9be5c4f0a3491952a |
| `PROTOCOL_E08_DRAFT_v2.md` | 9fae852d1c1d3c7dd5d6168871968cade8b59088eee94715831a88803cff6a87 |
| `src/wbea/e08.py` | c5d0d457204b30e37cb86b86b7ae3480166ebfdd707508e45fdda13574370dc4 |
| `src/wbea/h2.py` | dd1e2dce836061c52cdb35a1c6388219d5b1ea778232ee7bd55f58cb9f465fa6 |
| `src/wbea/io.py` | fccf45fd1fefb2517ed55e7c8f1f74e078ef476005621675aeee502dfd85d25e |
| `src/wbea/wind.py` | 4a446277cacb6ed0d21fc71b266009e522fcccf4e01f00d00a741362c36cba98 |
| `src/wbea/geometry.py` | 39b77a5bff3c184c4063f75af526463e7798957337d67b720141675e525da247 |
| `src/wbea/solar.py` | 68bf2a227ee9e0467318f18f4a98194bbdd776a631b2ca1305aa71237df3849e |
| `src/build/build_e08_panel.py` | 2d135e4d21a87d0a64dd09ddbc6b4621ec428ac6c25d12d2d74f1a14d9e03da7 |
| `experiments/E08_confirmation/run_e08.py` | 8158802bdfddb732b2b2b75d2f5f47abc87dbb3e82a4f98640acba7ee7292aae |
| `experiments/E08_confirmation/run_e08_descriptive.py` | 631c5902c9fe47a2e5936bf0a47997ff390ce321d9d7ed0d11b61cfac11e3b42 |
| `manifests/station_exports_2021_2026_manifest.csv` | 56f90193259f486ebf8e033504d0c17a1d3c6231add76b0ce060ecc5e964cfc6 |
| `manifests/dev_panel_SHA256SUMS.txt` | 6372bebc7228bafa514765b40e99710ce9c3861bd008c4251c54dd9d9beb6630 |
| `manifests/archives_sha256.csv` | e0feda38f98bc6b009cfc50d31da51f72a7f6eba0f5b956f26411b0b7a40427d |

## Data-source checksums
- 12 source workbooks: `PROTOCOL_E08_DRAFT_v2.md` section 1 (re-verified by the splitter before any 2026 row is written).
- ERA5: `/home/claude/raw_ext/era5c/reanalysis-era5-single-levels-timeseries-sfcgbn6qfny.nc` d35f35349a00ff0652f14c5ca25169cec093477a1c7b6982ef25896821f877c5 (archive 48b741e5c32ed3ff9358879859669b4.zip, see manifests).
- Development panel: `manifests/dev_panel_SHA256SUMS.txt`.

## Confirmation settings (from the frozen protocol)
Window 2026-01-01 01:00 to 2026-10-01 00:00 MST hour-ending; development comparison years 2021-2025; seeds base 20261190 (+1 H1, +2 H2 centroid, +3 H3, +5 ERA5 proxy, +6 six-regime, +7 F5); Python 3.12.3.
