"""Synthetic demonstration network with KNOWN mechanisms (no WBEA data):
 - regional level rises with a stability index S (accumulation), with coefficient `beta_s` per SD;
 - an advected tracer moves along a north-south line of stations with transit time d / U (advection);
 - stations sit 6 km apart; wind alternates between northerly and southerly regimes."""
import numpy as np, pandas as pd

def make_network(n_days=180, n_stations=6, spacing_km=6.0, beta_s=0.05, advect_amp=0.08, seed=0):
    rng = np.random.default_rng(seed); n = n_days * 24
    idx = pd.date_range("2030-01-01 01:00", periods=n, freq="h"); hour = idx.hour.to_numpy()
    lat0, lon0 = 57.0, -111.5
    coords = {f"S{k + 1}": (lat0 + k * spacing_km / 110.57, lon0) for k in range(n_stations)}   # S1 south ... Sn north
    S = np.zeros(n); e = rng.normal(size=n)
    for t in range(1, n): S[t] = 0.9 * S[t - 1] + 0.45 * e[t]
    S += 0.8 * np.cos(2 * np.pi * (hour - 4) / 24); S = (S - S.mean()) / S.std()               # stable at night
    regime = np.repeat(rng.integers(0, 2, n // 48 + 1), 48)[:n]                               # 2-day wind regimes
    wd = np.where(regime == 0, 0.0, 180.0) + rng.normal(0, 15, n)                              # from north or from south
    ws = np.clip(np.exp(rng.normal(np.log(2.0), 0.4, n)) * (1 - 0.25 * (S > 1)), 0.3, None)
    q = np.zeros(n + 24); eq = rng.normal(size=n + 24)
    for t in range(1, n + 24): q[t] = 0.85 * q[t - 1] + eq[t]
    common = beta_s * S + 0.02 * np.cumsum(rng.normal(0, 0.05, n)) / np.sqrt(np.arange(1, n + 1))
    data = {}
    for k, name in enumerate(coords):
        # position along the flow: for northerly wind (from north) flow goes north -> south, so northern stations are upstream
        pos = np.where(regime == 0, (n_stations - 1 - k), k) * spacing_km
        delay = np.round(pos / (3.6 * ws)).astype(int).clip(0, 23)
        adv = advect_amp * q[np.arange(n) + 24 - delay]
        ch4 = 2.0 + common + adv + rng.normal(0, 0.03, n)
        miss = rng.random(n) < 0.04; ch4[miss] = np.nan
        data[name] = pd.DataFrame({"ch4_ppm": ch4, "ws_ms": ws * np.exp(rng.normal(0, 0.05, n)), "wd_from_deg": (wd + rng.normal(0, 5, n)) % 360}, index=idx)
    return dict(index=idx, coords=coords, stations=data, stability=pd.Series(S, index=idx), truth=dict(beta_s=beta_s, advect_amp=advect_amp))
