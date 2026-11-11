"""Pair geometry for arbitrary station coordinates (independent of WBEA metadata)."""
import itertools, numpy as np, pandas as pd

def haversine_km(a, b):
    la1, lo1, la2, lo2 = map(np.deg2rad, (*a, *b))
    return 6371.0088 * 2 * np.arcsin(np.sqrt(np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2))

def bearing_deg(a, b):
    la1, lo1, la2, lo2 = map(np.deg2rad, (*a, *b)); dl = lo2 - lo1
    return (np.rad2deg(np.arctan2(np.sin(dl) * np.cos(la2), np.cos(la1) * np.sin(la2) - np.sin(la1) * np.cos(la2) * np.cos(dl))) + 360) % 360

def pair_table(coords, max_km=30.0):
    """coords: {name: (lat, lon)}. Returns pairs within max_km with distance and bearing i -> j."""
    rows = [dict(i=a, j=b, km=haversine_km(coords[a], coords[b]), bearing=bearing_deg(coords[a], coords[b]))
            for a, b in itertools.combinations(list(coords), 2)]
    t = pd.DataFrame(rows); return t[t.km <= max_km].reset_index(drop=True)

class Wind:
    """Minimal wind container with toward-components u, v (m/s), as used by netmech.h2.pair_wind."""
    def __init__(self, ws_ms, wd_from_deg):
        ws, wd = pd.Series(ws_ms), pd.Series(wd_from_deg)
        self.ws = ws; self.u = -ws * np.sin(np.deg2rad(wd)); self.v = -ws * np.cos(np.deg2rad(wd))
