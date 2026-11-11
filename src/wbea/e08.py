"""E08 confirmation library (PROTOCOL_E08_DRAFT_v2). Pure decision-rule functions are separated from the
estimators so that every numerical rule can be unit-tested on synthetic inputs."""
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from . import h2
from .config import CFG

# =====================================================================  pure decision rules
def finite_shift_p(observed, null_values):
    """p = (1 + #{T_k >= T_obs}) / (K + 1)."""
    null_values = np.asarray(null_values)
    return (1 + int((null_values >= observed).sum())) / (len(null_values) + 1)

def admissible_shifts(n_days, min_days=14):
    return np.arange(min_days, n_days - min_days + 1)

def h1_decision(primary_ci, b1_joint, b_nc, b_nc_ci, ratio=0.5):
    """(a) primary CI entirely above 0; (b) NOT [CI(b_nc) excludes 0 AND |b_nc| >= ratio * b1_joint]."""
    a = primary_ci[0] > 0
    nc_flag = (b_nc_ci[0] > 0 or b_nc_ci[1] < 0) and abs(b_nc) >= ratio * b1_joint
    return dict(a_primary_ci_above_0=bool(a), b_negative_control_ok=bool(not nc_flag), confirmed=bool(a and not nc_flag))

def centroid_rule(centroids, n_per_bin, possum_per_bin, diff_ci, min_n=500):
    """Ordered lag-centroid trend allowing limited inversions (v2, D-68). Bins estimable if n >= min_n and the
    positive-part profile sums > 0. Requires >= 4 estimable bins incl. the first; Spearman (average ranks) >= 0.9
    with 5 bins or >= 0.8 with 4 bins (at most one adjacent inversion); c_last - c_first CI > 0.
    Tied centroids count as non-increasing (handled by average ranks lowering rho)."""
    c = np.asarray(centroids, float); n = np.asarray(n_per_bin); ps = np.asarray(possum_per_bin)
    est = (n >= min_n) & (ps > 0) & np.isfinite(c)
    out = dict(estimable_bins=int(est.sum()), first_bin_estimable=bool(est[0]))
    if est.sum() < 4 or not est[0]:
        return dict(out, rho=np.nan, rho_threshold=np.nan, evaluable=False, met=False)
    idx = np.where(est)[0]; rho = spearmanr(idx, c[idx])[0] if np.ptp(c[idx]) > 0 else 0.0
    thr = 0.9 if len(idx) >= 5 else 0.8
    met = bool(rho >= thr - 1e-12 and diff_ci[0] > 0)
    return dict(out, rho=float(rho), rho_threshold=thr, diff_ci_lo=float(diff_ci[0]), evaluable=True, met=met)

def kitagawa_groups(ha, xa, hb, xb, groups):
    """Kitagawa split (a minus b) over fixed merged groups. Returns (composition, within, total, estimable);
    not estimable if any group has zero hours in either unit."""
    Ha = np.array([ha[g].sum() for g in groups], float); Hb = np.array([hb[g].sum() for g in groups], float)
    if (Ha == 0).any() or (Hb == 0).any():
        return np.nan, np.nan, np.nan, False
    Xa = np.array([xa[g].sum() for g in groups]); Xb = np.array([xb[g].sum() for g in groups])
    pa, pb, qa, qb = Ha / Ha.sum(), Hb / Hb.sum(), Xa / Ha, Xb / Hb
    return float(((pa - pb) * (qa + qb) / 2).sum()), float(((pa + pb) * (qa - qb) / 2).sum()), \
           float(Xa.sum() / Ha.sum() - Xb.sum() / Hb.sum()), True

def projection_share(comp, total):
    comp, total = np.asarray(comp), np.asarray(total)
    return float((comp * total).sum() / (total ** 2).sum())

def merge_groups(ha, hb, minh=50):
    """E07 merge rule (D-40), applied once on full data: within each day/night half, pool wind classes of any
    (stability, day/night) group with a sparse cell; if still sparse, pool the whole half."""
    out = []
    for nt in (0, 1):
        g1 = []
        for st in range(3):
            grp = [st * 6 + w * 2 + nt for w in range(3)]
            if all(min(ha[c], hb[c]) >= minh for c in grp): g1 += [[c] for c in grp]
            else: g1.append(grp)
        if any(min(ha[g].sum(), hb[g].sum()) < minh for g in g1):
            g1 = [[st * 6 + w * 2 + nt for st in range(3) for w in range(3)]]
        out += g1
    return [np.array(x) for x in out]

def h3_bootstrap_summary(shares, estimable, max_nonest=0.10):
    shares = np.asarray(shares, float); estimable = np.asarray(estimable, bool)
    frac = 1 - estimable.mean(); s = shares[estimable]
    lo, hi = (np.percentile(s, 2.5), np.percentile(s, 97.5)) if len(s) else (np.nan, np.nan)
    return dict(nonestimable_fraction=float(frac), ci_lo=float(lo), ci_hi=float(hi), evaluable=bool(frac <= max_nonest))

# =====================================================================  estimators
def block_ids(index, days=14):
    return ((index - index[0]).days // days).to_numpy()

def fe_coefs(arr, cell):
    """OLS of column 0 on columns 1.. after absorbing cell means (FWL)."""
    n = np.bincount(cell); m = np.vstack([np.bincount(cell, arr[:, j], minlength=len(n)) for j in range(arr.shape[1])]).T / np.maximum(n, 1)[:, None]
    Z = arr - m[cell]; return np.linalg.lstsq(Z[:, 1:], Z[:, 0], rcond=None)[0]

def h1_estimate(Y, S, Snext, LU, idx, nboot, rng):
    cellraw = (idx.year * 10000 + idx.month * 100 + idx.hour).to_numpy(); blk = block_ids(idx)
    ub = np.unique(blk); pos = {b: np.where(blk == b)[0] for b in ub}
    d1 = np.column_stack([Y, S, LU]); ok1 = np.isfinite(d1).all(1)
    d2 = np.column_stack([Y, S, Snext, LU]); ok2 = np.isfinite(d2).all(1)
    def fit(d, ok, ii):
        ii = ii[ok[ii]]; return fe_coefs(d[ii], pd.factorize(cellraw[ii])[0])
    allidx = np.arange(len(Y)); b_p = fit(d1, ok1, allidx)[0]; b_j = fit(d2, ok2, allidx)
    bp, bj, bn = [], [], []
    for _ in range(nboot):
        ii = np.concatenate([pos[b] for b in rng.choice(ub, len(ub))])          # same draw for both models (paired)
        bp.append(fit(d1, ok1, ii)[0]); c = fit(d2, ok2, ii); bj.append(c[0]); bn.append(c[1])
    bp, bj, bn = map(np.array, (bp, bj, bn))
    return dict(n_primary=int(ok1.sum()), n_joint=int(ok2.sum()), b1_primary=float(b_p),
                b1_primary_ci=(float(np.percentile(bp, 2.5)), float(np.percentile(bp, 97.5))),
                b1_joint=float(b_j[0]), b_nc=float(b_j[1]), b_nc_ci=(float(np.percentile(bn, 2.5)), float(np.percentile(bn, 97.5))),
                ratio_nc=float(b_j[1] / b_j[0]), ratio_nc_ci=(float(np.percentile(bn / bj, 2.5)), float(np.percentile(bn / bj, 97.5))))

BINS = [0, 0.5, 1.0, 1.5, 2.0, 3.0]

def h2_block_sums(dri, drj, binmask, blk, nblk):
    S = np.zeros((nblk, len(BINS) - 1, 4, 6))
    for li, l in enumerate(range(4)):
        a = np.r_[np.full(l, np.nan), dri[:-l]] if l else dri
        ok = np.isfinite(a) & np.isfinite(drj) & (binmask >= 0); key = blk[ok] * (len(BINS) - 1) + binmask[ok]
        av, bv = a[ok], drj[ok]
        for c, val in enumerate((np.ones_like(av), av, bv, av * av, bv * bv, av * bv)):
            S[:, :, li, c] = np.bincount(key, val, minlength=nblk * (len(BINS) - 1)).reshape(nblk, -1)
    return S

def h2_centroids(Slist, w=None):
    nb_ = len(BINS) - 1; num = np.zeros((nb_, 4)); den = np.zeros((nb_, 4))
    for S in Slist:
        T = S.sum(0) if w is None else np.tensordot(w, S, axes=(0, 0))
        n, sa, sb, saa, sbb, sab = np.moveaxis(T, -1, 0)
        with np.errstate(invalid="ignore", divide="ignore"):
            r = (n * sab - sa * sb) / np.sqrt((n * saa - sa ** 2) * (n * sbb - sb ** 2))
        use = (n > 50) & np.isfinite(r); num += np.where(use, n * r, 0); den += np.where(use, n, 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        prof = num / den
    p = np.maximum(np.nan_to_num(prof), 0); possum = p.sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        c = (p * np.arange(4)).sum(1) / possum
    nlag0 = sum(S[:, :, 0, 0].sum(0) for S in Slist) if w is None else None
    return c, possum, nlag0
