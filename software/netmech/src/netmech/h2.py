"""Copied mechanically from the WBEA project (src/wbea/h2.py, frozen at tag protocol-freeze) by
software/netmech/build_from_frozen.py. Only the configuration import is replaced by explicit defaults. Do not edit by hand."""
"""H2 directional-coupling estimator (logic identical to experiments/E05_directional_coupling/run_e05.py,
specification D-26). Shared by E06 and E08."""
import numpy as np, pandas as pd
DEFAULTS = dict(max_pair_km=30.0, lags=[1, 2, 3], u_min_ms=1.0, max_tau_h=3.0, align_cos=0.707, kmin_other_stations=4)

H2 = DEFAULTS; LAGS = H2["lags"]

def lpo_residual_levels(X, i, j, stations, kmin=H2["kmin_other_stations"]):
    others = [s for s in stations if s not in (i, j)]
    m = X[others].median(1).where(X[others].notna().sum(1) >= kmin)
    return (X[i] - m).to_numpy(), (X[j] - m).to_numpy()

def pair_wind(Wi, Wj, bearing, shift_h=0):
    u = ((Wi.u + Wj.u) / 2).to_numpy(); v = ((Wi.v + Wj.v) / 2).to_numpy()
    if shift_h:
        u = np.roll(u, shift_h); v = np.roll(v, shift_h)
    phi = np.deg2rad(bearing); upar = u * np.sin(phi) + v * np.cos(phi); sp = np.hypot(u, v)
    with np.errstate(invalid="ignore", divide="ignore"):
        return upar, upar / sp

def sets(km, upar, cosang, extra=None):
    with np.errstate(invalid="ignore", divide="ignore"):
        tau = km / (3.6 * np.abs(upar))
    ok = np.isfinite(tau) & (tau <= H2["max_tau_h"]) & (np.abs(upar) >= H2["u_min_ms"])
    al = ok & (upar > 0) & (cosang >= H2["align_cos"]); rv = ok & (upar < 0) & (cosang <= -H2["align_cos"])
    if extra is not None:
        al &= extra; rv &= extra
    return al, rv, tau

def weights(tau, al, rv):
    t = tau[al | rv]; w = np.array([np.maximum(0, 1 - np.abs(l - t)).mean() for l in LAGS])
    return w / w.sum() if w.sum() > 0 else np.full(len(LAGS), 1 / len(LAGS))

def total_sums(dri, drj, al, rv):
    out = np.zeros((2, len(LAGS), 2, 6))
    for si, m in enumerate((al, rv)):
        for li, l in enumerate(LAGS):
            a1 = np.r_[np.full(l, np.nan), dri[:-l]]; a2 = np.r_[np.full(l, np.nan), drj[:-l]]
            ok = m & np.isfinite(a1) & np.isfinite(drj) & np.isfinite(a2) & np.isfinite(dri)
            for oi, (a, b) in enumerate(((a1[ok], drj[ok]), (a2[ok], dri[ok]))):
                out[si, li, oi] = [len(a), a.sum(), b.sum(), (a * a).sum(), (b * b).sum(), (a * b).sum()]
    return out

def corr_from(s):
    n, sa, sb, saa, sbb, sab = np.moveaxis(s, -1, 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (n * sab - sa * sb) / np.sqrt((n * saa - sa ** 2) * (n * sbb - sb ** 2))

def D_stat(dri, drj, al, rv, w):
    r = corr_from(total_sums(dri, drj, al, rv)); rho = r[:, :, 0] - r[:, :, 1]
    return float(np.sum(w * (rho[0] - rho[1])))

def lag_profile(dr_up, dr_down, mask, lags=(0, 1, 2, 3)):
    """corr(dR_up(t-l), dR_down(t)) over hours t in mask."""
    out = []
    for l in lags:
        a = np.r_[np.full(l, np.nan), dr_up[:-l]] if l else dr_up
        ok = mask & np.isfinite(a) & np.isfinite(dr_down)
        out.append(np.corrcoef(a[ok], dr_down[ok])[0, 1] if ok.sum() > 50 else np.nan)
    return np.array(out)

def centroid(r):
    p = np.maximum(np.nan_to_num(r), 0)
    return float((np.arange(len(p)) * p).sum() / p.sum()) if p.sum() > 0 else np.nan
