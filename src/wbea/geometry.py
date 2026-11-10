import numpy as np, pandas as pd, itertools
from .config import ROOT

def stations():
    c = pd.read_csv(ROOT / "metadata" / "stations_official_2024.csv").set_index("station_id")
    return {s: (r.latitude_deg_n, r.longitude_deg_e) for s, r in c.iterrows()}

def haversine_km(a, b):
    la1, lo1, la2, lo2 = map(np.deg2rad, (*a, *b))
    return 6371.0088 * 2 * np.arcsin(np.sqrt(np.sin((la2 - la1) / 2) ** 2 +
                                             np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2))

def bearing_deg(a, b):
    """Initial bearing from a toward b, degrees clockwise from north."""
    la1, lo1, la2, lo2 = map(np.deg2rad, (*a, *b)); dl = lo2 - lo1
    return (np.rad2deg(np.arctan2(np.sin(dl) * np.cos(la2),
                                  np.cos(la1) * np.sin(la2) - np.sin(la1) * np.cos(la2) * np.cos(dl))) + 360) % 360

def pair_table(names, max_km=None):
    xy = stations(); rows = []
    for a, b in itertools.combinations(names, 2):
        d = haversine_km(xy[a], xy[b])
        if max_km is None or d <= max_km:
            rows.append(dict(i=a, j=b, km=d, bearing=bearing_deg(xy[a], xy[b])))
    return pd.DataFrame(rows)
