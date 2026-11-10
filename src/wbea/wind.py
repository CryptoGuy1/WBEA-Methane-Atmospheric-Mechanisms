"""Composite station wind (decision D-03): 10 m where valid, else 20 m. Returns toward-components."""
import numpy as np, pandas as pd

def composite(d):
    def get(h):
        ws, wd = f"WS{h} (km/h)", f"WD{h} (deg)"
        return (d[ws] / 3.6, d[wd]) if ws in d and wd in d else (None, None)
    ws10, wd10 = get(10); ws20, wd20 = get(20)
    if ws10 is None:
        ws, wd = ws20, wd20; h = pd.Series(20.0, index=d.index)
    else:
        use10 = ws10.notna() & wd10.notna()
        ws = ws10.where(use10, ws20) if ws20 is not None else ws10
        wd = wd10.where(use10, wd20) if wd20 is not None else wd10
        h = pd.Series(10.0, index=d.index).where(use10, 20.0 if ws20 is not None else np.nan)
    ok = ws.notna() & wd.notna()
    u = -ws * np.sin(np.deg2rad(wd)); v = -ws * np.cos(np.deg2rad(wd))
    return pd.DataFrame({"ws": ws.where(ok), "wd": wd.where(ok), "u": u.where(ok), "v": v.where(ok),
                         "height_m": h.where(ok)})
