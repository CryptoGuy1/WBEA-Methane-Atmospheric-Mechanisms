"""E05 - H2: direction-dependent lagged coupling between station pairs (specification D-26).
Development data; exploratory. D_ij is a process signature of direction-dependent coupling, not a
trajectory, a source rate or a transport fraction."""
import sys, pathlib, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(EXP.parents[1] / "src"))
from wbea.config import CFG
from wbea.io import load_dev
from wbea.wind import composite
from wbea.geometry import pair_table
from wbea import runmeta
from wbea.plotstyle import plt, save

RES = EXP / "results"; FIG = EXP / "figures"; RES.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
SEED = CFG["project"]["seed"] + 5; rng = np.random.default_rng(SEED); H2 = CFG["h2"]; LAGS = H2["lags"]
P = load_dev(); ST = CFG["stations"]["usable"]; idx = P["AMS 1"].index; N = len(idx)
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST})
X = CH - CH.loc["2021":"2023"].median()
W = {s: composite(P[s]) for s in ST}
FAM = pair_table(ST, H2["max_pair_km"]).reset_index(drop=True)
BLK = ((idx - idx[0]).days // CFG["bootstrap"]["block_days"]).to_numpy(); NBLK = BLK.max() + 1
S5 = P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"]
STAB = pd.Series(np.digitize(S5, S5.loc["2021":"2023"].quantile([1 / 3, 2 / 3]).values), index=idx).where(S5.notna()).to_numpy()
SEASON = pd.Series(idx.month).map({12: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2, 9: 3, 10: 3, 11: 3}).to_numpy()

def residuals(i, j, mode="lpo", ch_shift=None):
    Xs = X.copy()
    if ch_shift:
        st, h = ch_shift; Xs[st] = Xs[st].shift(h)
    if mode == "raw":
        return Xs[i].diff().to_numpy(), Xs[j].diff().to_numpy()
    if mode == "loo":
        mi = Xs.drop(columns=i).median(1); mj = Xs.drop(columns=j).median(1)
        return (Xs[i] - mi).diff().to_numpy(), (Xs[j] - mj).diff().to_numpy()
    others = [s for s in ST if s not in (i, j)] if mode == "lpo" else \
             [s for s in ST if s not in (i, j, "AMS 14", "AMS 18")]
    m = Xs[others].median(1).where(Xs[others].notna().sum(1) >= H2["kmin_other_stations"])
    return (Xs[i] - m).diff().to_numpy(), (Xs[j] - m).diff().to_numpy()

def pair_wind(i, j, bearing, shift_h=0):
    u = ((W[i].u + W[j].u) / 2).to_numpy(); v = ((W[i].v + W[j].v) / 2).to_numpy()
    if shift_h:
        u = np.roll(u, shift_h); v = np.roll(v, shift_h)
    phi = np.deg2rad(bearing); upar = u * np.sin(phi) + v * np.cos(phi); sp = np.hypot(u, v)
    with np.errstate(invalid="ignore", divide="ignore"):
        cosang = upar / sp; tau = None
    return upar, cosang

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

def block_sums(dri, drj, al, rv):
    """Sufficient statistics per block: [set(2), lag(3), order(2), stat(6)]: n, sa, sb, saa, sbb, sab."""
    out = np.zeros((NBLK, 2, len(LAGS), 2, 6))
    for si, m in enumerate((al, rv)):
        for li, l in enumerate(LAGS):
            a1 = np.r_[np.full(l, np.nan), dri[:-l]]; b1 = drj      # i leads
            a2 = np.r_[np.full(l, np.nan), drj[:-l]]; b2 = dri      # j leads
            ok = m & np.isfinite(a1) & np.isfinite(b1) & np.isfinite(a2) & np.isfinite(b2)
            bk = BLK[ok]
            for oi, (a, b) in enumerate(((a1[ok], b1[ok]), (a2[ok], b2[ok]))):
                for k, val in enumerate((np.ones_like(a), a, b, a * a, b * b, a * b)):
                    out[:, si, li, oi, k] = np.bincount(bk, val, minlength=NBLK)
    return out

def corr_from(s):
    n, sa, sb, saa, sbb, sab = np.moveaxis(s, -1, 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (n * sab - sa * sb) / np.sqrt((n * saa - sa ** 2) * (n * sbb - sb ** 2))

def D_from(tot, w):
    r = corr_from(tot)                      # [set, lag, order]
    rho = r[:, :, 0] - r[:, :, 1]           # i-leads minus j-leads
    return float(np.sum(w * (rho[0] - rho[1]))), rho

# ---------------- primary statistics per pair
prim, store = [], {}
for p, r in FAM.iterrows():
    dri, drj = residuals(r.i, r.j)
    upar, cosang = pair_wind(r.i, r.j, r.bearing); al, rv, tau = sets(r.km, upar, cosang)
    w = weights(tau, al, rv); bs = block_sums(dri, drj, al, rv); D, rho = D_from(bs.sum(0), w)
    store[p] = dict(dri=dri, drj=drj, w=w, bs=bs)
    prim.append(dict(pair=f"{r.i}->{r.j}", i=r.i, j=r.j, km=r.km, bearing=r.bearing, n_aligned=int(al.sum()), n_reversed=int(rv.sum()),
                     median_tau=float(np.nanmedian(tau[al | rv])), w1=w[0], w2=w[1], w3=w[2], D=D,
                     rho1_al=rho[0, 0], rho1_rv=rho[1, 0], rho2_al=rho[0, 1], rho2_rv=rho[1, 1]))
prim = pd.DataFrame(prim)

# ---------------- null: whole-day circular wind shifts (same shift for all pairs)
NS = H2["n_wind_shifts"]; ndays = N // 24
shifts = rng.integers(H2["min_shift_days"], ndays - H2["min_shift_days"], NS) * 24
null = np.empty((NS, len(FAM)))
for p, r in FAM.iterrows():
    dri, drj = store[p]["dri"], store[p]["drj"]
    for k, sh in enumerate(shifts):
        upar, cosang = pair_wind(r.i, r.j, r.bearing, sh); al, rv, tau = sets(r.km, upar, cosang)
        null[k, p] = D_from(block_sums(dri, drj, al, rv).sum(0), weights(tau, al, rv))[0]
mu, sd = null.mean(0), null.std(0); prec = 1 / sd ** 2
prim["null_mean"] = mu; prim["null_sd"] = sd; prim["null_p95"] = np.percentile(null, 95, 0)
prim["p_one_sided"] = (1 + (null >= prim.D.values).sum(0)) / (NS + 1)
Z = (prim.D.values - mu) / sd; Zn = (null - mu) / sd; maxZ = Zn.max(1)
prim["Z"] = Z; prim["p_maxT_familywise"] = [(1 + (maxZ >= z).sum()) / (NS + 1) for z in Z]
pooled = float(np.sum(prec * prim.D) / prec.sum()); pooled_null = null @ prec / prec.sum()
p_pooled = (1 + (pooled_null >= pooled).sum()) / (NS + 1)

# ---------------- joint block bootstrap CIs (same block draws for all pairs)
NB = CFG["bootstrap"]["n_boot"]; bsD = np.empty((NB, len(FAM)))
draws = [rng.integers(0, NBLK, NBLK) for _ in range(NB)]
for p in range(len(FAM)):
    bsum = store[p]["bs"]; w = store[p]["w"]
    for b, dr in enumerate(draws):
        bsD[b, p] = D_from(bsum[dr].sum(0), w)[0]
prim["ci_lo"] = np.nanpercentile(bsD, 2.5, 0); prim["ci_hi"] = np.nanpercentile(bsD, 97.5, 0)
bs_pooled = bsD @ prec / prec.sum()
prim.round(5).to_csv(RES / "h2_pair_statistics.csv", index=False)
pd.DataFrame(null, columns=prim.pair).round(5).to_csv(RES / "h2_null_distribution.csv.gz", index=False, compression="gzip")

# ---------------- sensitivities (pooled D with the primary precision weights)
def pooled_D(mode="lpo", wind_shift=0, ch_shift_station=None, extra=None):
    Ds = []
    for p, r in FAM.iterrows():
        cs = (r.i if ch_shift_station == "source" else r.j, 1) if ch_shift_station else None
        dri, drj = (store[p]["dri"], store[p]["drj"]) if (mode == "lpo" and not cs) else residuals(r.i, r.j, mode, cs)
        upar, cosang = pair_wind(r.i, r.j, r.bearing, wind_shift)
        al, rv, tau = sets(r.km, upar, cosang, extra)
        Ds.append(D_from(block_sums(dri, drj, al, rv).sum(0), weights(tau, al, rv))[0])
    Ds = np.array(Ds); ok = np.isfinite(Ds)
    return float(np.sum(prec[ok] * Ds[ok]) / prec[ok].sum()), Ds

sens = [dict(analysis="primary (leave-pair-out)", pooled_D=pooled)]
for h in (+1, -1):
    sens.append(dict(analysis=f"wind shifted {h:+d} h relative to CH4", pooled_D=pooled_D(wind_shift=h)[0]))
for which in ("source", "receptor"):
    sens.append(dict(analysis=f"{which} station CH4 delayed by 1 h (diagnostic)", pooled_D=pooled_D(ch_shift_station=which)[0]))
modes = {}
for mode, lab in [("raw", "no common-mode removal"), ("loo", "leave-one-out common mode"), ("lpo_core", "leave-pair-out, AMS 14/18 excluded")]:
    v, Ds = pooled_D(mode); sens.append(dict(analysis=lab, pooled_D=v)); modes[lab] = Ds
for k, name in enumerate(["DJF", "MAM", "JJA", "SON"]):
    sens.append(dict(analysis=f"season {name}", pooled_D=pooled_D(extra=SEASON == k)[0]))
for k, name in enumerate(["unstable", "neutral", "stable"]):
    sens.append(dict(analysis=f"stability {name}", pooled_D=pooled_D(extra=STAB == k)[0]))
sens = pd.DataFrame(sens); sens.round(5).to_csv(RES / "h2_sensitivity.csv", index=False)
res_modes = pd.DataFrame({"pair": prim.pair, "km": prim.km, "leave-pair-out (primary)": prim.D, **modes})
res_modes.round(5).to_csv(RES / "h2_residualisation_comparison.csv", index=False)

# ---------------- observed kernel-shape statistics (reference kernels come from E06)
bins = [0, 0.5, 1.0, 1.5, 2.0, 3.0]; acc = {k: [] for k in range(len(bins) - 1)}
for p, r in FAM.iterrows():
    dri, drj = store[p]["dri"], store[p]["drj"]; upar, cosang = pair_wind(r.i, r.j, r.bearing)
    al, rv, tau = sets(r.km, upar, cosang)
    for k in range(len(bins) - 1):
        m = al & (tau >= bins[k]) & (tau < bins[k + 1]); m[0] = False
        a0, b0, a1 = dri[m], drj[m], dri[np.where(m)[0] - 1]; ok = np.isfinite(a0) & np.isfinite(b0) & np.isfinite(a1)
        if ok.sum() > 50:
            acc[k].append(np.column_stack([(a0[ok] - a0[ok].mean()) / a0[ok].std(), (a1[ok] - a1[ok].mean()) / a1[ok].std(),
                                           (b0[ok] - b0[ok].mean()) / b0[ok].std()]))
shape = []
for k, lst in acc.items():
    A = np.vstack(lst); r0 = np.corrcoef(A[:, 0], A[:, 2])[0, 1]; r1 = np.corrcoef(A[:, 1], A[:, 2])[0, 1]
    shape.append(dict(tau_bin=f"{bins[k]}-{bins[k + 1]} h", n=len(A), r_lag0=r0, r_lag1=r1, ratio_lag1_to_lag0=r1 / r0))
shape = pd.DataFrame(shape); shape.round(4).to_csv(RES / "h2_observed_lag_profile_by_tau.csv", index=False)

# ---------------- gate (D-26; shape criterion deferred to E06)
g1 = pooled > np.percentile(pooled_null, 95); g2 = all(sens.loc[sens.analysis.str.startswith("wind shifted"), "pooled_D"] > 0)
dec = pd.DataFrame([dict(criterion="Pooled D above 95th percentile of wind-shift null (one-sided p < 0.05)", value=f"p = {p_pooled:.4f}", met=bool(g1)),
                    dict(criterion="Pooled D positive under +/-1 h wind-vs-CH4 shift", value="; ".join(f"{x:.4f}" for x in sens.pooled_D[1:3]), met=bool(g2)),
                    dict(criterion="Kernel-shape criterion", value="evaluated in E06", met=None),
                    dict(criterion="H2 development gate (criteria 1-2)", value="", met=bool(g1 and g2))])
dec.to_csv(RES / "h2_decision.csv", index=False)
pd.DataFrame([dict(pooled_D=pooled, ci_lo=np.percentile(bs_pooled, 2.5), ci_hi=np.percentile(bs_pooled, 97.5),
                   null_mean=pooled_null.mean(), null_p95=np.percentile(pooled_null, 95), p_one_sided=p_pooled,
                   n_pairs=len(FAM), pairs_p_unadj_lt_05=int((prim.p_one_sided < .05).sum()),
                   pairs_familywise_lt_05=int((prim.p_maxT_familywise < .05).sum()),
                   pairs_D_positive=int((prim.D > 0).sum()))]).round(5).to_csv(RES / "h2_pooled.csv", index=False)

# ---------------- Figure 6: per-pair D vs distance with null band and CIs
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.1), gridspec_kw={"width_ratios": [2.2, 1]})
o = prim.sort_values("km")
ax[0].fill_between(o.km, np.percentile(null, 2.5, 0)[o.index], np.percentile(null, 97.5, 0)[o.index], color="0.88", step="mid", label="wind-shift null 95% range")
sc = ax[0].scatter(o.km, o.D, c=o.median_tau, cmap="viridis", s=22, zorder=3)
ax[0].vlines(o.km, o.ci_lo, o.ci_hi, color="0.4", lw=0.7, zorder=2); ax[0].axhline(0, c="0.6", lw=0.6)
for _, r in o[o.p_maxT_familywise < 0.05].iterrows():
    ax[0].annotate("*", (r.km, r.ci_hi), ha="center", fontsize=8)
fig.colorbar(sc, ax=ax[0], fraction=0.04).set_label("median predicted transit (h)")
ax[0].set_xlabel("Station separation (km)"); ax[0].set_ylabel("Directional contrast D (lags 1-3)")
ax[0].set_title("a  27 pairs; * family-wise p < 0.05 (max-T)"); ax[0].legend(fontsize=6, frameon=False, loc="upper right")
ax[1].hist(pooled_null, bins=40, color="0.7"); ax[1].axvline(pooled, c="C3", lw=1.5)
ax[1].set_xlabel("Pooled D"); ax[1].set_ylabel("Wind-shift replicates"); ax[1].set_title(f"b  Pooled D = {pooled:.3f}, p = {p_pooled:.3f}")
fig.text(0.01, -0.06, "Leave-pair-out residual CH$_4$ changes; aligned minus reversed flow; 1,000 whole-day wind shifts; "
         "bars: 14-day joint block bootstrap 95% CI. Development data 2021-2025.", fontsize=6.3)
save(fig, FIG / "figure06_directional_coupling")

# ---------------- Figure 8: residualisation comparison
fig, ax = plt.subplots(figsize=(6.6, 3.0)); xs = np.arange(len(o))
for k, (lab, col) in enumerate([("no common-mode removal", "0.6"), ("leave-one-out common mode", "C1"),
                                ("leave-pair-out (primary)", "k"), ("leave-pair-out, AMS 14/18 excluded", "C0")]):
    ax.plot(xs + (k - 1.5) * 0.18, res_modes.loc[o.index, lab], "o", ms=3, c=col, label=lab)
ax.axhline(0, c="0.6", lw=0.6); ax.set_xticks(xs, [p.replace("AMS ", "").replace("->", "-") for p in o.pair], rotation=90, fontsize=6)
ax.set_ylabel("Directional contrast D"); ax.set_xlabel("Pair (ordered by separation)"); ax.legend(fontsize=6, frameon=False, ncol=2)
ax.set_title("How much directional signal survives removal of the regional component")
save(fig, FIG / "figure08_residualisation_sensitivity")

runmeta.write(EXP, dict(experiment="E05_directional_coupling", status="exploratory", seed_used=SEED, n_shifts=NS, n_boot=NB))
print(prim[["pair", "km", "n_aligned", "n_reversed", "D", "ci_lo", "ci_hi", "p_one_sided", "p_maxT_familywise"]].round(4).to_string(index=False))
print(pd.read_csv(RES / "h2_pooled.csv").to_string(index=False)); print(sens.round(4).to_string(index=False))
print(shape.round(3).to_string(index=False)); print(dec.to_string(index=False))
