"""E09 (X4) - Elevated-wind sensitivity of the lag-centroid discrepancy (D-55). Development data; exploratory.
A smaller centroid discrepancy is NOT proof of a physical transport speed. The original E06 kernel criterion
remains failed regardless of the outcome.

Variants (selection wind -> hours; transport wind -> transit time, upstream side, bins):
  W0            selection W0 (station 10 m pair mean), transport W0                 [E05/E06 setting]
  W4_speed      selection W0, transport = W0 direction with ERA5-100 m speed          [speed only]
  W4_full       selection W0, transport ERA5 100 m (X4a, PRIMARY)                     [speed + direction]
  W4_resel      selection ERA5 100 m, transport ERA5 100 m (X4b)                      [selection]
  W0_dc, W4_dc  direction-consistent common sample (W0- and W4-aligned), transport W0 / W4
  T45/T75/T90   selection W0, transport AMS 5 tower wind at 45/75/90 m (supporting; one location for all pairs)
Observed centroids use real wind; reference centroids use continuous-source injections (A = 0.3, memory 180 min,
10 replicates) into real residuals analysed with all winds shifted by 182 days (as E06)."""
import sys, pathlib, numpy as np, pandas as pd
from scipy.signal import lfilter
EXP = pathlib.Path(__file__).resolve().parent; ROOT = EXP.parents[1]
sys.path.insert(0, str(ROOT / "src"))
from wbea.config import CFG
from wbea.io import load_dev, load_era5
from wbea.wind import composite
from wbea.geometry import pair_table, stations, haversine_km
from wbea import h2, runmeta
from wbea.plotstyle import plt, save

RES = EXP / "results"; FIG = EXP / "figures"; RES.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
SEED = CFG["project"]["seed"] + 9; rng = np.random.default_rng(SEED)
P = load_dev(); ST = CFG["stations"]["usable"]; idx = P["AMS 1"].index; N = len(idx)
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); X = CH - CH.loc["2021":"2023"].median()
W = {s: composite(P[s]) for s in ST}; ERA = load_era5(); A5 = P["AMS 5"]
FAM = pair_table(ST, 30.0).reset_index(drop=True)
BINS = [0, 0.5, 1.0, 1.5, 2.0, 3.0]; NBIN = len(BINS) - 1; LAGS = [0, 1, 2, 3]; SHIFT = 182 * 24
A_REF, MEM, REPS, NB = 0.3, 180, 10, 1000
BLK = ((idx - idx[0]).days // 14).to_numpy(); NBLK = BLK.max() + 1

def tower_uv(h):
    ws = A5[f"WS{h} (km/h)"].to_numpy() / 3.6; wd = np.deg2rad(A5[f"WD{h} (deg)"].to_numpy())
    return -ws * np.sin(wd), -ws * np.cos(wd)

TOWER = {h: tower_uv(h) for h in (45, 75, 90)}

def winds(a, b):
    """u, v (toward components, m/s) for each wind source, pair-specific where applicable."""
    w0 = (((W[a].u + W[b].u) / 2).to_numpy(), ((W[a].v + W[b].v) / 2).to_numpy())
    e4 = (((ERA[a].u100 + ERA[b].u100) / 2).reindex(idx).to_numpy(), ((ERA[a].v100 + ERA[b].v100) / 2).reindex(idx).to_numpy())
    sp0, sp4 = np.hypot(*w0), np.hypot(*e4)
    with np.errstate(invalid="ignore", divide="ignore"):
        k = sp4 / sp0
    return {"W0": w0, "W4": e4, "W4speed": (w0[0] * k, w0[1] * k), "T45": TOWER[45], "T75": TOWER[75], "T90": TOWER[90]}

def along(uv, phi):
    u, v = uv; up = u * np.sin(phi) + v * np.cos(phi); sp = np.hypot(u, v)
    with np.errstate(invalid="ignore", divide="ignore"):
        return up, up / sp

def aligned(km, up, cs):
    with np.errstate(invalid="ignore", divide="ignore"):
        tau = km / (3.6 * np.abs(up))
    return np.isfinite(tau) & (np.abs(up) >= 1) & (up > 0) & (cs >= 0.707) & (tau <= 3), \
           np.isfinite(tau) & (np.abs(up) >= 1) & (up < 0) & (cs <= -0.707) & (tau <= 3)

VARIANTS = {  # name: (selection wind, transport wind, subset rule)
    "W0": ("W0", "W0", None), "W4_speed": ("W0", "W4speed", None), "W4_full": ("W0", "W4", None),
    "W4_resel": ("W4", "W4", None), "W0_dc": ("W0", "W0", "dc"), "W4_dc": ("W0", "W4", "dc"),
    "T45": ("W0", "T45", None), "T75": ("W0", "T75", None), "T90": ("W0", "T90", None)}

def spec(a, b, km, phi, shift=0):
    """For each variant: aligned-hour mask (selection), eligible mask for injection, transport (upar, cos), tau bins."""
    wd = winds(a, b)
    if shift:
        wd = {k: (np.roll(v[0], shift), np.roll(v[1], shift)) for k, v in wd.items()}
    al = {}; rv = {}; tr = {}
    for k, uv in wd.items():
        up, cs = along(uv, phi); al[k], rv[k] = aligned(km, up, cs); tr[k] = (up, cs)
    out = {}
    for name, (sel, trn, sub) in VARIANTS.items():
        m_al, m_rv = al[sel].copy(), rv[sel].copy()
        if sub == "dc":
            m_al &= al["W4"]; m_rv &= rv["W4"]
        up, cs = tr[trn]
        with np.errstate(invalid="ignore", divide="ignore"):
            tau = km / (3.6 * np.abs(up))
        b_ = np.full(N, -1)
        for k_ in range(NBIN):
            b_[(tau >= BINS[k_]) & (tau < BINS[k_ + 1])] = k_
        out[name] = dict(al=m_al, el=m_al | m_rv, bin=np.where(m_al, b_, -1), up=up, cs=cs, tau=tau)
    return out, wd

def inject_continuous(Ri, Rj, up, cs, km, sd):
    q = lfilter([1.0], [1.0, -np.exp(-1.0 / MEM)], rng.standard_normal(N * 60 + 600))[600:]
    k = np.arange(N * 60); hr = k // 60; u_ = up[hr]; c_ = np.abs(np.nan_to_num(cs[hr])); ok = np.isfinite(u_)
    tau = np.minimum(km / (3.6 * np.maximum(np.abs(np.nan_to_num(u_)), 0.5)), 6.0)
    qd = 0.8 * c_ * q[np.clip(k - np.round(60 * tau).astype(int), 0, None)] * ok
    i_up = np.nan_to_num(u_) >= 0
    si = np.where(i_up, q, qd).reshape(N, 60).mean(1); sj = np.where(i_up, qd, q).reshape(N, 60).mean(1)
    sc = A_REF * sd / np.nanstd(np.diff(si))
    return np.diff(np.r_[np.nan, Ri + sc * si]), np.diff(np.r_[np.nan, Rj + sc * sj])

def block_sums(dri, drj, binmask):
    """S[blk, bin, lag, 6]: n, sa, sb, saa, sbb, sab for corr(dR_i(t-l), dR_j(t)) over aligned hours in each bin."""
    S = np.zeros((NBLK, NBIN, len(LAGS), 6))
    for li, l in enumerate(LAGS):
        a = np.r_[np.full(l, np.nan), dri[:-l]] if l else dri
        ok = np.isfinite(a) & np.isfinite(drj) & (binmask >= 0)
        key = BLK[ok] * NBIN + binmask[ok]; av, bv = a[ok], drj[ok]
        for c, val in enumerate((np.ones_like(av), av, bv, av * av, bv * bv, av * bv)):
            S[:, :, li, c] = np.bincount(key, val, minlength=NBLK * NBIN).reshape(NBLK, NBIN)
    return S

def centroids(Slist, w=None):
    """Pooled (n-weighted mean of per-pair correlations) lag profile per bin -> centroid per bin."""
    num = np.zeros((NBIN, len(LAGS))); den = np.zeros((NBIN, len(LAGS)))
    for S in Slist:
        T = S.sum(0) if w is None else np.tensordot(w, S, axes=(0, 0))
        n, sa, sb, saa, sbb, sab = np.moveaxis(T, -1, 0)
        with np.errstate(invalid="ignore", divide="ignore"):
            r = (n * sab - sa * sb) / np.sqrt((n * saa - sa ** 2) * (n * sbb - sb ** 2))
        use = (n > 50) & np.isfinite(r); num += np.where(use, n * r, 0); den += np.where(use, n, 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        prof = num / den
    p = np.maximum(np.nan_to_num(prof), 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (p * np.arange(len(LAGS))).sum(1) / p.sum(1), prof

# ---------------- observed: block sufficient statistics per variant
obsS = {v: [] for v in VARIANTS}; membership = []; dirdis = []; resid = []
for _, r in FAM.iterrows():
    phi = np.deg2rad(r.bearing); Ri, Rj = h2.lpo_residual_levels(X, r.i, r.j, ST)
    dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj]); sd = np.nanstd(dri)
    sp, wd = spec(r.i, r.j, r.km, phi)
    for v in VARIANTS:
        obsS[v].append(block_sums(dri, drj, sp[v]["bin"]))
    b0 = sp["W0"]["bin"]
    for v in VARIANTS:
        bv = sp[v]["bin"]; in0, inv = b0 >= 0, bv >= 0
        membership.append(dict(pair=f"{r.i}->{r.j}", variant=v, aligned_hours_in_bins=int(inv.sum()),
                               W0_hours_in_bins=int(in0.sum()), shared=int((in0 & inv).sum()),
                               jaccard=float((in0 & inv).sum() / max((in0 | inv).sum(), 1)),
                               same_bin_share=float((b0[in0 & inv] == bv[in0 & inv]).mean()) if (in0 & inv).any() else np.nan,
                               moved_beyond_3h=int((in0 & ~inv & (sp["W0"]["al"])).sum()) if VARIANTS[v][0] == "W0" else np.nan))
    m = sp["W0"]["al"]
    for k in ("W4", "T45", "T90"):
        u0, v0 = wd["W0"]; u1, v1 = wd[k]
        ang = np.degrees(np.abs(np.angle(np.exp(1j * (np.arctan2(u1, v1) - np.arctan2(u0, v0))))))
        a_ = ang[m & np.isfinite(ang)]
        dirdis.append(dict(pair=f"{r.i}->{r.j}", km=r.km, wind=k, median_abs_dir_diff_deg=float(np.median(a_)),
                           share_gt_45deg=float((a_ > 45).mean()), share_gt_90deg=float((a_ > 90).mean())))
    resid.append(dict(dri=dri, Ri=Ri, Rj=Rj, sd=sd, km=r.km, phi=phi, i=r.i, j=r.j))
pd.DataFrame(membership).round(4).to_csv(RES / "e09_membership_by_pair_variant.csv", index=False)
pd.DataFrame(dirdis).round(3).to_csv(RES / "e09_direction_disagreement.csv", index=False)

obs = {}; nbin = {}
for v in VARIANTS:
    c, prof = centroids(obsS[v]); obs[v] = c
    nbin[v] = sum(S[:, :, 0, 0].sum(0) for S in obsS[v])

# ---------------- reference centroids (continuous source, shifted winds)
ref = {v: [] for v in VARIANTS}
for rep in range(REPS):
    reps = {v: [] for v in VARIANTS}
    for rr in resid:
        sp, _ = spec(rr["i"], rr["j"], rr["km"], rr["phi"], SHIFT)
        for v in VARIANTS:
            dri_, drj_ = inject_continuous(rr["Ri"], rr["Rj"], sp[v]["up"], sp[v]["cs"], rr["km"], rr["sd"])
            reps[v].append(block_sums(dri_, drj_, sp[v]["bin"]))
    for v in VARIANTS:
        ref[v].append(centroids(reps[v])[0])
ref = {v: np.array(x) for v, x in ref.items()}

# ---------------- SSE, Delta and paired bootstrap
def sse(c, r):
    return np.nansum((c - r) ** 2)

boot = {v: np.empty((NB, NBIN)) for v in VARIANTS}
for b in range(NB):
    wts = np.bincount(rng.integers(0, NBLK, NBLK), minlength=NBLK).astype(float)
    for v in VARIANTS:
        boot[v][b] = centroids(obsS[v], wts)[0]
rows = []
for v in VARIANTS:
    rm = np.nanmean(ref[v], 0)
    s_b = np.array([sse(boot[v][b], ref[v][rng.integers(0, REPS)]) for b in range(NB)])
    rows.append(dict(variant=v, **{f"obs_bin{k}": obs[v][k] for k in range(NBIN)}, **{f"ref_bin{k}": rm[k] for k in range(NBIN)},
                     **{f"n_bin{k}": int(nbin[v][k]) for k in range(NBIN)}, SSE=sse(obs[v], rm),
                     SSE_ci_lo=np.percentile(s_b, 2.5), SSE_ci_hi=np.percentile(s_b, 97.5)))
tab = pd.DataFrame(rows); tab.round(4).to_csv(RES / "e09_centroids_reference_sse.csv", index=False)

def delta(base, alt):
    d = []
    for b in range(NB):
        d.append(sse(boot[base][b], ref[base][rng.integers(0, REPS)]) - sse(boot[alt][b], ref[alt][rng.integers(0, REPS)]))
    d = np.array(d); point = sse(obs[base], np.nanmean(ref[base], 0)) - sse(obs[alt], np.nanmean(ref[alt], 0))
    return point, np.percentile(d, 2.5), np.percentile(d, 97.5)

comps = [("W0", "W4_full", "PRIMARY X4a: ERA5 100 m transit on fixed W0 hours"),
         ("W0", "W4_speed", "speed only (W0 direction, ERA5 speed)"),
         ("W0", "W4_resel", "X4b: reselected hours with ERA5 100 m"),
         ("W0_dc", "W4_dc", "direction-consistent common sample"),
         ("W0", "T45", "AMS 5 45 m (supporting)"), ("W0", "T75", "AMS 5 75 m (supporting)"), ("W0", "T90", "AMS 5 90 m (supporting)")]
dl = pd.DataFrame([dict(comparison=lab, base=a, alternative=b, delta_SSE=x[0], ci_lo=x[1], ci_hi=x[2])
                   for a, b, lab in comps for x in [delta(a, b)]])
dl.round(4).to_csv(RES / "e09_delta_sse.csv", index=False)
prim = dl.iloc[0]
dec = pd.DataFrame([dict(criterion="Primary: Delta SSE (W0 minus ERA5 100 m, X4a) 95% CI above 0",
                         value=f"{prim.delta_SSE:.3f} ({prim.ci_lo:.3f} to {prim.ci_hi:.3f})", outcome=(
                         "supported" if prim.ci_lo > 0 else "not supported" if prim.ci_hi < 0 else "inconclusive"))])
dec.to_csv(RES / "e09_decision.csv", index=False)

# ---------------- representativeness of the AMS 5 tower direction
XY = stations(); rep_rows = []
uT, vT = TOWER[45]
for s in ST:
    u, v = W[s].u.to_numpy(), W[s].v.to_numpy(); ok = np.isfinite(u) & np.isfinite(uT) & (np.hypot(u, v) >= 1)
    ang = np.degrees(np.abs(np.angle(np.exp(1j * (np.arctan2(uT, vT) - np.arctan2(u, v))))))[ok]
    th = np.arctan2(u, v)[ok]; tt = np.arctan2(uT, vT)[ok]
    rc = np.mean(np.cos(th - tt))
    rep_rows.append(dict(station=s, km_from_AMS5=haversine_km(XY[s], XY["AMS 5"]), mean_cos_dir_diff=rc,
                         median_abs_dir_diff_deg=np.median(ang), share_gt_45deg=(ang > 45).mean()))
pd.DataFrame(rep_rows).round(3).to_csv(RES / "e09_tower_representativeness.csv", index=False)

# ---------------- figure
mids = np.array([(BINS[k] + BINS[k + 1]) / 2 for k in range(NBIN)])
fig, ax = plt.subplots(1, 3, figsize=(7.6, 2.8), sharey=True)
for a_, vs, title in [(ax[0], ["W0", "W4_full"], "a  Fixed W0 hours (X4a)"), (ax[1], ["W0", "W4_speed", "W4_resel"], "b  Speed vs selection"),
                      (ax[2], ["W0_dc", "W4_dc"], "c  Direction-consistent sample")]:
    for k, v in enumerate(vs):
        lo = np.percentile(boot[v], 2.5, 0); hi = np.percentile(boot[v], 97.5, 0)
        a_.errorbar(mids + 0.04 * k, obs[v], yerr=[obs[v] - lo, hi - obs[v]], fmt="o-", ms=3, capsize=2, c=f"C{k}", label=f"{v} observed")
        a_.fill_between(mids, ref[v].min(0), ref[v].max(0), color=f"C{k}", alpha=0.15)
    a_.plot([0, 3], [0, 3], ":", c="0.6", lw=0.8); a_.set_title(title, fontsize=7.5); a_.set_xlabel("Transit time bin midpoint (h)")
    a_.legend(fontsize=5.5, frameon=False)
ax[0].set_ylabel("Lag centroid (h)")
fig.text(0.01, -0.07, "Points: observed centroids (95% joint block bootstrap); bands: continuous-source reference range (A = 0.3, 10 replicates) "
         "under the same wind. Bins are defined by each variant's transit time. Development data 2021-2025.", fontsize=6)
save(fig, FIG / "e09_centroids_by_wind")
runmeta.write(EXP, dict(experiment="E09_elevated_wind (X4)", status="exploratory", seed_used=SEED, reps=REPS, n_boot=NB))
print(tab[["variant"] + [f"obs_bin{k}" for k in range(NBIN)] + [f"ref_bin{k}" for k in range(NBIN)] + ["SSE"]].round(3).to_string(index=False))
print(tab[["variant"] + [f"n_bin{k}" for k in range(NBIN)]].to_string(index=False)); print(dl.round(3).to_string(index=False)); print(dec.to_string(index=False))
print(pd.DataFrame(dirdis).groupby("wind")[["median_abs_dir_diff_deg", "share_gt_45deg", "share_gt_90deg"]].median().round(3).to_string())
print(pd.DataFrame(membership).groupby("variant")[["jaccard", "same_bin_share"]].median().round(3).to_string())
print(pd.DataFrame(rep_rows).round(2).sort_values("km_from_AMS5").to_string(index=False))
