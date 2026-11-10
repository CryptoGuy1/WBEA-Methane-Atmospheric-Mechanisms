"""E07-r1 review corrections (D-43). Exploratory, development stage. Original E07 outputs are not modified.
Outputs: results/r1_*.csv"""
import sys, pathlib, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent
src = (EXP / "run_e07.py").read_text().split("# ---------------- primary")[0]
g = {"__file__": str(EXP / "run_e07.py"), "__name__": "e07_setup"}; exec(compile(src, "run_e07_setup", "exec"), g)
from wbea import runmeta
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, brier_score_loss
SEED = g["SEED"] + 100; g["rng"] = np.random.default_rng(SEED)
ST, YEARS, PAIRS, P, idx, CH, REF, S5, WIN = (g[k] for k in ["ST", "YEARS", "PAIRS", "P", "idx", "CH", "REF", "S5", "WIN"])
counts, analyse, groups_for, composite = g["counts"], g["analyse"], g["groups_for"], g["composite"]
RES = EXP / "results"
E95 = CH.gt(REF.quantile(.95)).astype(float).where(CH.notna()); H, Xn = counts(E95)

# ---------- (3) merge structure
_, s0, _, G = analyse(H, Xn)
eff = pd.DataFrame([dict(station=k[0], year_a=YEARS[k[1]], year_b=YEARS[k[2]], effective_regimes=len(v),
                         merged_cells=int(sum(len(x) for x in v if len(x) > 1))) for k, v in G.items()])
eff.to_csv(RES / "r1_effective_regimes_by_contrast.csv", index=False)
eff.groupby("station").effective_regimes.describe()[["min", "50%", "max"]].to_csv(RES / "r1_effective_regimes_by_station.csv")
pooled = np.zeros(18)
for v in G.values():
    for x in v:
        if len(x) > 1: pooled[x] += 1
names = [f"{['unstable', 'neutral', 'stable'][c // 6]}|{['<1', '1-2.5', '>=2.5'][(c % 6) // 2]}|{['day', 'night'][c % 2]}" for c in range(18)]
pd.DataFrame({"cell": names, "share_of_contrasts_pooled": pooled / len(G)}).round(3).to_csv(RES / "r1_cell_pooling_frequency.csv", index=False)

# ---------- (4) regime-resolution sensitivity
six = {k: [np.array([st * 6 + w * 2 + nt for w in range(3)]) for nt in (0, 1) for st in range(3)] for k in G}
_, s6, bs6, _ = analyse(H, Xn, groups=six, nb=300)
g["MINH"] = 25; _, s25, _, G25 = analyse(H, Xn); g["MINH"] = 50
res = pd.DataFrame([dict(analysis="Registered primary (18 regimes, 50 h merge rule)", share=s0, ci_lo=np.nan, ci_hi=np.nan, note="see h3_sensitivity.csv for CI"),
                    dict(analysis="Fixed 6 regimes (stability x day/night; wind pooled; no merging)", share=s6,
                         ci_lo=np.percentile(bs6, 2.5), ci_hi=np.percentile(bs6, 97.5), note="300 joint block-bootstrap replicates"),
                    dict(analysis="18 regimes, 25 h merge rule (descriptive)", share=s25, ci_lo=np.nan, ci_hi=np.nan,
                         note=f"median effective regimes {np.median([len(v) for v in G25.values()]):.0f}")])
res.round(4).to_csv(RES / "r1_regime_resolution_sensitivity.csv", index=False)

# ---------- (2) forward-year validation of the boosted-tree model
rows = []
for s in ST:
    w = composite(P[s])
    F = pd.DataFrame({"S": S5, "ws": w.ws, "wds": np.sin(np.deg2rad(w.wd)), "wdc": np.cos(np.deg2rad(w.wd)),
                      "at2": P[s]["AT2 (C)"], "hour": idx.hour, "doy": idx.dayofyear, "year": idx.year}, index=idx)
    ok = F.notna().all(1) & E95[s].notna() & WIN; y = E95[s]
    for ty in (2024, 2025):
        tr = ok & (idx.year < ty); te = ok & (idx.year == ty)
        clim = y[tr].groupby([idx[tr].month, idx[tr].hour]).mean()
        pc = pd.Series(list(zip(idx[te].month, idx[te].hour)), index=idx[te]).map(clim).fillna(y[tr].mean())
        out = dict(station=s, test_year=ty, n_test=int(te.sum()), observed_rate=y[te].mean(),
                   brier_climatology=brier_score_loss(y[te], pc), auc_climatology=roc_auc_score(y[te], pc))
        for lab, cols in [("with_year", list(F.columns)), ("no_year", [c for c in F.columns if c != "year"])]:
            m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, random_state=SEED).fit(F.loc[tr, cols], y[tr])
            p = m.predict_proba(F.loc[te, cols])[:, 1]
            out.update({f"brier_{lab}": brier_score_loss(y[te], p), f"auc_{lab}": roc_auc_score(y[te], p), f"predicted_rate_{lab}": p.mean()})
        rows.append(out)
fv = pd.DataFrame(rows); fv.round(4).to_csv(RES / "r1_deweathering_forward_validation.csv", index=False)
summ = fv.groupby("test_year")[["observed_rate", "predicted_rate_with_year", "predicted_rate_no_year", "brier_climatology", "brier_with_year",
                                 "brier_no_year", "auc_climatology", "auc_with_year", "auc_no_year"]].mean()
summ.round(4).to_csv(RES / "r1_deweathering_forward_validation_summary.csv")
runmeta.write(RES, dict(experiment="E07-r1 review corrections (D-43)", seed_used=SEED)); (RES / "run_metadata.json").rename(RES / "r1_run_metadata.json")
print(res.round(4).to_string(index=False)); print(eff.effective_regimes.describe().round(1).to_dict())
print(pd.read_csv(RES / "r1_cell_pooling_frequency.csv").sort_values("share_of_contrasts_pooled", ascending=False).head(6).to_string(index=False))
print(summ.round(4).T.to_string())
print(fv[["station", "test_year", "observed_rate", "predicted_rate_with_year", "predicted_rate_no_year"]].round(3).to_string(index=False))
