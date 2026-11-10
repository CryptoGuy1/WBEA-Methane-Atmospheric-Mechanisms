"""E06 review corrections (D-38). Original E06 outputs are not modified; results go to results/review_*.
(1) Continuous-source injection independent of the detector's eligibility mask.
(2) Zero-injection calibration over 40 distinct no-transport backgrounds."""
import sys, pathlib, numpy as np, pandas as pd
from scipy.signal import lfilter
from scipy.stats import binomtest
EXP = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(EXP.parents[1] / "src"))
src = (EXP / "run_e06.py").read_text().split("# ---------------- detectability")[0]
g = {"__file__": str(EXP / "run_e06.py"), "__name__": "e06_setup"}; exec(compile(src, "run_e06_setup", "exec"), g)
from wbea import h2, runmeta
SEED = g["SEED"] + 200; rng = np.random.default_rng(SEED); g["rng"] = rng
setup, BINS, pooled_profile, inject, N, THR, W, FAM, X, ST = (g[k] for k in
    ["setup", "BINS", "pooled_profile", "inject", "N", "THR", "W", "FAM", "X", "ST"])
RES = EXP / "results"

# per-pair continuous-wind quantities (same 182-day-shifted wind as E06)
for s, (_, r) in zip(setup, FAM.iterrows()):
    upar, cosang = h2.pair_wind(W[r.i], W[r.j], r.bearing, g["SHIFT"])
    s["upar"], s["cos"] = upar, cosang

def inject_continuous(s, A, mem):
    q = lfilter([1.0], [1.0, -np.exp(-1.0 / mem)], rng.standard_normal(N * 60 + 600))[600:]
    k = np.arange(N * 60); hr = k // 60
    up, c = s["upar"][hr], np.abs(np.nan_to_num(s["cos"][hr]))
    ok = np.isfinite(up)
    tau = np.minimum(s["km"] / (3.6 * np.maximum(np.abs(np.nan_to_num(up)), 0.5)), 6.0)
    qd = 0.8 * c * q[np.clip(k - np.round(60 * tau).astype(int), 0, None)] * ok
    i_up = np.nan_to_num(up) >= 0
    si = np.where(i_up, q, qd).reshape(N, 60).mean(1); sj = np.where(i_up, qd, q).reshape(N, 60).mean(1)
    sc = A * s["sd"] / np.nanstd(np.diff(si))
    return np.diff(np.r_[np.nan, s["Ri"] + sc * si]), np.diff(np.r_[np.nan, s["Rj"] + sc * sj])

# ---------- (1a) detectability: original vs continuous
rows = []
for s in setup:
    for model in ("original (mask-gated)", "continuous source"):
        for mem in (180, 20):
            for A in (0.2, 0.4):
                for rep in range(4):
                    dri, drj = (inject(s["Ri"], s["Rj"], s["al"], s["rv"], s["tau"], A, mem, s["sd"]) if model.startswith("original")
                                else inject_continuous(s, A, mem))
                    D = h2.D_stat(dri, drj, s["al"], s["rv"], s["w"])
                    rows.append(dict(model=model, pair=s["pair"], memory_min=mem, A=A, rep=rep, D=D, detected=D > THR[s["pair"]]))
det = pd.DataFrame(rows); det.round(5).to_csv(RES / "review_continuous_injection_runs.csv", index=False)
dsum = det.groupby(["model", "memory_min", "A"]).agg(detection_rate=("detected", "mean"), mean_D=("D", "mean")).reset_index()
dsum.round(4).to_csv(RES / "review_continuous_detectability.csv", index=False)

# ---------- (1b) lag centroids: original vs continuous (memory 180)
cent = []
for model in ("original (mask-gated)", "continuous source"):
    for A in (0.3, 3.0):
        for rep in range(2):
            items = {b: [] for b in range(len(BINS) - 1)}
            for s in setup:
                dri, drj = (inject(s["Ri"], s["Rj"], s["al"], s["rv"], s["tau"], A, 180, s["sd"]) if model.startswith("original")
                            else inject_continuous(s, A, 180))
                for b in range(len(BINS) - 1):
                    items[b].append((dri, drj, s["al"] & (s["tau"] >= BINS[b]) & (s["tau"] < BINS[b + 1])))
            c = [h2.centroid(pooled_profile(items[b])) for b in range(len(BINS) - 1)]
            cent.append(dict(model=model, A=A, rep=rep, **{f"centroid_bin{b}": c[b] for b in range(5)}))
cent = pd.DataFrame(cent); cg = cent.groupby(["model", "A"]).mean(numeric_only=True).drop(columns="rep").reset_index()
obs = pd.read_csv(RES / "e06_observed_vs_reference_kernel.csv").centroid.values
cg["sse_vs_observed"] = ((cg[[f"centroid_bin{b}" for b in range(5)]].values - obs) ** 2).sum(1)
cg.round(4).to_csv(RES / "review_continuous_centroids.csv", index=False)

# ---------- (2) zero-injection calibration over 40 distinct backgrounds
ndays = N // 24; cand = np.setdiff1d(np.arange(14, ndays - 14), np.arange(182 - 14, 182 + 15))
shifts = rng.choice(cand, 40, replace=False) * 24; cal = []
for (_, r), s in zip(FAM.iterrows(), setup):
    Ri, Rj = h2.lpo_residual_levels(X, r.i, r.j, ST); dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
    for sh in shifts:
        upar, cosang = h2.pair_wind(W[r.i], W[r.j], r.bearing, sh); al, rv, tau = h2.sets(r.km, upar, cosang)
        D = h2.D_stat(dri, drj, al, rv, h2.weights(tau, al, rv)); cal.append(dict(pair=s["pair"], shift_days=sh // 24, D=D, detected=D > THR[s["pair"]]))
cal = pd.DataFrame(cal); cal.round(5).to_csv(RES / "review_zero_injection_calibration_runs.csv", index=False)
k, n = int(cal.detected.sum()), len(cal); ci = binomtest(k, n).proportion_ci()
per_bg = cal.groupby("shift_days").detected.mean()
calsum = pd.DataFrame([dict(backgrounds=40, pair_tests=n, false_detections=k, rate=k / n, ci_lo=ci.low, ci_hi=ci.high,
                            backgrounds_with_any_detection=int((per_bg > 0).sum()), max_rate_one_background=per_bg.max(),
                            note="pair tests within a background share CH4 and wind; the CI treats them as independent and is therefore too narrow")])
calsum.round(4).to_csv(RES / "review_zero_injection_calibration.csv", index=False)
runmeta.write(RES, dict(experiment="E06 review corrections (D-38)", seed_used=SEED)); (RES / "run_metadata.json").rename(RES / "review_run_metadata.json")
print(dsum.round(3).to_string(index=False)); print(cg.round(3).to_string(index=False)); print("observed", np.round(obs, 3)); print(calsum.round(4).to_string(index=False))
