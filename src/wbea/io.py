"""Guarded data access. Development code may ONLY use load_dev(); it reads the derived development
panel (data/dev/*.parquet), verifies checksums against manifests/dev_panel_SHA256SUMS.txt, and raises
if any timestamp is later than the frozen development cutoff. Raw exports (which contain the sealed
confirmation period) are never read by development code."""
import hashlib, pandas as pd
from .config import ROOT, CFG

CUT = pd.Timestamp(CFG["split"]["dev_end"])

class SealViolation(RuntimeError):
    pass

def _checksums():
    out = {}
    for line in (ROOT / "manifests" / "dev_panel_SHA256SUMS.txt").read_text().split("\n"):
        if line.strip():
            h, f = line.split()
            out[f] = h
    return out

def load_dev(stations=None, verify=True):
    """Return {station: DataFrame indexed by MST hour-ending time} for the development period only."""
    stations = stations or CFG["stations"]["usable"]
    sums = _checksums() if verify else {}
    out = {}
    for s in stations:
        f = ROOT / "data" / "dev" / f"{s.replace(' ', '')}.parquet"
        if verify and hashlib.sha256(f.read_bytes()).hexdigest() != sums[f.name]:
            raise RuntimeError(f"checksum mismatch for {f.name}")
        d = pd.read_parquet(f).set_index("time_mst_hour_ending")
        if d.index.max() > CUT:
            raise SealViolation(f"{s}: data after development cutoff {CUT}")
        out[s] = d
    return out

def ch4_panel(P):
    return pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in P})

def load_era5():
    """ERA5 at each station's nearest cell, averaged over the station's hour (development period only)."""
    d = pd.read_parquet(ROOT / "data" / "external" / "era5_station_cells.parquet")
    if d.time_mst_hour_ending.max() > CUT:
        raise SealViolation("ERA5 derived file extends past the development cutoff")
    return {s: g.set_index("time_mst_hour_ending").drop(columns="station") for s, g in d.groupby("station")}

def load_fire_days():
    f = pd.read_csv(ROOT / "data" / "external" / "firms_fire_days.csv", parse_dates=["fire_day"]).fire_day
    if (f > CUT).any():
        raise SealViolation("fire days past cutoff")
    return pd.DatetimeIndex(f)
