"""E10 (X1) - Methane-pattern and wind-alignment typology of P95 episodes (D-56, D-60). Development data;
exploratory. Labels say 'compatible with' accumulation or advection; they are not source identities and do not
prove mechanisms. Wind enters the upstream-lead definition, so wind-shift placebo checks are separate from the
external physical-consistency checks (ERA5 BLH, AMS 5 stability, ERA5 100 m direction variability)."""
import sys, pathlib, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent; ROOT = EXP.parents[1]
sys.path.insert(0, str(ROOT / "src"))
from wbea.config import CFG
from wbea.io import load_dev, load_era5
from wbea.wind import composite
from wbea.geometry import pair_table
from wbea import h2, runmeta
from wbea.plotstyle import plt, save

RES = EXP / "results"; FIG = EXP / "figures"; RES.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
SEED = CFG["project"]["seed"] + 10; rng = np.random.default_rng(SEED); NB = 1000; NPLAC = 200
P = load_dev(); ST = CFG["stations"]["usable"]; idx = P["AMS 1"].index; N = len(idx)
CORE = [s for s in ST if s not in ("AMS 14", "AMS 18")]
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); REF = CH.loc["2021":"2023"]; X = CH - REF.median()
W = {s: composite(P[s]) for s in ST}; ERA = load_era5(); FAM = pair_table(ST, 30.0).reset_index(drop=True)
LABELS = ["accumulation-compatible", "mixed", "advection-compatible", "isolated", "unclassified"]
BLK = ((idx - idx[0]).days // 14).to_numpy()

def episodes(q):
    thr = REF.quantile(q / 100); rows = []
    for s in ST:
        c = CH[s]; gap1 = c.isna() & c.shift(1).notna() & c.shift(-1).notna(); cb = c.where(~gap1, (c.shift(1) + c.shift(-1)) / 2)
        above = (cb > thr[s]); below = cb.notna() & ~above; onset = above & below.shift(1, fill_value=False)
        grp = (~above).cumsum(); run = above.groupby(grp).transform("sum"); peak = cb.where(above).groupby(grp).transform("max")
        for t in np.where(onset.to_numpy())[0]:
            rows.append(dict(station=s, t=t, time=idx[t], duration_h=int(run.iloc[t]), peak_excess=float(peak.iloc[t] - thr[s])))
    return pd.DataFrame(rows), thr

def synchrony(ep, thr, window="retro", omit=None):
    A = pd.DataFrame({k: CH[k].gt(thr[k]).astype(float).where(CH[k].notna()) for k in CORE})
    W_ = (pd.concat([A.shift(1), A, A.shift(-1)]).groupby(level=0).max() if window == "retro"
          else pd.concat([A.shift(1), A]).groupby(level=0).max())
    Wn = W_.reindex(idx)[CORE].to_numpy(); Vn = CH[CORE].notna().to_numpy(); ci = {k: n for n, k in enumerate(CORE)}
    sig, nval = [], []
    for s_, t_ in zip(ep.station.values, ep.t.values):
        cols = [ci[k] for k in CORE if k != s_ and k != omit]
        cols = [c for c in cols if Vn[t_, c]]
        nval.append(len(cols)); sig.append(np.nanmean(Wn[t_, cols]) if cols else np.nan)
    return np.array(sig), np.array(nval)

# pair-level quantities for the upstream lead
PAIRS = []
for _, r in FAM.iterrows():
    Ra, Rb = h2.lpo_residual_levels(X, r.i, r.j, ST)
    za = np.diff(np.r_[np.nan, Ra]); zb = np.diff(np.r_[np.nan, Rb]); za /= np.nanstd(za); zb /= np.nanstd(zb)
    PAIRS.append(dict(a=r.i, b=r.j, km=r.km, bearing=r.bearing, za=za, zb=zb))

def lead_arrays(shift=0, lags=3, zthr=1.0):
    """For each station: L(t) and lead_assessable(t) over all pairs where the station is the receptor."""
    L = {s: np.zeros(N, bool) for s in ST}; AS = {s: np.zeros(N, bool) for s in ST}
    for p in PAIRS:
        up, cs = h2.pair_wind(W[p["a"]], W[p["b"]], p["bearing"], shift); al, rv, _ = h2.sets(p["km"], up, cs)
        for recv, src_z, flow in ((p["b"], p["za"], al), (p["a"], p["zb"], rv)):      # al: flow a->b; rv: flow b->a
            zl = np.nanmax(np.vstack([np.r_[np.full(l, np.nan), src_z[:-l]] for l in range(1, lags + 1)]), 0)
            L[recv] |= flow & (zl >= zthr); AS[recv] |= flow
    return L, AS

def label(sig, nval, Lv, cut=0.5):
    lab = np.where(sig >= cut, np.where(Lv, "mixed", "accumulation-compatible"), np.where(Lv, "advection-compatible", "isolated"))
    return np.where((nval < 4) | ~np.isfinite(sig), "unclassified", lab)

def kappa(a, b):
    cats = LABELS; m = pd.crosstab(pd.Categorical(a, cats), pd.Categorical(b, cats), dropna=False).values.astype(float)
    n = m.sum(); po = np.trace(m) / n; pe = (m.sum(0) * m.sum(1)).sum() / n ** 2
    return (po - pe) / (1 - pe)

# ---------------- primary classification
ep, thr95 = episodes(95)
sig, nval = synchrony(ep, thr95)
Lr, ASr = lead_arrays()
ep["sigma"] = sig; ep["n_valid_core"] = nval
ep["lead"] = [Lr[s][t] for s, t in zip(ep.station, ep.t)]; ep["lead_assessable"] = [ASr[s][t] for s, t in zip(ep.station, ep.t)]
ep["label"] = label(sig, nval, ep.lead.values)
ep["block"] = BLK[ep.t.values]; ep["period"] = np.where(ep.time.dt.year <= 2023, "2021-2023", "2024-2025")

# external variables at onset
S5 = P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"]; Sz = (S5 - S5.loc["2021":"2023"].mean()) / S5.loc["2021":"2023"].std()
upper = S5.loc["2021":"2023"].quantile(2 / 3)
def dir_sd(s):
    e = ERA[s].reindex(idx); th = np.arctan2(e.u100, e.v100); z = np.exp(1j * th)
    R = np.abs(pd.Series(z).rolling(3, min_periods=3).mean().to_numpy())
    return np.degrees(np.sqrt(-2 * np.log(np.clip(R, 1e-9, 1))))
DSD = {s: dir_sd(s) for s in ST}
ep["blh"] = [ERA[s].blh.reindex(idx).iloc[t] for s, t in zip(ep.station, ep.t)]
ep["S_z"] = Sz.to_numpy()[ep.t.values]
ep["era5_dir_sd3h"] = [DSD[s][t] for s, t in zip(ep.station, ep.t)]
ws = {s: W[s].ws.to_numpy() for s in ST}
def f5(s, t):
    S_, w_ = S5.iloc[t], ws[s][t]
    if not (np.isfinite(S_) and np.isfinite(w_)): return "unclassified"
    return "stable-low-wind" if (S_ >= upper and w_ < 1.0) else ("advective" if (w_ >= 2.5 and S_ < upper) else "intermediate")
ep["f5_regime"] = [f5(s, t) for s, t in zip(ep.station, ep.t)]
ep.drop(columns=["t"]).round(4).to_csv(RES / "e10_episodes.csv", index=False)

# ---------------- shares with block-bootstrap CIs (pooled and per station)
ub = np.unique(ep.block); bi = {b: np.where(ep.block.values == b)[0] for b in ub}
def shares(df): return df.label.value_counts(normalize=True).reindex(LABELS, fill_value=0)
boot = np.array([shares(ep.iloc[np.concatenate([bi[b] for b in rng.choice(ub, len(ub))])]).values for _ in range(NB)])
pooled = pd.DataFrame({"label": LABELS, "share": shares(ep).values, "ci_lo": np.percentile(boot, 2.5, 0), "ci_hi": np.percentile(boot, 97.5, 0),
                       "n": ep.label.value_counts().reindex(LABELS, fill_value=0).values})
pooled.round(4).to_csv(RES / "e10_shares_pooled.csv", index=False)
st_sh = ep.groupby("station").label.value_counts(normalize=True).unstack(fill_value=0).reindex(columns=LABELS, fill_value=0)
st_sh["n_episodes"] = ep.groupby("station").size(); st_sh["lead_assessable_share"] = ep.groupby("station").lead_assessable.mean()
st_sh.round(4).to_csv(RES / "e10_shares_by_station.csv")

# ---------------- V1 wind-shift placebo (advection-compatible share)
ndays = N // 24; shifts = rng.choice(np.arange(14, ndays - 14), NPLAC, replace=False) * 24; plac = []
for sh in shifts:
    Ls, _ = lead_arrays(int(sh)); lv = np.array([Ls[s][t] for s, t in zip(ep.station, ep.t)])
    plac.append((label(sig, nval, lv) == "advection-compatible").mean())
plac = np.array(plac); real_adv = (ep.label == "advection-compatible").mean()
v1 = dict(check="V1 wind-shift placebo (not independent of wind)", real_share=real_adv, placebo_mean=plac.mean(),
          placebo_p95=np.percentile(plac, 95), p=(1 + (plac >= real_adv).sum()) / (NPLAC + 1), met=bool(real_adv > np.percentile(plac, 95)))

# ---------------- V2 external physical-consistency contrasts (accumulation- minus advection-compatible)
def contrast(df, col):
    a = df[df.label == "accumulation-compatible"][col].dropna(); b = df[df.label == "advection-compatible"][col].dropna()
    return a.median() - b.median()
v2 = []
for col, expect in [("blh", "negative"), ("S_z", "positive"), ("era5_dir_sd3h", "positive")]:
    est = contrast(ep, col); bs = np.array([contrast(ep.iloc[np.concatenate([bi[b] for b in rng.choice(ub, len(ub))])], col) for _ in range(NB)])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    v2.append(dict(variable=col, contrast_acc_minus_adv=est, ci_lo=lo, ci_hi=hi, expected_sign=expect,
                   met=bool(hi < 0) if expect == "negative" else bool(lo > 0)))
v2 = pd.DataFrame(v2); v2.round(4).to_csv(RES / "e10_v2_external_consistency.csv", index=False)

# ---------------- V3 temporal hold-out incremental information
def design(df, with_typ):
    cols = [pd.get_dummies(df.station, prefix="st"), pd.get_dummies(df.f5_regime, prefix="f5")]
    if with_typ: cols.append(pd.get_dummies(df.label, prefix="typ"))
    return pd.concat(cols, axis=1).astype(float)
tr = ep[ep.period == "2021-2023"]; te = ep[ep.period == "2024-2025"]; v3 = []
for yname, yf in [("log duration", lambda d: np.log(d.duration_h)), ("log peak excess", lambda d: np.log(d.peak_excess + 0.01))]:
    preds = {}
    for wt in (False, True):
        Xtr = design(tr, wt); Xte = design(te, wt).reindex(columns=Xtr.columns, fill_value=0)
        beta = np.linalg.lstsq(Xtr.values, yf(tr).values, rcond=None)[0]; preds[wt] = Xte.values @ beta
    y = yf(te).values; tb = te.block.values; tub = np.unique(tb); tbi = {b: np.where(tb == b)[0] for b in tub}
    def gain(ii):
        yy = y[ii]; sst = ((yy - yy.mean()) ** 2).sum()
        return (1 - ((yy - preds[True][ii]) ** 2).sum() / sst) - (1 - ((yy - preds[False][ii]) ** 2).sum() / sst)
    g0 = gain(np.arange(len(y))); gb = np.array([gain(np.concatenate([tbi[b] for b in rng.choice(tub, len(tub))])) for _ in range(NB)])
    v3.append(dict(outcome=yname, n_train=len(tr), n_test=len(te), r2_gain_test=g0, ci_lo=np.percentile(gb, 2.5), ci_hi=np.percentile(gb, 97.5),
                   met=bool(np.percentile(gb, 2.5) > 0)))
v3 = pd.DataFrame(v3); v3.round(4).to_csv(RES / "e10_v3_temporal_holdout.csv", index=False)

# ---------------- V4 temporal stability
v4 = pd.concat([ep.groupby("period").label.value_counts(normalize=True).unstack(fill_value=0).reindex(columns=LABELS, fill_value=0),
                pd.Series({p_: contrast(ep[ep.period == p_], "blh") for p_ in ("2021-2023", "2024-2025")}, name="blh_contrast")], axis=1)
v4.round(4).to_csv(RES / "e10_v4_period_stability.csv")

# ---------------- classification stability (kappa vs primary)
stab = []
for name, cut in [("sigma cut 0.4", 0.4), ("sigma cut 0.6", 0.6)]:
    stab.append(dict(variant=name, kappa=kappa(ep.label, label(sig, nval, ep.lead.values, cut))))
for name, lags, z in [("lead lags 1-2", 2, 1.0), ("lead z >= 0.75", 3, 0.75), ("lead z >= 1.25", 3, 1.25)]:
    Lx, _ = lead_arrays(0, lags, z); lv = np.array([Lx[s][t] for s, t in zip(ep.station, ep.t)])
    stab.append(dict(variant=name, kappa=kappa(ep.label, label(sig, nval, lv))))
s_on, n_on = synchrony(ep, thr95, "onset")
stab.append(dict(variant="onset-available synchrony (t0-1..t0) vs retrospective", kappa=kappa(ep.label, label(s_on, n_on, ep.lead.values))))
loo = [kappa(ep.label, label(*synchrony(ep, thr95, omit=m), ep.lead.values)) for m in CORE]
stab.append(dict(variant=f"leave-one-core-station-out synchrony (min over {len(CORE)})", kappa=min(loo)))
ep90, thr90 = episodes(90); ep90 = ep90.copy()
s90, n90 = synchrony(ep90, thr90); L90 = np.array([Lr[s][t] for s, t in zip(ep90.station, ep90.t)]); ep90["label"] = label(s90, n90, L90)
key95 = {(s, t + d): lab for s, t, lab in zip(ep.station, ep.t, ep.label) for d in (-1, 0, 1)}
m90 = [(lab, key95[(s, t)]) for s, t, lab in zip(ep90.station, ep90.t, ep90.label) if (s, t) in key95]
stab.append(dict(variant=f"P90 matched episodes ({len(m90)} of {len(ep90)} P90 onsets matched to {len(ep)} P95 onsets)",
                 kappa=kappa([a for a, _ in m90], [b for _, b in m90])))
stab = pd.DataFrame(stab); stab.round(4).to_csv(RES / "e10_classification_stability.csv", index=False)
pd.DataFrame({"label": LABELS, "P95_share": shares(ep).values, "P90_share": shares(ep90).values}).round(4).to_csv(RES / "e10_p90_population.csv", index=False)

# ---------------- decision
blh_ok = bool(v2.set_index("variable").loc["blh", "met"]); v3_ok = bool(v3.met.any())
dec = pd.DataFrame([dict(criterion=v1["check"], value=f"real {real_adv:.3f} vs placebo 95th {v1['placebo_p95']:.3f} (p = {v1['p']:.3f})", met=v1["met"]),
                    dict(criterion="V2 ERA5 BLH lower in accumulation- than advection-compatible (external consistency)",
                         value=f"{v2.contrast_acc_minus_adv[0]:.0f} m ({v2.ci_lo[0]:.0f} to {v2.ci_hi[0]:.0f})", met=blh_ok),
                    dict(criterion="V3 out-of-sample R2 gain > 0 for at least one outcome (2024-2025 hold-out)",
                         value="; ".join(f"{r.outcome}: {r.r2_gain_test:.4f} ({r.ci_lo:.4f} to {r.ci_hi:.4f})" for r in v3.itertuples()), met=v3_ok),
                    dict(criterion="Typology supported (V1 and V2-BLH and V3)", value="", met=bool(v1["met"] and blh_ok and v3_ok))])
dec.to_csv(RES / "e10_decision.csv", index=False); pd.DataFrame([v1]).round(4).to_csv(RES / "e10_v1_placebo.csv", index=False)

# ---------------- figure
fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.7, 1]})
cols_ = {"accumulation-compatible": "C0", "mixed": "C4", "advection-compatible": "C1", "isolated": "0.6", "unclassified": "0.85"}
bottom = np.zeros(len(st_sh))
for lab in LABELS:
    ax[0].bar(range(len(st_sh)), st_sh[lab], bottom=bottom, color=cols_[lab], label=lab); bottom += st_sh[lab].values
ax[0].set_xticks(range(len(st_sh)), [s.replace("AMS ", "") for s in st_sh.index], fontsize=7); ax[0].set_ylabel("Share of P95 episodes")
ax[0].set_xlabel("Station"); ax[0].legend(fontsize=5.5, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.18))
ax[0].set_title("a  Methane-pattern and wind-alignment typology", fontsize=7.5)
data = [ep[ep.label == l].blh.dropna() for l in LABELS[:4]]
ax[1].boxplot(data, showfliers=False); ax[1].set_xticks(range(1, 5), ["accum.", "mixed", "advec.", "isolated"], fontsize=6.5)
ax[1].set_ylabel("ERA5 BLH at onset (m)"); ax[1].set_title("b  External consistency check", fontsize=7.5)
save(fig, FIG / "e10_typology")
runmeta.write(EXP, dict(experiment="E10_episode_typology (X1)", status="exploratory", seed_used=SEED, n_boot=NB, n_placebo=NPLAC))
print(pooled.round(3).to_string(index=False)); print(pd.DataFrame([v1]).round(3).to_string(index=False)); print(v2.round(3).to_string(index=False))
print(v3.round(4).to_string(index=False)); print(v4.round(3).to_string()); print(stab.round(3).to_string(index=False)); print(dec.to_string(index=False))
print(st_sh.round(2).to_string())
