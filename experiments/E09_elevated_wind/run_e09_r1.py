"""E09-r1 (D-59): precision refinement of the X4 elevated-wind comparison. Exploratory, development data.
Changes vs E09: common random source signals across variants (per pair x replicate); paired reference replicates
in Delta SSE; 50 replicates; Monte Carlo vs temporal uncertainty separated; fixed-bin diagnostic W4_fixbin.
Hypothesis and decision threshold unchanged. Original E09 outputs are not modified."""
import sys, pathlib, numpy as np, pandas as pd
from scipy.signal import lfilter
EXP = pathlib.Path(__file__).resolve().parent
src = (EXP / "run_e09.py").read_text().split("# ---------------- observed")[0]
g = {"__file__": str(EXP / "run_e09.py"), "__name__": "e09_setup"}; exec(compile(src, "run_e09_setup", "exec"), g)
from wbea import h2, runmeta
from wbea.plotstyle import plt, save
N, NBIN, BINS, BLK, NBLK, FAM, X, ST = (g[k] for k in ["N", "NBIN", "BINS", "BLK", "NBLK", "FAM", "X", "ST"])
winds, along, aligned, block_sums, centroids = g["winds"], g["along"], g["aligned"], g["block_sums"], g["centroids"]
SEED = g["SEED"] + 100; rng = np.random.default_rng(SEED); REPS, NB, SHIFT, MEM, A_REF = 50, 1000, g["SHIFT"], g["MEM"], g["A_REF"]
RES = EXP / "results"; FIG = EXP / "figures"
VAR = {  # name: (selection wind, transport wind, bin wind, subset)
    "W0": ("W0", "W0", "W0", None), "W4_speed": ("W0", "W4speed", "W4speed", None), "W4_full": ("W0", "W4", "W4", None),
    "W0_dc": ("W0", "W0", "W0", "dc"), "W4_dc": ("W0", "W4", "W4", "dc"), "W4_fixbin": ("W0", "W4", "W0", None)}

def spec(a, b, km, phi, shift=0):
    wd = winds(a, b)
    if shift:
        wd = {k: (np.roll(v[0], shift), np.roll(v[1], shift)) for k, v in wd.items()}
    al, rv, tr, tau = {}, {}, {}, {}
    for k, uv in wd.items():
        up, cs = along(uv, phi); al[k], rv[k] = aligned(km, up, cs); tr[k] = (up, cs)
        with np.errstate(invalid="ignore", divide="ignore"):
            tau[k] = km / (3.6 * np.abs(up))
    out = {}
    for name, (sel, trn, bw, sub) in VAR.items():
        m = al[sel].copy()
        if sub == "dc": m &= al["W4"]
        bn = np.full(N, -1)
        for k_ in range(NBIN): bn[(tau[bw] >= BINS[k_]) & (tau[bw] < BINS[k_ + 1])] = k_
        out[name] = dict(bin=np.where(m, bn, -1), up=tr[trn][0], cs=tr[trn][1])
    return out

def inject(q, Ri, Rj, up, cs, km, sd):
    k = np.arange(N * 60); hr = k // 60; u_ = up[hr]; c_ = np.abs(np.nan_to_num(cs[hr])); ok = np.isfinite(u_)
    tau = np.minimum(km / (3.6 * np.maximum(np.abs(np.nan_to_num(u_)), 0.5)), 6.0)
    qd = 0.8 * c_ * q[np.clip(k - np.round(60 * tau).astype(int), 0, None)] * ok
    i_up = np.nan_to_num(u_) >= 0
    si = np.where(i_up, q, qd).reshape(N, 60).mean(1); sj = np.where(i_up, qd, q).reshape(N, 60).mean(1)
    sc = A_REF * sd / np.nanstd(np.diff(si))
    return np.diff(np.r_[np.nan, Ri + sc * si]), np.diff(np.r_[np.nan, Rj + sc * sj])

pairs = []
for _, r in FAM.iterrows():
    Ri, Rj = h2.lpo_residual_levels(X, r.i, r.j, ST); dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
    phi = np.deg2rad(r.bearing)
    pairs.append(dict(i=r.i, j=r.j, km=r.km, phi=phi, Ri=Ri, Rj=Rj, dri=dri, drj=drj, sd=np.nanstd(dri),
                      obs=spec(r.i, r.j, r.km, phi), sh=spec(r.i, r.j, r.km, phi, SHIFT)))
obsS = {v: [block_sums(p["dri"], p["drj"], p["obs"][v]["bin"]) for p in pairs] for v in VAR}
obs = {v: centroids(obsS[v])[0] for v in VAR}
nbin = {v: sum(S[:, :, 0, 0].sum(0) for S in obsS[v]) for v in VAR}

ref = {v: np.empty((REPS, NBIN)) for v in VAR}
for rep in range(REPS):
    reps = {v: [] for v in VAR}
    for p in pairs:
        q = lfilter([1.0], [1.0, -np.exp(-1.0 / MEM)], rng.standard_normal(N * 60 + 600))[600:]   # common random numbers
        for v in VAR:
            a, b = inject(q, p["Ri"], p["Rj"], p["sh"][v]["up"], p["sh"][v]["cs"], p["km"], p["sd"])
            reps[v].append(block_sums(a, b, p["sh"][v]["bin"]))
    for v in VAR:
        ref[v][rep] = centroids(reps[v])[0]

boot = {v: np.empty((NB, NBIN)) for v in VAR}
for b in range(NB):
    w = np.bincount(rng.integers(0, NBLK, NBLK), minlength=NBLK).astype(float)
    for v in VAR: boot[v][b] = centroids(obsS[v], w)[0]
sse = lambda c, r: np.nansum((c - r) ** 2)
rows = []
for base, alt, lab in [("W0", "W4_full", "PRIMARY X4a: ERA5 100 m transit, fixed W0 hours"), ("W0", "W4_speed", "speed only"),
                       ("W0_dc", "W4_dc", "direction-consistent common sample"),
                       ("W0", "W4_fixbin", "fixed-bin diagnostic: identical observed bins, ERA5 transport in reference")]:
    point = sse(obs[base], ref[base].mean(0)) - sse(obs[alt], ref[alt].mean(0))
    mc = np.array([sse(obs[base], ref[base][r]) - sse(obs[alt], ref[alt][r]) for r in range(REPS)])          # paired replicates
    tmp = np.array([sse(boot[base][b], ref[base].mean(0)) - sse(boot[alt][b], ref[alt].mean(0)) for b in range(NB)])
    ridx = rng.integers(0, REPS, NB)
    comb = np.array([sse(boot[base][b], ref[base][ridx[b]]) - sse(boot[alt][b], ref[alt][ridx[b]]) for b in range(NB)])
    rows.append(dict(comparison=lab, delta_SSE=point, mc_sd=mc.std(), mc_ci_lo=np.percentile(mc, 2.5), mc_ci_hi=np.percentile(mc, 97.5),
                     temporal_sd=tmp.std(), temporal_ci_lo=np.percentile(tmp, 2.5), temporal_ci_hi=np.percentile(tmp, 97.5),
                     combined_ci_lo=np.percentile(comb, 2.5), combined_ci_hi=np.percentile(comb, 97.5)))
dl = pd.DataFrame(rows); dl.round(4).to_csv(RES / "r1_delta_sse.csv", index=False)
orig = pd.read_csv(RES / "e09_delta_sse.csv")
cmp_ = pd.DataFrame([dict(version="E09 (10 replicates, unpaired)", delta_SSE=orig.delta_SSE[0], ci_lo=orig.ci_lo[0], ci_hi=orig.ci_hi[0]),
                     dict(version="E09-r1 (50 paired replicates, common random numbers)", delta_SSE=dl.delta_SSE[0],
                          ci_lo=dl.combined_ci_lo[0], ci_hi=dl.combined_ci_hi[0])])
cmp_.round(4).to_csv(RES / "r1_vs_original_primary.csv", index=False)
tab = pd.DataFrame([dict(variant=v, **{f"obs_bin{k}": obs[v][k] for k in range(NBIN)}, **{f"ref_bin{k}": ref[v].mean(0)[k] for k in range(NBIN)},
                         **{f"ref_mcsd_bin{k}": ref[v].std(0)[k] for k in range(NBIN)}, **{f"n_bin{k}": int(nbin[v][k]) for k in range(NBIN)},
                         SSE=sse(obs[v], ref[v].mean(0))) for v in VAR])
tab.round(4).to_csv(RES / "r1_centroids_reference_sse.csv", index=False)
p = dl.iloc[0]; outcome = "supported" if p.combined_ci_lo > 0 else ("changed direction (alternative worse)" if p.combined_ci_hi < 0 else "inconclusive")
pd.DataFrame([dict(criterion="Primary Delta SSE combined 95% CI above 0 (unchanged threshold)",
                   value=f"{p.delta_SSE:.3f} ({p.combined_ci_lo:.3f} to {p.combined_ci_hi:.3f})", outcome=outcome)]).to_csv(RES / "r1_decision.csv", index=False)
mids = np.array([(BINS[k] + BINS[k + 1]) / 2 for k in range(NBIN)])
fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
for a_, vs, t in [(ax[0], ["W0", "W4_full"], "a  Fixed W0 hours (X4a), 50 paired replicates"), (ax[1], ["W0", "W4_fixbin"], "b  Fixed bins: only the reference changes")]:
    for k, v in enumerate(vs):
        lo, hi = np.percentile(boot[v], 2.5, 0), np.percentile(boot[v], 97.5, 0)
        a_.errorbar(mids + 0.04 * k, obs[v], yerr=[obs[v] - lo, hi - obs[v]], fmt="o-", ms=3, capsize=2, c=f"C{k}", label=f"{v} observed")
        a_.fill_between(mids, np.percentile(ref[v], 2.5, 0), np.percentile(ref[v], 97.5, 0), color=f"C{k}", alpha=0.2, label=f"{v} reference 95%")
    a_.plot([0, 3], [0, 3], ":", c="0.6", lw=0.8); a_.set_xlabel("Transit time bin midpoint (h)"); a_.set_title(t, fontsize=7.5); a_.legend(fontsize=5.5, frameon=False)
ax[0].set_ylabel("Lag centroid (h)")
save(fig, FIG / "e09_r1_centroids")
runmeta.write(RES, dict(experiment="E09-r1 (D-59)", seed_used=SEED, reps=REPS, n_boot=NB)); (RES / "run_metadata.json").rename(RES / "r1_run_metadata.json")
print(dl.round(4).to_string(index=False)); print(cmp_.round(4).to_string(index=False)); print("outcome:", outcome)
print(tab[["variant", "SSE"] + [f"obs_bin{k}" for k in range(NBIN)] + [f"ref_bin{k}" for k in range(NBIN)]].round(3).to_string(index=False))
