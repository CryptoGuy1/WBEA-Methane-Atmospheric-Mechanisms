"""E08 data splitter (PROTOCOL_E08_DRAFT_v2, section 6). Verifies each raw workbook's SHA-256 against the
acquisition manifest, streams rows in time order, keeps ONLY rows with start <= t <= end (MST hour-ending,
inclusive on both ends) and stops at the first row after `end`. Raw tokens are preserved. Writes one parquet
per station plus SHA256SUMS and a split log. Raises on checksum mismatch, out-of-order or duplicate timestamps.

Usage: python build_e08_panel.py --start "2025-01-01 01:00" --end "2025-10-01 00:00" --out <dir> [--roots ...]"""
import argparse, hashlib, json, pathlib, sys, openpyxl, pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
USE = ["AMS 1", "AMS 2", "AMS 5", "AMS 6", "AMS 7", "AMS 9", "AMS 11", "AMS 13", "AMS 14", "AMS 18", "AMS 23", "AMS 30"]

class SplitError(RuntimeError):
    pass

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()

def split_workbook(path, start, end, expected_sha=None):
    """Return (station, DataFrame) with rows start <= t <= end. Never reads past the first row after `end`."""
    if expected_sha is not None and sha256(path) != expected_sha:
        raise SplitError(f"checksum mismatch: {path}")
    ws = openpyxl.load_workbook(path, read_only=True)["Data"]; it = ws.iter_rows(values_only=True)
    hdr = [next(it) for _ in range(8)]; station = hdr[6][1]; cols = list(hdr[7])
    keep = [k for k, c in enumerate(cols) if c not in (None, "")]; rows, prev = [], None
    for r in it:
        if not r[0] or str(r[0])[:2] != "20": break               # footer
        t = pd.Timestamp(r[0])
        if prev is not None and t <= prev: raise SplitError(f"non-increasing timestamp {t} in {path}")
        prev = t
        if t > end: break                                           # strict end: nothing after `end` is kept or read further
        if t >= start: rows.append([r[k] for k in keep])
    ws.parent.close()
    names = [cols[k] for k in keep]; df = pd.DataFrame(rows, columns=names)
    out = pd.DataFrame({"time_mst_hour_ending": pd.to_datetime(df[names[0]]), "station": station})
    for c in names[1:]:
        s = df[c].astype(str); num = pd.to_numeric(s, errors="coerce"); out[c] = num; out[c + "__token"] = s.where(num.isna(), "")
    return station, out

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--start", required=True); ap.add_argument("--end", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--manifest", default=str(ROOT / "manifests" / "station_exports_2021_2026_manifest.csv"))
    ap.add_argument("--roots", nargs="+", default=["/home/claude/raw_station/WBEA_Station_Data_2021_2026", "/home/claude/raw_ext"])
    a = ap.parse_args(argv); start, end = pd.Timestamp(a.start), pd.Timestamp(a.end)
    man = pd.read_csv(a.manifest); man = man[man.station.isin(USE)]
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True); log = []
    for _, m in man.iterrows():
        name = pathlib.Path(m.file).name; hits = [p for r in a.roots for p in pathlib.Path(r).rglob(name)]
        if len(hits) != 1: raise SplitError(f"{m.station}: expected one raw file named {name}, found {len(hits)}")
        st, df = split_workbook(hits[0], start, end, m.sha256)
        if st != m.station: raise SplitError(f"station mismatch {st} vs {m.station}")
        if len(df) and (df.time_mst_hour_ending.min() < start or df.time_mst_hour_ending.max() > end): raise SplitError("boundary violation")
        f = out / f"{st.replace(' ', '')}.parquet"; df.to_parquet(f, index=False)
        log.append(dict(station=st, source=name, source_sha256=m.sha256, rows=len(df), first=str(df.time_mst_hour_ending.min()),
                        last=str(df.time_mst_hour_ending.max()), output_sha256=sha256(f)))
    pd.DataFrame(log).to_csv(out / "split_log.csv", index=False)
    (out / "SHA256SUMS.txt").write_text("".join(f"{r['output_sha256']}  {r['station'].replace(' ', '')}.parquet\n" for r in log))
    print(json.dumps(dict(start=str(start), end=str(end), stations=len(log), rows=int(sum(r["rows"] for r in log))), indent=1))

if __name__ == "__main__":
    sys.exit(main())
