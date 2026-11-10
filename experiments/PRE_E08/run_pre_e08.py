"""Pre-E08 development tasks (2021-2025 data only; no 2026 methane values).
 F3  (D-47): H3 benchmark on the common 1 Jan - 31 Oct window (E07-r2).
 F4  (D-48): enumerate admissible whole-day shifts for a series of the confirmation length and verify the
            finite-shift p-value procedure on a development window of equal length.
 F5  (D-50): development benchmark of the episode regime distribution.
 X4  availability: coverage of elevated-wind variables (AMS 5 tower 45/75/90 m; ERA5 100 m)."""
import sys, pathlib, time, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent; ROOT = EXP.parents[1]; RES = EXP / "results"; RES.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "src"))
from wbea.config import CFG
from wbea.io import load_dev, load_era5
from wbea.wind import composite
from wbea.geometry import pair_table
from wbea import h2, runmeta

# ---------------- F3: H3 on Jan-Oct window, re-using the registered E07 code path
src = (ROOT / "experiments/E07_composition_decomposition/run_e07.py").read_text().split("# ---------------- primary")[0]
g = {"__file__": str(ROOT / "experiments/E07_composition_decomposition/run_e07.py"), "__name__": "e07_setup"}
exec(compile(src, "run_e07_setup", "exec"), g)
g["rng"] = np.random.default_rng(CFG["project"]["seed"] + 70)
idx = g["idx"]; g["WIN"][:] = np.asarray((idx.month <= 10) | ((idx.month == 11) & (idx.day == 1) & (idx.hour == 0)))
E95 = g["CH"].gt(g["REF"].quantile(.95)).astype(float).where(g["CH"].notna())
H, Xn = g["counts"](E95); df, share, bs, G = g["analyse"](H, Xn, nb=1000)
f3 = pd.DataFrame([dict(version="E07-r2 (Jan-Oct, D-47)", share=share, ci_lo=np.percentile(bs, 2.5), ci_hi=np.percentile(bs, 97.5),
                        contrasts=len(df), median_effective_regimes=float(np.median([len(v) for v in G.values()]))),
                   dict(version="E07 original (Jan-Nov, D-40), for reference", share=0.0269, ci_lo=-0.0396, ci_hi=0.1264, contrasts=120,
                        median_effective_regimes=12.0)])
f3.round(4).to_csv(RES / "f3_h3_jan_oct_benchmark.csv", index=False); df.round(6).to_csv(RES / "f3_h3_jan_oct_contrasts.csv", index=False)

# ---------------- F4: admissible shifts and finite-shift verification on a development window
conf_start, conf_end = pd.Timestamp("2025-12-02 01:00"), pd.Timestamp("2026-11-09 00:00")   # dates only; no data read
n_days_conf = int(((conf_end - conf_start) / pd.Timedelta(hours=1) + 1) // 24)
K_conf = len(range(14, n_days_conf - 14 + 1))
P = load_dev(); ST = CFG["stations"]["usable"]; didx = P["AMS 1"].index
win = didx[-n_days_conf * 24:]                                  # last 342 days of development data
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); X = (CH - CH.loc["2021":"2023"].median()).loc[win]
W = {s: composite(P[s]).loc[win] for s in ST}; FAM = pair_table(ST, 30.0).reset_index(drop=True)
shifts = np.arange(14, n_days_conf - 14 + 1) * 24
t0 = time.time(); Dobs = []; Dnull = np.empty((len(shifts), len(FAM)))
for p, r in FAM.iterrows():
    Ri, Rj = h2.lpo_residual_levels(X, r.i, r.j, ST); dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
    for k, sh in enumerate(np.r_[0, shifts]):
        upar, cosang = h2.pair_wind(W[r.i], W[r.j], r.bearing, int(sh)); al, rv, tau = h2.sets(r.km, upar, cosang)
        D = h2.D_stat(dri, drj, al, rv, h2.weights(tau, al, rv))
        if k == 0: Dobs.append(D)
        else: Dnull[k - 1, p] = D
Dobs = np.array(Dobs); ok = np.isfinite(Dobs) & np.isfinite(Dnull).all(0)
prec = 1 / np.nanvar(Dnull, 0); pooled = np.nansum(prec[ok] * Dobs[ok]) / prec[ok].sum()
pooled_null = (Dnull[:, ok] @ prec[ok]) / prec[ok].sum(); K = len(shifts)
p_pooled = (1 + (pooled_null >= pooled).sum()) / (K + 1)
Z = (Dobs - Dnull.mean(0)) / Dnull.std(0); Zn = (Dnull - Dnull.mean(0)) / Dnull.std(0); maxZ = np.nanmax(Zn[:, ok], 1)
p_fw = [(1 + (maxZ >= z).sum()) / (K + 1) if np.isfinite(z) else np.nan for z in Z]
f4 = pd.DataFrame([dict(confirmation_days=n_days_conf, admissible_shifts_K=K_conf, min_attainable_p=1 / (K_conf + 1),
                        dev_window=f"{win[0]} to {win[-1]}", dev_window_shifts=K, pooled_D=pooled, p_pooled=p_pooled,
                        pairs_estimable=int(ok.sum()), pairs_familywise_lt_05=int(np.nansum(np.array(p_fw) < .05)),
                        runtime_s=round(time.time() - t0, 1))])
f4.round(5).to_csv(RES / "f4_finite_shift_verification.csv", index=False)

# ---------------- F5: development benchmark of the episode regime distribution (D-50)
S5 = P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"]; upper = S5.loc["2021":"2023"].quantile(2 / 3)
CHd = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); thr = CHd.loc["2021":"2023"].quantile(.95)
blk = ((didx - didx[0]).days // 14).to_numpy(); nb = blk.max() + 1; rng = np.random.default_rng(CFG["project"]["seed"] + 71)
REG = ["stable-low-wind", "intermediate", "advective", "unclassified"]; rows = []; Ostack = []; Hstack = []
for s in ST:
    c = CHd[s]; gap1 = c.isna() & c.shift(1).notna() & c.shift(-1).notna(); cb = c.where(~gap1, (c.shift(1) + c.shift(-1)) / 2)
    above = cb > thr[s]; below = cb.notna() & ~above; onset = (above & below.shift(1, fill_value=False)).to_numpy()
    ws = composite(P[s]).ws; st_ = S5 >= upper
    reg = np.where(S5.isna() | ws.isna(), 3, np.where(st_ & (ws < 1.0), 0, np.where((ws >= 2.5) & ~st_, 2, 1)))
    validh = c.notna().to_numpy()
    O = np.stack([np.bincount(blk[onset & (reg == k)], minlength=nb) for k in range(4)], 1)
    Hh = np.stack([np.bincount(blk[validh & (reg == k)], minlength=nb) for k in range(4)], 1)
    Ostack.append(O); Hstack.append(Hh)
    for k in range(3):
        rows.append(dict(station=s, regime=REG[k], onsets=int(O[:, k].sum()), onset_share=O[:, k].sum() / O[:, :3].sum(),
                         hour_share=Hh[:, k].sum() / Hh[:, :3].sum()))
O = np.sum(Ostack, 0); Hh = np.sum(Hstack, 0); bsr = []
for _ in range(1000):
    d = np.bincount(rng.integers(0, nb, nb), minlength=nb).astype(float); o = d @ O[:, :3]; h = d @ Hh[:, :3]
    bsr.append((o / o.sum()) / (h / h.sum()))
bsr = np.array(bsr); pool = (O[:, :3].sum(0) / O[:, :3].sum()) / (Hh[:, :3].sum(0) / Hh[:, :3].sum())
f5 = pd.DataFrame(rows); f5["enrichment"] = f5.onset_share / f5.hour_share
f5.round(4).to_csv(RES / "f5_dev_regime_distribution_by_station.csv", index=False)
f5p = pd.DataFrame({"regime": REG[:3], "onsets": O[:, :3].sum(0), "onset_share": O[:, :3].sum(0) / O[:, :3].sum(),
                    "hour_share": Hh[:, :3].sum(0) / Hh[:, :3].sum(), "enrichment": pool,
                    "ci_lo": np.percentile(bsr, 2.5, 0), "ci_hi": np.percentile(bsr, 97.5, 0)})
f5p["unclassified_onsets_all_regimes"] = int(O[:, 3].sum()); f5p.round(4).to_csv(RES / "f5_dev_regime_distribution_pooled.csv", index=False)

# ---------------- X4 availability
A5 = P["AMS 5"]; era = load_era5()
av = [dict(variable=f"AMS 5 {v}{h} m", coverage=float(A5[f"{v}{h} ({'km/h' if v == 'WS' else 'deg'})"].notna().mean()))
      for h in (20, 45, 75, 90) for v in ("WS", "WD")]
for s in ["AMS 1", "AMS 13", "AMS 5"]:
    e = era[s]; av.append(dict(variable=f"ERA5 u100/v100 at {s} cell", coverage=float((e.u100.notna() & e.v100.notna()).mean())))
ws = {h: A5[f"WS{h} (km/h)"] / 3.6 for h in (20, 45, 75, 90)}
for h in (45, 75, 90):
    r = (ws[h] / ws[20]).replace([np.inf, -np.inf], np.nan)
    av.append(dict(variable=f"median ratio WS{h}/WS20 at AMS 5", coverage=float(r[ws[20] > 1].median())))
e1 = era["AMS 1"]; s100 = np.hypot(e1.u100, e1.v100); s10 = composite(P["AMS 1"]).ws
av.append(dict(variable="median ratio ERA5 100 m speed / AMS 1 10 m speed", coverage=float((s100 / s10)[s10 > 1].median())))
pd.DataFrame(av).round(3).to_csv(RES / "x4_variable_availability.csv", index=False)
runmeta.write(EXP, dict(experiment="PRE_E08 tasks (F3, F4, F5 dev benchmark, X4 availability)", status="development"))
print(f3.round(4).to_string(index=False)); print(f4.round(4).to_string(index=False)); print(f5p.round(3).to_string(index=False))
print(pd.DataFrame(av).round(3).to_string(index=False))
