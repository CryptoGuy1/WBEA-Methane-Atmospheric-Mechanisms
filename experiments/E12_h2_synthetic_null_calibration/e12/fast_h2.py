"""Fast evaluation of the FROZEN H2 statistic over all admissible whole-day circular wind shifts.
Circular wind shifts only rotate the aligned/reversed masks (wbea.h2.sets is elementwise in the wind), and the frozen
weights depend on the multiset of (mask, tau) values, so they are shift-invariant. The masked moment sums for every
shift are circular cross-correlations of six per-hour moment series with each mask, computed by FFT. Parity with the
frozen loop is tested in tests/test_e12.py. Alternative nulls and the ungated baseline are EXPLORATORY statistics."""
import sys, pathlib, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT / "src"))
from wbea import h2, e08
from scipy.stats import norm

LAGS = (1, 2, 3)

def moment_matrix(dri, drj):
    """(N, 36): for lag l and order o, columns n, a, b, aa, bb, ab with zeros where any of the four values is missing
    (the frozen total_sums requires dR_i(t-l), dR_j(t), dR_j(t-l), dR_i(t) all finite)."""
    cols = []
    for l in LAGS:
        a1 = np.r_[np.full(l, np.nan), dri[:-l]]; a2 = np.r_[np.full(l, np.nan), drj[:-l]]
        v = np.isfinite(a1) & np.isfinite(drj) & np.isfinite(a2) & np.isfinite(dri)
        for a, b in ((a1, drj), (a2, dri)):
            a0, b0 = np.where(v, a, 0.0), np.where(v, b, 0.0)
            cols += [v.astype(float), a0, b0, a0 * a0, b0 * b0, a0 * b0]
    return np.column_stack(cols)

def corr_from(S):
    n, sa, sb, saa, sbb, sab = (S[..., k] for k in range(6))
    with np.errstate(invalid="ignore", divide="ignore"):
        return (n * sab - sa * sb) / np.sqrt((n * saa - sa ** 2) * (n * sbb - sb ** 2))

def D_from_sums(Sal, Srv, w):
    """Sal, Srv: (K, 36) sums -> D (K,), using the frozen D definition."""
    out = 0.0
    for li in range(3):
        ra = corr_from(Sal[:, li * 12: li * 12 + 6]) - corr_from(Sal[:, li * 12 + 6: li * 12 + 12])
        rr = corr_from(Srv[:, li * 12: li * 12 + 6]) - corr_from(Srv[:, li * 12 + 6: li * 12 + 12])
        out = out + w[li] * (ra - rr)
    return out

def circ_sums(M, mask, shifts_h):
    """sum_t M[t] * mask[(t - s) mod N] for each s in shifts_h (FFT circular cross-correlation)."""
    FM = np.fft.rfft(M, axis=0); Fm = np.conj(np.fft.rfft(mask.astype(float)))
    full = np.fft.irfft(FM * Fm[:, None], n=M.shape[0], axis=0)
    S = full[np.asarray(shifts_h) % M.shape[0]]; S[:, ::6] = np.round(S[:, ::6]); return S

def pair_inputs(X, i, j, stations, Wi, Wj, km, bearing):
    Ri, Rj = h2.lpo_residual_levels(X, i, j, stations); dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
    up, cs = h2.pair_wind(Wi, Wj, bearing); al, rv, tau = h2.sets(km, up, cs)
    return dict(dri=dri, drj=drj, al=al, rv=rv, w=h2.weights(tau, al, rv), M=moment_matrix(dri, drj))

def evaluate(X, winds, stations, fam, season_blocks, trunc_days=60, run_alternatives=True):
    """Frozen H2 (primary) + exploratory alternatives + baseline for one synthetic dataset."""
    N = len(X); ndays = N // 24; K = e08.admissible_shifts(ndays); prim_shifts = np.r_[0, K] * 24
    cov = X.notna().mean(); excluded = [s for s in stations if cov[s] < 0.5]              # E08 station-coverage rule
    stations = [s for s in stations if s not in excluded]; fam = fam[fam.i.isin(stations) & fam.j.isin(stations)]
    D0, Dn, Ds, Dsn, Dt, Dtn, B = [], [], [], [], [], [], []; dropped = 0
    for _, r in fam.iterrows():
        p = pair_inputs(X, r.i, r.j, stations, winds[r.i], winds[r.j], r.km, r.bearing)
        if p["al"].sum() < 100 or p["rv"].sum() < 100: dropped += 1; continue
        D = D_from_sums(circ_sums(p["M"], p["al"], prim_shifts), circ_sums(p["M"], p["rv"], prim_shifts), p["w"])
        D0.append(D[0]); Dn.append(D[1:])
        if run_alternatives:
            # within-season circular shift (same k in every season block), k = 14..76 days
            ks = np.arange(14, 77); sal = 0; srv = 0
            for a, b in season_blocks:
                sh = np.r_[0, ks] * 24; sal = sal + circ_sums(p["M"][a:b], p["al"][a:b], sh); srv = srv + circ_sums(p["M"][a:b], p["rv"][a:b], sh)
            Dw = D_from_sums(sal, srv, p["w"]); Ds.append(Dw[0]); Dsn.append(Dw[1:])
            # truncated (non-circular) time shift: methane window [W, N-W); wind offset by k days
            Wh = trunc_days * 24; win = np.arange(Wh, N - Wh); kk = np.r_[0, np.arange(-trunc_days, -13), np.arange(14, trunc_days + 1)]
            Mw = p["M"][win]; sal = np.vstack([Mw.T @ p["al"][win - 24 * k] for k in kk]); srv = np.vstack([Mw.T @ p["rv"][win - 24 * k] for k in kk])
            Dtt = D_from_sums(sal, srv, p["w"]); Dt.append(Dtt[0]); Dtn.append(Dtt[1:])
        # baseline B1: ungated asymmetry over all valid hours, naive Fisher-z on lag 1
        allm = np.ones(N, bool); Sall = (p["M"] * allm[:, None]).sum(0)[None, :]
        A = sum(p["w"][li] * (corr_from(Sall[:, li * 12: li * 12 + 6]) - corr_from(Sall[:, li * 12 + 6: li * 12 + 12]))[0] for li in range(3))
        r1, r2, n1 = corr_from(Sall[:, 0:6])[0], corr_from(Sall[:, 6:12])[0], Sall[0, 0]
        z = (np.arctanh(r1) - np.arctanh(r2)) / np.sqrt(2 / max(n1 - 3, 1)); B.append((A, bool(abs(z) > 1.96)))
    out = dict(n_pairs=len(D0), dropped=dropped, excluded_stations=excluded, evaluable=len(D0) >= 10)
    if not out["evaluable"]: return out
    def pool(d0, dn):
        dn = np.array(dn).T; pooled, pn, w = e08.pooled_inverse_null_variance(np.array(d0), dn)
        return pooled, e08.finite_shift_p(pooled, pn), dn.shape[0]
    out["D_primary"], out["p_primary"], out["K_primary"] = pool(D0, Dn)
    if run_alternatives:
        out["D_season"], out["p_season"], out["K_season"] = pool(Ds, Dsn)
        out["D_trunc"], out["p_trunc"], out["K_trunc"] = pool(Dt, Dtn)
    out["B1_mean_abs_A"] = float(np.mean([abs(a) for a, _ in B])); out["B1_share_pairs_naive_sig"] = float(np.mean([s for _, s in B]))
    out["pair_D"] = D0
    return out
