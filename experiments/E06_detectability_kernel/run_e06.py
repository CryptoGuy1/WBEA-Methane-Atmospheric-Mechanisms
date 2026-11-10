"""E06 - Synthetic signal injection, detectability of directional coupling, and the H2 kernel-shape
criterion (specification D-35). Development data; exploratory. Injected signals are idealised advected
fluctuations, not emission sources."""
import sys, pathlib, numpy as np, pandas as pd
from scipy.signal import lfilter
from scipy.stats import spearmanr
EXP = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(EXP.parents[1] / "src"))
from wbea.config import CFG
from wbea.io import load_dev
from wbea.wind import composite
from wbea.geometry import pair_table
from wbea import h2, runmeta
from wbea.plotstyle import plt, save

RES = EXP / "results"; FIG = EXP / "figures"; RES.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
SEED = CFG["project"]["seed"] + 6; rng = np.random.default_rng(SEED)
P = load_dev(); ST = CFG["stations"]["usable"]; idx = P["AMS 1"].index; N = len(idx)
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); X = CH - CH.loc["2021":"2023"].median()
W = {s: composite(P[s]) for s in ST}; FAM = pair_table(ST, h2.H2["max_pair_km"]).reset_index(drop=True)
E05 = pd.read_csv(EXP.parents[0] / "E05_directional_coupling" / "results" / "h2_pair_statistics.csv")
THR = dict(zip(E05.pair, E05.null_p95))
SHIFT = 182 * 24; AMPS = [0.0, 0.1, 0.2, 0.4]; MEMS = [20, 180]; REPS = 8; ATTEN = 0.8
BINS = [0, 0.5, 1.0, 1.5, 2.0, 3.0]

def inject(Ri, Rj, al, rv, tau, A, mem, sd_ref):
    e = al | rv
    q = lfilter([1.0], [1.0, -np.exp(-1.0 / mem)], rng.standard_normal(N * 60 + 600))[600:]
    k = np.arange(N * 60); hr = k // 60
    dmin = np.where(e[hr], np.round(60 * np.nan_to_num(tau[hr])), 0).astype(int)
    qd = ATTEN * q[np.clip(k - dmin, 0, None)]
    em, am = e[hr], al[hr]
    si = np.where(em, np.where(am, q, qd), 0.0).reshape(N, 60).mean(1)
    sj = np.where(em, np.where(am, qd, q), 0.0).reshape(N, 60).mean(1)
    sc = A * sd_ref / np.nanstd(np.diff(si)) if A > 0 else 0.0
    return np.diff(np.r_[np.nan, Ri + sc * si]), np.diff(np.r_[np.nan, Rj + sc * sj])

def pooled_profile(items):
    """items: list of (dr_up, dr_down, mask); returns pooled corr at lags 0..3 (standardised within item)."""
    r = []
    for l in range(4):
        A_, B_ = [], []
        for up, dn, m in items:
            a = np.r_[np.full(l, np.nan), up[:-l]] if l else up
            ok = m & np.isfinite(a) & np.isfinite(dn)
            if ok.sum() > 50:
                A_.append((a[ok] - a[ok].mean()) / a[ok].std()); B_.append((dn[ok] - dn[ok].mean()) / dn[ok].std())
        r.append(np.corrcoef(np.concatenate(A_), np.concatenate(B_))[0, 1])
    return np.array(r)

# ---------------- per-pair setup with shifted (decorrelated) wind
setup = []
for _, r in FAM.iterrows():
    Ri, Rj = h2.lpo_residual_levels(X, r.i, r.j, ST)
    upar, cosang = h2.pair_wind(W[r.i], W[r.j], r.bearing, SHIFT); al, rv, tau = h2.sets(r.km, upar, cosang)
    setup.append(dict(pair=f"{r.i}->{r.j}", km=r.km, Ri=Ri, Rj=Rj, al=al, rv=rv, tau=tau, w=h2.weights(tau, al, rv),
                      sd=np.nanstd(np.diff(Ri)), med_tau=float(np.nanmedian(tau[al | rv]))))

# ---------------- detectability
rows = []
for s in setup:
    for mem in MEMS:
        for A in AMPS:
            for rep in range(REPS):
                dri, drj = inject(s["Ri"], s["Rj"], s["al"], s["rv"], s["tau"], A, mem, s["sd"])
                D = h2.D_stat(dri, drj, s["al"], s["rv"], s["w"])
                rows.append(dict(pair=s["pair"], km=s["km"], median_tau=s["med_tau"], memory_min=mem, A=A, rep=rep,
                                 D=D, detected=D > THR[s["pair"]]))
det = pd.DataFrame(rows); det.round(5).to_csv(RES / "e06_injection_runs.csv", index=False)
summ = det.groupby(["pair", "km", "median_tau", "memory_min", "A"]).agg(detection_rate=("detected", "mean"),
                                                                     mean_D=("D", "mean")).reset_index()
summ.round(4).to_csv(RES / "e06_detectability_by_pair.csv", index=False)
cal = det[det.A == 0].groupby("memory_min").detected.mean()
glob = det.groupby(["memory_min", "A"]).agg(detection_rate=("detected", "mean"), mean_D=("D", "mean")).reset_index()
glob.round(4).to_csv(RES / "e06_detectability_overall.csv", index=False)

# ---------------- reference kernels (signal-dominated, A = 3) and observed kernels
ref = []
for mem in MEMS:
    for rep in range(3):
        items = {b: [] for b in range(len(BINS) - 1)}
        for s in setup:
            dri, drj = inject(s["Ri"], s["Rj"], s["al"], s["rv"], s["tau"], 3.0, mem, s["sd"])
            for b in range(len(BINS) - 1):
                m = s["al"] & (s["tau"] >= BINS[b]) & (s["tau"] < BINS[b + 1])
                items[b].append((dri, drj, m))
        for b in range(len(BINS) - 1):
            rp = pooled_profile(items[b])
            ref.append(dict(memory_min=mem, rep=rep, tau_bin=b, r0=rp[0], r1=rp[1], r2=rp[2], r3=rp[3], centroid=h2.centroid(rp)))
ref = pd.DataFrame(ref); ref.round(4).to_csv(RES / "e06_reference_kernels.csv", index=False)

obs_items = {b: [] for b in range(len(BINS) - 1)}; obs_year = []
for _, r in FAM.iterrows():
    Ri, Rj = h2.lpo_residual_levels(X, r.i, r.j, ST); dri = np.diff(np.r_[np.nan, Ri]); drj = np.diff(np.r_[np.nan, Rj])
    upar, cosang = h2.pair_wind(W[r.i], W[r.j], r.bearing); al, rv, tau = h2.sets(r.km, upar, cosang)
    for b in range(len(BINS) - 1):
        obs_items[b].append((dri, drj, al & (tau >= BINS[b]) & (tau < BINS[b + 1])))
obs = []
for b in range(len(BINS) - 1):
    rp = pooled_profile(obs_items[b])
    yr_c = [h2.centroid(pooled_profile([(u, d, m & np.asarray(idx.year == y)) for u, d, m in obs_items[b]])) for y in range(2021, 2026)]
    obs.append(dict(tau_bin=b, tau_range=f"{BINS[b]}-{BINS[b + 1]} h", r0=rp[0], r1=rp[1], r2=rp[2], r3=rp[3],
                    centroid=h2.centroid(rp), centroid_min_by_year=np.nanmin(yr_c), centroid_max_by_year=np.nanmax(yr_c),
                    ref_centroid_min=ref[ref.tau_bin == b].centroid.min(), ref_centroid_max=ref[ref.tau_bin == b].centroid.max()))
obs = pd.DataFrame(obs); obs.round(4).to_csv(RES / "e06_observed_vs_reference_kernel.csv", index=False)

# ---------------- criterion 3 (D-35)
mids = np.array([(BINS[b] + BINS[b + 1]) / 2 for b in range(len(BINS) - 1)])
rho = spearmanr(mids, obs.centroid)[0]
inside = ((obs.centroid >= obs.ref_centroid_min) & (obs.centroid <= obs.ref_centroid_max)).sum()
rho_ref = spearmanr(np.tile(mids, len(ref) // len(mids)), ref.sort_values(["memory_min", "rep", "tau_bin"]).centroid)[0]
dec = pd.DataFrame([dict(criterion="(i) Spearman(tau bin, observed centroid) > 0", value=f"{rho:.3f}", met=bool(rho > 0)),
                    dict(criterion="(ii) observed centroid inside simulated reference range in >= 4 of 5 bins", value=f"{inside} of 5", met=bool(inside >= 4)),
                    dict(criterion="H2 criterion 3 (kernel shape)", value="", met=bool(rho > 0 and inside >= 4)),
                    dict(criterion="Reference check: simulated centroid increases with tau", value=f"{rho_ref:.3f}", met=bool(rho_ref > 0)),
                    dict(criterion="Calibration: false detection at A = 0 (target about 0.05)", value="; ".join(f"{m} min: {v:.3f}" for m, v in cal.items()), met=None)])
dec.to_csv(RES / "e06_decision.csv", index=False)

# ---------------- Figure 7 (main): observed vs reference lag kernels and centroids
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw={"width_ratios": [1.6, 1]})
cols = plt.cm.viridis(np.linspace(0, 0.9, len(BINS) - 1))
for b in range(len(BINS) - 1):
    rr = ref[ref.tau_bin == b][["r0", "r1", "r2", "r3"]]
    ax[0].fill_between(np.arange(4) + b * 5, rr.min().values, rr.max().values, color=cols[b], alpha=0.25)
    ax[0].plot(np.arange(4) + b * 5, obs.loc[b, ["r0", "r1", "r2", "r3"]].values, "o-", c=cols[b], ms=3)
ax[0].axhline(0, c="0.6", lw=0.6)
ax[0].set_xticks([b * 5 + 1.5 for b in range(len(BINS) - 1)], obs.tau_range, fontsize=6)
ax[0].set_xlabel("Predicted transit-time bin (each group: lags 0, 1, 2, 3 h)"); ax[0].set_ylabel("corr(dR$_{up}$(t-lag), dR$_{down}$(t))")
ax[0].set_title("a  Lag profiles: observed (points) vs simulated (bands)")
ax[1].fill_between(mids, obs.ref_centroid_min, obs.ref_centroid_max, color="C0", alpha=0.25, label="simulated range")
ax[1].errorbar(mids, obs.centroid, yerr=[obs.centroid - obs.centroid_min_by_year, obs.centroid_max_by_year - obs.centroid],
               fmt="ko-", ms=3, capsize=2, label="observed (bars: range over years)")
ax[1].plot([0, 3], [0, 3], ":", c="0.6", lw=0.8, label="lag = transit time")
ax[1].set_xlabel("Predicted transit time (h, bin midpoint)"); ax[1].set_ylabel("Lag centroid (h)")
ax[1].legend(fontsize=6, frameon=False); ax[1].set_title("b  Lag centroid vs transit time")
fig.text(0.01, -0.06, "Aligned-flow hours, 27 pairs pooled, leave-pair-out residual CH$_4$ changes. Simulated: advected AR(1) signals "
         "(memory 20 and 180 min) injected into real residuals with 182-day-shifted wind, A = 3. Development data 2021-2025.", fontsize=6.2)
save(fig, FIG / "figure07_kernel_shape")

# ---------------- Figure S2: detectability vs transit time
fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8), sharey=True)
for k, mem in enumerate(MEMS):
    for A, c in zip(AMPS, ["0.6", "C0", "C1", "C3"]):
        d = summ[(summ.memory_min == mem) & (summ.A == A)].sort_values("median_tau")
        ax[k].plot(d.median_tau, d.detection_rate, "o", ms=3, c=c, label=f"A = {A}")
    ax[k].axhline(0.05, ls=":", c="0.5"); ax[k].set_xlabel("Pair median predicted transit (h)")
    ax[k].set_title(f"{'ab'[k]}  Signal memory {mem} min")
ax[0].set_ylabel(f"Detection rate ({REPS} replicates)"); ax[1].legend(fontsize=6, frameon=False)
save(fig, FIG / "figureS2_detectability")

runmeta.write(EXP, dict(experiment="E06_detectability_kernel", status="exploratory", seed_used=SEED, reps=REPS, amplitudes=AMPS))
print(glob.round(3).to_string(index=False)); print(obs.round(3).to_string(index=False)); print(dec.to_string(index=False))
print(summ[summ.A == 0.2].groupby("memory_min").apply(lambda g: g.sort_values("median_tau")[["pair", "median_tau", "detection_rate"]].to_string(index=False)).to_string())
