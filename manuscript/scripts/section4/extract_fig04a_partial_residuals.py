"""PLOTTING-ONLY extraction (researcher-authorised) of the E04 partial residuals for Fig. 4(a).
The code below is copied from experiments/E04_stability_elasticity/run_e04.py: data preparation, response(), design() and
fit() (lines 15-31), and the residualisation (lines 114-116). The bootstrap is omitted because it does not affect the
residuals. No model is changed. The extraction must reproduce the saved E04 primary coefficient and sample size before
any data are written."""
import sys, pathlib, json, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT / "src"))
from wbea.config import CFG
from wbea.io import load_dev
from wbea.wind import composite
OUT = ROOT / "manuscript/data/section4"; OUT.mkdir(parents=True, exist_ok=True)
# ---- verbatim from run_e04.py (data preparation, response, design, fit)
P = load_dev(); ST = CFG["stations"]["usable"]; idx = P["AMS 1"].index
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST})
REF = slice(str(CFG["split"]["reference_years"][0]), str(CFG["split"]["reference_years"][-1]))
X = CH - CH.loc[REF].median()
CORE, KMIN = CFG["stations"]["h1_core_response"], CFG["stations"]["h1_core_kmin"]
A5 = P["AMS 5"]
def z(s):
    return (s - s.loc[REF].mean()) / s.loc[REF].std()
S = z(A5["AT90 (C)"] - A5["AT20 (C)"]); LU = np.log(composite(A5).ws + 0.5)
CELL = pd.Series(idx.year * 10000 + idx.month * 100 + idx.hour, index=idx)
def response(stations=CORE, kmin=KMIN, data=X):
    return data[stations].median(axis=1).where(data[stations].notna().sum(1) >= kmin)
def design(y, xs, mask=None):
    d = pd.concat([y.rename("y")] + [x.rename(f"x{k}") for k, x in enumerate(xs)] + [CELL.rename("cell")], axis=1).dropna()
    if mask is not None:
        d = d[mask.reindex(d.index).fillna(False).astype(bool)]
    return d
def fit(d):
    cols = [c for c in d.columns if c.startswith("x")]
    g = d.groupby("cell")[["y"] + cols].transform("mean")
    Z = d[["y"] + cols].values - g.values
    return np.linalg.lstsq(Z[:, 1:], Z[:, 0], rcond=None)[0]
Y = response(); d_dir = design(Y, [S, LU])
b_dir = fit(d_dir)[0]
# ---- verbatim residualisation (run_e04.py lines 114-116)
yv = d_dir.y; cm = d_dir.groupby("cell").y.transform("mean")
ry = yv - cm; rs = d_dir.x0 - d_dir.groupby("cell").x0.transform("mean"); rl = d_dir.x1 - d_dir.groupby("cell").x1.transform("mean")
rl_y = ry - np.polyval(np.polyfit(rl, ry, 1), rl); rl_s = rs - np.polyval(np.polyfit(rl, rs, 1), rl)
# ---- verification against saved E04 outputs BEFORE writing
saved = pd.read_csv(ROOT / "experiments/E04_stability_elasticity/results/h1_estimates.csv").set_index("label").loc["Direct (with log wind)"]
base = pd.read_csv(ROOT / "experiments/E04_stability_elasticity/results/baselines.csv")
saved_pr2 = float(base[base.model.str.startswith("partial R2 of S")].r2.iloc[0])
slope_fwl = float(np.polyfit(rl_s, rl_y, 1)[0]); pr2 = float(np.corrcoef(rl_y, rl_s)[0, 1] ** 2)
chk = dict(n_hours=(len(d_dir), int(saved.n_hours)), n_cells=(int(d_dir.cell.nunique()), int(saved.n_cells)),
           coefficient_fit=(round(float(b_dir), 5), float(saved.estimate)), coefficient_residual_slope=(round(slope_fwl, 5), float(saved.estimate)),
           partial_r2=(round(pr2, 4), saved_pr2))
ok = all(a == b for a, b in chk.values()); print(json.dumps({k: list(v) for k, v in chk.items()}, indent=1), "\nALL MATCH:", ok)
if not ok: sys.exit("extraction does not reproduce saved E04 outputs; nothing written")
q = pd.qcut(rl_s, 25, labels=False); bins = pd.DataFrame({"S_bin_mean": rl_s.groupby(q).mean(), "y_bin_mean": rl_y.groupby(q).mean()})
pd.DataFrame({"time_mst_hour_ending": d_dir.index, "S_partial_residual_sd": rl_s.values, "CH4_partial_residual_ppm": rl_y.values}).to_csv(OUT / "fig04a_partial_residuals.csv.gz", index=False, float_format="%.6f")
bins.round(6).to_csv(OUT / "fig04a_quantile_bin_means.csv", index_label="bin")
(OUT / "fig04a_extraction_verification.json").write_text(json.dumps(dict(source="experiments/E04_stability_elasticity/run_e04.py (lines 15-31, 114-116), copied verbatim",
    checks={k: dict(extracted=v[0], saved=v[1], match=v[0] == v[1]) for k, v in chk.items()}, b_dir_full_precision=float(b_dir), n_rows=len(d_dir)), indent=1))
print("written:", len(d_dir), "rows")
