"""Pre-freeze verification of the E08 H2 finite-shift null on DEVELOPMENT data (2025-01-01 01:00 to
2025-10-01 00:00, same length and season span as the 2026 window). Checks: K, p-value mechanics, and
exchangeability diagnostics (null D vs seasonal offset of the shift; eligible-hour counts under shifts)."""
import sys, pathlib, numpy as np, pandas as pd
from scipy.stats import spearmanr
EXP = pathlib.Path(__file__).resolve().parent; ROOT = EXP.parents[1]; RES = EXP / "results"
sys.path.insert(0, str(ROOT / "src"))
from wbea.config import CFG
from wbea.io import load_dev
from wbea.wind import composite
from wbea.geometry import pair_table
from wbea import h2, runmeta
P = load_dev(); ST = CFG["stations"]["usable"]; idx = P["AMS 1"].index
win = (idx >= pd.Timestamp("2025-01-01 01:00")) & (idx <= pd.Timestamp("2025-10-01 00:00"))
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); X = (CH - CH.loc["2021":"2023"].median()).loc[win]
W = {s: composite(P[s]).loc[win] for s in ST}; FAM = pair_table(ST, 30.0).reset_index(drop=True)
ndays = int(win.sum() // 24); shifts = np.arange(14, ndays - 14 + 1); K = len(shifts)
Dobs, Dnull, nel = [], np.empty((K, len(FAM))), np.empty((K + 1, len(FAM)))
for p, r in FAM.iterrows():
    Ri, Rj = h2.lpo_residual_levels(X, r.i, r.j, ST); dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
    for k, sh in enumerate(np.r_[0, shifts]):
        up, cs = h2.pair_wind(W[r.i], W[r.j], r.bearing, int(sh) * 24); al, rv, tau = h2.sets(r.km, up, cs)
        D = h2.D_stat(dri, drj, al, rv, h2.weights(tau, al, rv)); nel[k, p] = (al | rv).sum()
        if k == 0: Dobs.append(D)
        else: Dnull[k - 1, p] = D
Dobs = np.array(Dobs); prec = 1 / np.var(Dnull, 0); pooled = (prec * Dobs).sum() / prec.sum(); pn = Dnull @ prec / prec.sum()
offset = np.minimum(shifts, ndays - shifts)                               # days of seasonal displacement
terc = pd.qcut(offset, 3, labels=["short offset", "medium offset", "long offset"])
diag = pd.DataFrame({"offset_tercile": terc, "pooled_null": pn}).groupby("offset_tercile", observed=True).pooled_null.agg(["mean", "std", "count"])
out = pd.DataFrame([dict(window_days=ndays, K=K, min_p=1 / (K + 1), pooled_D_dev=pooled, p_dev=(1 + (pn >= pooled).sum()) / (K + 1),
                         spearman_null_vs_offset=spearmanr(offset, pn)[0], spearman_p=spearmanr(offset, pn)[1],
                         eligible_hours_real=nel[0].sum(), eligible_hours_shift_median=np.median(nel[1:].sum(1)),
                         eligible_hours_shift_p5=np.percentile(nel[1:].sum(1), 5), eligible_hours_shift_p95=np.percentile(nel[1:].sum(1), 95))])
out.round(4).to_csv(RES / "h2_null_verification_jan_sep_dev.csv", index=False); diag.round(4).to_csv(RES / "h2_null_by_offset_tercile_dev.csv")
runmeta.write(RES, dict(experiment="pre-freeze H2 null verification (dev Jan-Sep 2025)")); (RES / "run_metadata.json").rename(RES / "h2_null_verification_run_metadata.json")
print(out.round(4).T.to_string()); print(diag.round(4).to_string())
