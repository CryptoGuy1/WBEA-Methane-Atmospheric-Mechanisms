"""Build the canonical development station-hour panel (2021-01-01 01:00 .. 2025-12-02 00:00, MST hour-ending).
Streams each raw WBEA workbook in time order and STOPS at the first row after the cutoff:
no confirmation-period (sealed) value is read. Raw tokens for every non-numeric cell are preserved.
Usage: python build_dev_panel.py <part 0|1|2>   (three parts run in parallel)"""
import openpyxl, glob, sys, hashlib, json, pandas as pd

CUT = pd.Timestamp('2025-12-02 00:00')
USE = ['AMS 1', 'AMS 2', 'AMS 5', 'AMS 6', 'AMS 7', 'AMS 9', 'AMS 11', 'AMS 13', 'AMS 14', 'AMS 18', 'AMS 23', 'AMS 30']
FILES = sorted(glob.glob('/home/claude/raw_station/WBEA_Station_Data_2021_2026/*/*.xlsx')) + \
        sorted(glob.glob('/home/claude/raw_ext/WBEA_FinalData_export_26110918*/*.xlsx'))
OUT = '/mnt/user-data/outputs/wbea_repo/data/dev'


def one(f):
    ws = openpyxl.load_workbook(f, read_only=True)['Data']
    it = ws.iter_rows(values_only=True)
    hdr = [next(it) for _ in range(8)]
    st = hdr[6][1]
    if st not in USE:
        return st, None
    cols = list(hdr[7])
    keep = [k for k, c in enumerate(cols) if c not in (None, '')]
    rows = []
    for r in it:
        if not r[0] or str(r[0])[:2] != '20':
            break
        if pd.Timestamp(r[0]) > CUT:          # seal: stop before any confirmation-period row
            break
        rows.append([r[k] for k in keep])
    names = [cols[k] for k in keep]
    df = pd.DataFrame(rows, columns=names)
    out = pd.DataFrame({'time_mst_hour_ending': pd.to_datetime(df[names[0]]), 'station': st})
    for c in names[1:]:
        s = df[c].astype(str)
        num = pd.to_numeric(s, errors='coerce')
        out[c] = num
        out[c + '__token'] = s.where(num.isna(), '')   # raw token retained when value is not numeric
    return st, out


if __name__ == '__main__':
    part = int(sys.argv[1])
    res = {}
    for f in FILES[part::3]:
        st, out = one(f)
        if out is None:
            continue
        out.to_parquet(f'{OUT}/{st.replace(" ", "")}.parquet', index=False)
        res[st] = dict(source=f.split('/')[-1], sha256=hashlib.sha256(open(f, 'rb').read()).hexdigest(),
                       rows=len(out), first=str(out.time_mst_hour_ending.min()),
                       last=str(out.time_mst_hour_ending.max()))
    json.dump(res, open(f'/home/claude/build_{part}.json', 'w'), indent=1)
