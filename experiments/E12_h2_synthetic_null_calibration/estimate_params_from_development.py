"""One-off estimation of synthetic WIND-generator parameters from DEVELOPMENT-period wind (2021-2025, Jan-Sep).
No methane values and no 2026 data are read. Output: synthetic_params.json (committed; the simulator needs only
this file). Regional wind = AMS 5 composite wind (20 m); station deviations relative to it."""
import sys, json, pathlib, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "src"))
from wbea.io import load_dev
from wbea.wind import composite
ST = ["AMS 1", "AMS 5", "AMS 6", "AMS 7", "AMS 9", "AMS 11", "AMS 13", "AMS 14", "AMS 18", "AMS 23", "AMS 30"]
P = load_dev(ST); idx = P["AMS 5"].index; jan_sep = idx.month <= 9
W = {s: composite(P[s]) for s in ST}; r = W["AMS 5"]
season = np.select([idx.month <= 3, idx.month <= 6], [0, 1], 2)
sec = (np.round(r.wd / 45.0) % 8)
out = {"source": "development wind 2021-2025 Jan-Sep; AMS 5 composite (regional); no methane, no 2026 data",
       "sectors_deg_from": [0, 45, 90, 135, 180, 225, 270, 315], "transition": [], "stationary": [],
       "logspeed_mean_season_hour": [], "logspeed_ar1_phi": None, "logspeed_resid_sd": None}
for s_ in range(3):
    m = jan_sep & (season == s_); a = sec[m].to_numpy(); prev = sec.shift(1)[m].to_numpy()
    ok = np.isfinite(a) & np.isfinite(prev); T = np.ones((8, 8))                       # +1 smoothing
    np.add.at(T, (prev[ok].astype(int), a[ok].astype(int)), 1); T /= T.sum(1, keepdims=True)
    out["transition"].append(T.round(5).tolist())
    out["stationary"].append((np.bincount(a[np.isfinite(a)].astype(int), minlength=8) / np.isfinite(a).sum()).round(4).tolist())
    ls = np.log(r.ws[m].clip(lower=0.3)); out["logspeed_mean_season_hour"].append(ls.groupby(idx[m].hour).mean().round(4).tolist())
lsall = np.log(r.ws.clip(lower=0.3)); mu = lsall.groupby([season, idx.hour]).transform("mean"); res = (lsall - mu)[jan_sep]
out["logspeed_ar1_phi"] = round(float(res.autocorr(1)), 4); out["logspeed_resid_sd"] = round(float(res.std()), 4)
dev, spd = [], []
for s in ST:
    if s == "AMS 5": continue
    d = np.degrees(np.angle(np.exp(1j * np.deg2rad(W[s].wd - r.wd))))[jan_sep]; d = d[np.isfinite(d) & (r.ws[jan_sep] >= 1)]
    dev.append(dict(station=s, mean_offset_deg=float(np.mean(d)), sd_deg=float(np.std(d))))
    spd.append(float((W[s].ws / r.ws)[jan_sep & (r.ws >= 1)].median()))
dv = pd.DataFrame(dev); out["station_dir_offset_sd_deg"] = round(float(dv.mean_offset_deg.std()), 2)
out["station_dir_hourly_sd_deg"] = round(float(dv.sd_deg.median()), 2)
out["station_speed_ratio_range"] = [round(float(np.min(spd)), 3), round(float(np.max(spd)), 3)]
out["wind_missing_fraction_regional"] = round(float(r.ws[jan_sep].isna().mean()), 4)
(pathlib.Path(__file__).parent / "synthetic_params.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k not in ("transition", "logspeed_mean_season_hour")}, indent=1))
print("persistence (diag) by season:", [np.round(np.diag(np.array(t)), 2).tolist() for t in out["transition"]])
