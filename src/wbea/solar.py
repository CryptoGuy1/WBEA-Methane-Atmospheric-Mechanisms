import numpy as np, pandas as pd

def elevation_deg(index_mst, lat=57.0, lon=-111.5):
    """Solar elevation at the MIDPOINT of an MST hour-ending interval (NOAA approximate algorithm)."""
    t = (index_mst - pd.Timedelta(minutes=30)) + pd.Timedelta(hours=7)          # to UTC midpoint
    doy = t.dayofyear.to_numpy(); hr = t.hour.to_numpy() + t.minute.to_numpy() / 60
    g = 2 * np.pi / 365 * (doy - 1 + (hr - 12) / 24)
    decl = (0.006918 - 0.399912 * np.cos(g) + 0.070257 * np.sin(g) - 0.006758 * np.cos(2 * g)
            + 0.000907 * np.sin(2 * g) - 0.002697 * np.cos(3 * g) + 0.00148 * np.sin(3 * g))
    eqt = 229.18 * (0.000075 + 0.001868 * np.cos(g) - 0.032077 * np.sin(g) - 0.014615 * np.cos(2 * g)
                    - 0.040849 * np.sin(2 * g))
    tst = hr * 60 + eqt + 4 * lon
    ha = np.deg2rad(tst / 4 - 180); la = np.deg2rad(lat)
    cz = np.sin(la) * np.sin(decl) + np.cos(la) * np.cos(decl) * np.cos(ha)
    return pd.Series(np.rad2deg(np.arcsin(np.clip(cz, -1, 1))), index=index_mst)
