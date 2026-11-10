"""Potential wildfire-influenced period (PWIP) flag (decisions D-11, D-31; sensitivity use only).
Combines FIRMS fire detections and PM2.5; it is NOT a direct smoke-transport measurement."""
import numpy as np, pandas as pd
from .geometry import haversine_km

def firms_fire_days(csv_path, centre=(57.0, -111.5), radius_km=100, min_det=10, persistent_months=6):
    d = pd.read_csv(csv_path, low_memory=False); d["date"] = pd.to_datetime(d.acq_date)
    if "type" in d:
        d = d[d["type"] == 0]
    d = d[d.confidence.isin(["n", "h"])]
    km = haversine_km(centre, (d.latitude.to_numpy(), d.longitude.to_numpy()))
    d = d[km <= radius_km].copy()
    d["cell"] = list(zip(d.latitude.round(2), d.longitude.round(2)))
    months = d.groupby("cell").date.apply(lambda s: s.dt.to_period("M").nunique())
    d = d[~d.cell.isin(set(months[months >= persistent_months].index))]
    n = d.groupby(d.date.dt.normalize()).size()
    return n[n >= min_det].index
