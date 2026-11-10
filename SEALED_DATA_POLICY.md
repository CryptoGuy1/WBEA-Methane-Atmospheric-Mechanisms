# Sealed confirmation data (E08)

**Sealed period:** 2025-12-02 01:00 to 2026-11-09 00:00 MST (hour-ending).

## How the seal is enforced
1. No raw export (the only files containing sealed methane values) is in this repository.
2. Development code may only call `wbea.io.load_dev()`, which verifies panel checksums and raises
   `SealViolation` on any timestamp after the cutoff.
3. `tests/test_seal.py` fails if any development script references raw exports or a `sealed/` path.
4. The E08 splitter will be written and committed **after** the protocol freeze tag (`protocol-freeze`).

## Limitation of this enforcement
The raw archives remain readable in the analyst's working environment (they were uploaded there and
cannot be deleted from it). The seal is therefore procedural and code-level, not cryptographic. Any
access is logged in this file.

## Disclosure of confirmation-period information already seen
| When | What | Values analysed? |
|---|---|---|
| Prior audit (Nov 2026) | AMS 2 CH4-only file: count of valid hours after 2025-12-02 (3,379); identity of 2023-2025 overlap | No 2026 values analysed |
| R1 (2026-11-10) | Header rows of all 15 exports (station, date range, variable names) | No |
| R1 | ERA5 arrays including 2026 loaded with the file; all computations restricted to development hours | Meteorology only; not a methane outcome |
| R1 | FIRMS 2026 counts displayed (9,374 detections; 59 local fire days; 23 after persistent-pixel mask) | Fire data only; not a methane outcome |
