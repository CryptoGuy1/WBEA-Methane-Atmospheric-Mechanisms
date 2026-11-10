"""Joint E05+E06 review (2026-11-10): deferred sensitivities RB-08 and RB-09. Pooled D uses the E05
primary precision weights; no new null distribution (descriptive sensitivity only).
 RB-08: hour sets chosen with the pair-mean wind averaged over hours t-3..t (transit window) instead of hour t.
 RB-09: AMS 9 pairs split by the sensor height (10 m vs 20 m) used by AMS 9's composite wind at hour t."""
import sys, pathlib, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(EXP.parents[1] / "src"))
from wbea.config import CFG
from wbea.io import load_dev
from wbea.wind import composite
from wbea.geometry import pair_table
from wbea import h2, runmeta

RES = EXP / "results"; P = load_dev(); ST = CFG["stations"]["usable"]
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); X = CH - CH.loc["2021":"2023"].median()
W = {s: composite(P[s]) for s in ST}; FAM = pair_table(ST, 30.0).reset_index(drop=True)
E05 = pd.read_csv(RES / "h2_pair_statistics.csv"); prec = (1 / E05.null_sd ** 2).values

class Avg:                                           # wind object with u, v averaged over t-3..t
    def __init__(self, w): self.u = w.u.rolling(4, min_periods=3).mean(); self.v = w.v.rolling(4, min_periods=3).mean()

rows, Dp, Da = [], [], []
for k, r in FAM.iterrows():
    Ri, Rj = h2.lpo_residual_levels(X, r.i, r.j, ST); dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
    for lab, wi, wj, store in [("receptor hour (E05)", W[r.i], W[r.j], Dp), ("averaged t-3..t", Avg(W[r.i]), Avg(W[r.j]), Da)]:
        upar, cosang = h2.pair_wind(wi, wj, r.bearing); al, rv, tau = h2.sets(r.km, upar, cosang)
        store.append(h2.D_stat(dri, drj, al, rv, h2.weights(tau, al, rv)))
    if "AMS 9" in (r.i, r.j):
        hgt = W["AMS 9"].height_m.to_numpy()
        upar, cosang = h2.pair_wind(W[r.i], W[r.j], r.bearing); al, rv, tau = h2.sets(r.km, upar, cosang); w = h2.weights(tau, al, rv)
        for hv in (10.0, 20.0):
            m = hgt == hv
            rows.append(dict(pair=f"{r.i}->{r.j}", ams9_wind_height_m=hv, n_aligned=int((al & m).sum()),
                             n_reversed=int((rv & m).sum()), D=h2.D_stat(dri, drj, al & m, rv & m, w)))
Dp, Da = np.array(Dp), np.array(Da)
s8 = pd.DataFrame([dict(analysis="receptor-hour wind (E05 primary, recomputed)", pooled_D=np.sum(prec * Dp) / prec.sum(), pairs_D_positive=int((Dp > 0).sum())),
                   dict(analysis="wind averaged over t-3..t", pooled_D=np.sum(prec * Da) / prec.sum(), pairs_D_positive=int((Da > 0).sum()))])
s8.round(4).to_csv(RES / "review_rb08_transit_window_wind.csv", index=False)
s9 = pd.DataFrame(rows); s9.round(4).to_csv(RES / "review_rb09_ams9_height.csv", index=False)
runmeta.write(RES, dict(experiment="E05+E06 joint review sensitivities")); (RES / "run_metadata.json").rename(RES / "review_run_metadata.json")
print(s8.round(4).to_string(index=False)); print(s9.round(3).to_string(index=False))
