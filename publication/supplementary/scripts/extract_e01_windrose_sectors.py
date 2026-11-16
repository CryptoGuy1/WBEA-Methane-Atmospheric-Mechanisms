"""Aggregate-only extraction for Fig. S1 wind roses (E01 panels c-e). Copies run_e01.py lines 70-72 verbatim:
composite station wind direction -> 16 sectors of 22.5 deg -> relative frequency. Development data 2021-01-01 to 2025-12-02.
Writes only sector frequencies and n (no hourly values)."""
import sys, pathlib, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT / "src"))
from wbea.io import load_dev
from wbea.wind import composite
P = load_dev(); rows = []
for s in ["AMS 1", "AMS 5", "AMS 7"]:
    wd = composite(P[s]).wd.dropna(); sec = (np.round(wd / 22.5) % 16).astype(int); f = sec.value_counts(normalize=True).reindex(range(16), fill_value=0)
    rows += [dict(station=s, sector=k, centre_deg=22.5 * k, frequency=float(f[k]), n_hours=len(wd)) for k in range(16)]
pd.DataFrame(rows).to_csv(ROOT / "publication/supplementary/data/figS01_windrose_sectors.csv", index=False)
print(pd.DataFrame(rows).groupby("station").n_hours.first().to_dict())
