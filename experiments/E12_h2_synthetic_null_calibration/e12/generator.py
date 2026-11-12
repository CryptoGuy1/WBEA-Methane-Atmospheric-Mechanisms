"""E12 synthetic network generator (EXPERIMENT_PLAN.md sections 3-4). Synthetic data only; wind parameters come
from synthetic_params.json (estimated once from development wind). CH4 in ppm (levels)."""
import json, pathlib, numpy as np, pandas as pd

HERE = pathlib.Path(__file__).resolve().parents[1]
PARAMS = json.loads((HERE / "synthetic_params.json").read_text())
STATIONS = ["AMS 1", "AMS 5", "AMS 6", "AMS 7", "AMS 9", "AMS 11", "AMS 13", "AMS 14", "AMS 18", "AMS 23", "AMS 30"]
N = 6552
IDX = pd.date_range("2031-01-01 01:00", periods=N, freq="h")
_t = IDX - pd.Timedelta(minutes=1)                       # hour-ending: hour ending 1 Jan 00:00 belongs to 31 Dec
MONTH, HOUR, DAY = _t.month.to_numpy(), IDX.hour.to_numpy(), ((IDX - IDX[0]).days).to_numpy()
SEASON = np.select([MONTH <= 3, MONTH <= 6], [0, 1], 2)

class Wind:
    """Toward-components u, v (m/s) as pandas Series, as consumed by wbea.h2.pair_wind."""
    def __init__(self, ws, wd_from):
        self.ws = pd.Series(ws, index=IDX); wd = pd.Series(wd_from, index=IDX)
        self.u = -self.ws * np.sin(np.deg2rad(wd)); self.v = -self.ws * np.cos(np.deg2rad(wd)); self.wd = wd

def ar1(rng, phi, sd, n=N, burn=500):
    e = rng.normal(0, sd * np.sqrt(1 - phi ** 2), n + burn); x = np.empty(n + burn); x[0] = rng.normal(0, sd)
    for t in range(1, n + burn): x[t] = phi * x[t - 1] + e[t]
    return x[burn:]

def regional_wind(rng, tilt=False, diurnal=False):
    T = [np.array(m) for m in PARAMS["transition"]]
    if tilt:                                                   # N2a/N2b: winter toward from-N, summer toward from-S
        T = [t.copy() for t in T]
        for s, col in ((0, 0), (2, 4)):
            T[s][:, col] *= 3.0; T[s] /= T[s].sum(1, keepdims=True)
    sec = np.empty(N, int); sec[0] = rng.choice(8, p=np.array(PARAMS["stationary"][0]) / sum(PARAMS["stationary"][0]))
    u = rng.random(N)
    for t in range(1, N):
        sec[t] = min(np.searchsorted(np.cumsum(T[SEASON[t]][sec[t - 1]]), u[t]), 7)     # clamp inside loop (fix, DEVIATIONS D1)
    sec = np.minimum(sec, 7); wd = (45.0 * sec + rng.uniform(-22.5, 22.5, N)) % 360
    mu = np.array(PARAMS["logspeed_mean_season_hour"])[SEASON, HOUR]
    ws = np.exp(mu + ar1(rng, PARAMS["logspeed_ar1_phi"], PARAMS["logspeed_resid_sd"])).clip(0.3)
    if diurnal:
        night = (HOUR >= 21) | (HOUR <= 6); ws = np.where(night, ws * 0.6, ws).clip(0.3)
        flip = night & (rng.random(N) < 0.3); wd = np.where(flip, (wd + 180) % 360, wd)
    return ws, wd

def station_winds(rng, ws, wd):
    off = rng.normal(0, PARAMS["station_dir_offset_sd_deg"], len(STATIONS)); lo, hi = PARAMS["station_speed_ratio_range"]
    ratio = rng.uniform(lo, hi, len(STATIONS)); W = {}
    for k, s in enumerate(STATIONS):
        d = (wd + off[k] + rng.normal(0, PARAMS["station_dir_hourly_sd_deg"], N)) % 360
        v = (ws * ratio[k] * np.exp(rng.normal(0, 0.1, N))).clip(0.3)
        miss = rng.random(N) < 0.005; W[s] = Wind(np.where(miss, np.nan, v), np.where(miss, np.nan, d))
    return W

def positions_km(coords):
    lat0 = np.mean([c[0] for c in coords.values()]); lon0 = np.mean([c[1] for c in coords.values()])
    return {s: np.array([(c[1] - lon0) * 111.32 * np.cos(np.deg2rad(lat0)), (c[0] - lat0) * 110.57]) for s, c in coords.items()}

def lag_series(x, d):
    """x(t - d) for array-valued fractional delays d (linear interpolation; NaN outside range)."""
    t = np.arange(N) - d; i0 = np.floor(t).astype(int); f = t - i0
    ok = (i0 >= 0) & (i0 + 1 < N); out = np.full(N, np.nan)
    out[ok] = (1 - f[ok]) * x[i0[ok]] + f[ok] * x[i0[ok] + 1]; return out

def generate(scenario, seed, coords, pair_wind_fn=None, pairs=None, amp=0.0, lag=1):
    """Return dict(ch4=DataFrame[ppm], winds={station: Wind}, scenario, seed)."""
    rng = np.random.default_rng(seed)
    tilt = scenario in ("N2a", "N2b"); diurnal = scenario == "N3"
    ws, wd = regional_wind(rng, tilt=tilt, diurnal=diurnal); W = station_winds(rng, ws, wd)
    S = ar1(rng, 0.9, 1.0) + np.cos(2 * np.pi * (HOUR - 4) / 24); S = (S - S.mean()) / S.std()
    c = ar1(rng, 0.97, 0.05); X = {}
    phis = rng.uniform(0.85, 0.97, len(STATIONS)) if scenario == "N3" else rng.uniform(0.6, 0.9, len(STATIONS))
    sds = rng.uniform(0.03, 0.06, len(STATIONS)); winter = SEASON == 0
    for k, s in enumerate(STATIONS):
        e = ar1(rng, phis[k], sds[k]); cc = c.copy()
        if tilt:
            e = np.where(winter, e * np.sqrt(2), e); cc = np.where(winter, cc * np.sqrt(2) + 0.1, cc)
        X[s] = 2.0 + 0.05 * S + cc + e
        if scenario == "N3":
            X[s] = X[s] + rng.uniform(0.02, 0.08) * np.cos(2 * np.pi * (HOUR - 4) / 24)
    if scenario == "N1a":
        g = ar1(rng, 0.8, 0.06); lam = rng.uniform(0.5, 1.5, len(STATIONS)); d = rng.integers(0, 4, len(STATIONS))
        for k, s in enumerate(STATIONS): X[s] = X[s] + lam[k] * lag_series(g, np.full(N, float(d[k])))
    if scenario == "N2b":
        g = ar1(rng, 0.8, 0.06); lat = np.array([coords[s][0] for s in STATIONS]); rank = (-lat).argsort().argsort() / (len(STATIONS) - 1)
        for k, s in enumerate(STATIONS):
            X[s] = X[s] + np.where(winter, np.nan_to_num(lag_series(g, np.full(N, float(np.round(3 * rank[k]))))), 0.0)
    if scenario == "N1b":
        g = ar1(rng, 0.8, 0.06); pos = positions_km(coords)
        toward = np.deg2rad((wd + 180) % 360); unit = np.column_stack([np.sin(toward), np.cos(toward)])
        for s in STATIONS:
            tau = np.clip((unit @ pos[s]) / (3.6 * ws), -6, 6); X[s] = X[s] + lag_series(g, tau)
    if scenario.startswith("P1"):
        q = {s: ar1(rng, 0.7, 1.0) for s in STATIONS}
        for s in STATIONS: X[s] = X[s] + amp * q[s]
        for _, r in pairs.iterrows():
            up, cs = pair_wind_fn(W[r.i], W[r.j], r.bearing)
            al = (up >= 1) & (cs >= 0.707); rv = (up <= -1) & (cs <= -0.707)
            if lag == "transit":                                   # P1T (DEVIATIONS D3): lag = clip(round(tau_ij(t)), 1, 3) h
                with np.errstate(invalid="ignore", divide="ignore"):
                    L = np.clip(np.round(np.nan_to_num(r.km / (3.6 * np.abs(up)), nan=1.0)), 1, 3).astype(int)
                qi = np.choose(L - 1, [np.r_[np.zeros(l), q[r.i][:-l]] for l in (1, 2, 3)])
                qj = np.choose(L - 1, [np.r_[np.zeros(l), q[r.j][:-l]] for l in (1, 2, 3)])
                X[r.j] = X[r.j] + np.where(al, 0.8 * amp * qi, 0.0); X[r.i] = X[r.i] + np.where(rv, 0.8 * amp * qj, 0.0)
                continue
            X[r.j] = X[r.j] + np.where(al, 0.8 * amp * np.nan_to_num(np.r_[np.full(lag, np.nan), q[r.i][:-lag]]), 0.0)
            X[r.i] = X[r.i] + np.where(rv, 0.8 * amp * np.nan_to_num(np.r_[np.full(lag, np.nan), q[r.j][:-lag]]), 0.0)
    CH = pd.DataFrame(X, index=IDX)
    CH = CH.mask(rng.random(CH.shape) < 0.03)
    if scenario == "N3":
        off = rng.integers(0, 6, len(STATIONS))
        for k, s in enumerate(STATIONS):
            zero_hour = ((DAY + off[k]) % 6) + 1; CH.loc[(HOUR == zero_hour), s] = np.nan
        CH.loc[MONTH >= 7, "AMS 23"] = np.nan
    return dict(ch4=CH, winds=W, scenario=scenario, seed=seed)
