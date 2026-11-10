"""Derive external inputs for development (restricted to the development period):
 - data/external/era5_station_cells.parquet : ERA5 variables at each station's nearest cell, MST hour-ending index
 - data/external/firms_fire_days.csv         : D-11 FIRMS fire days (non-persistent vegetation detections)
Raw ERA5/FIRMS files are external reanalysis/satellite products, not sealed methane data."""
import sys, glob, hashlib, pathlib, numpy as np, pandas as pd, netCDF4 as nc
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "src"))
from wbea.config import CFG
from wbea.geometry import stations
from wbea.smoke import firms_fire_days
ERA5 = "/home/claude/raw_ext/era5c/reanalysis-era5-single-levels-timeseries-sfcgbn6qfny.nc"
FIRMS = "/home/claude/raw_ext/firms/NASA_EarthData/fire_archive_J1V-C2_841773.csv"
OUT = ROOT / "data" / "external"; OUT.mkdir(parents=True, exist_ok=True)
CUT = pd.Timestamp(CFG["split"]["dev_end"]); START = pd.Timestamp(CFG["split"]["dev_start"])

ds = nc.Dataset(ERA5); lat = np.array(ds["latitude"][:]); lon = np.array(ds["longitude"][:])
t_utc = pd.to_datetime(np.array(ds["valid_time"][:]), unit="s")
t_mst = t_utc - pd.Timedelta(hours=7)                   # ERA5 instantaneous at top of hour, expressed in MST
keep = (t_mst >= START - pd.Timedelta(hours=1)) & (t_mst <= CUT)
rows = []
for s, (la, lo) in stations().items():
    i = int(np.argmin(abs(lat - la))); j = int(np.argmin(abs(lon - lo)))
    d = {"time_mst_hour_ending": t_mst[keep], "station": s}
    for v in ["t2m", "d2m", "blh", "u10", "v10", "u100", "v100", "sp", "fg10"]:
        x = np.array(ds[v][:, i, j])[keep]
        d[v] = x - 273.15 if v in ("t2m", "d2m") else x
    df = pd.DataFrame(d).set_index("time_mst_hour_ending")
    # Station hour-ending h covers (h-1, h]; ERA5 instantaneous values at h-1 and h averaged (D-02 convention)
    num = [c for c in df.columns if c != "station"]
    df[num] = (df[num] + df[num].shift(1)) / 2
    rows.append(df.loc[START:CUT].reset_index())
era = pd.concat(rows); era.to_parquet(OUT / "era5_station_cells.parquet", index=False)
fd = firms_fire_days(FIRMS, radius_km=CFG["smoke"]["firms_radius_km"], min_det=CFG["smoke"]["firms_min_detections"],
                     persistent_months=CFG["smoke"]["firms_persistent_months"])
fd = pd.Series(sorted(fd[fd <= CUT.normalize()]), name="fire_day"); fd.to_csv(OUT / "firms_fire_days.csv", index=False)
with open(ROOT / "manifests" / "external_derived_SHA256SUMS.txt", "w") as f:
    for p in sorted(OUT.iterdir()):
        f.write(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n")
print(len(era), "ERA5 station-hours;", len(fd), "fire days in development period")
