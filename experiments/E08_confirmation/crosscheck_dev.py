"""Cross-check E08 implementations against established development implementations on common development inputs."""
import sys, pathlib, json, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "src")); OUT = ROOT / "experiments/E08_confirmation/crosscheck"; OUT.mkdir(exist_ok=True)
from wbea.config import CFG
from wbea.io import load_dev
from wbea.wind import composite
from wbea.geometry import pair_table
from wbea import h2, e08
P = load_dev(); ST = CFG["stations"]["usable"]; idx = P["AMS 1"].index; CORE = CFG["stations"]["h1_core_response"]
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); X = CH - CH.loc["2021":"2023"].median(); res = {}
# H1: E08 estimator on the full development period vs E04 primary (direct) estimate
S0 = P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"]; Sz = (S0 - S0.loc["2021":"2023"].mean()) / S0.loc["2021":"2023"].std()
LU = np.log(composite(P["AMS 5"]).ws + 0.5); Y = X[CORE].median(1).where(X[CORE].notna().sum(1) >= 5)
h1 = e08.h1_estimate(Y.to_numpy(), Sz.to_numpy(), Sz.shift(-24).to_numpy(), LU.to_numpy(), idx, 5, np.random.default_rng(0))
e04 = pd.read_csv(ROOT / "experiments/E04_stability_elasticity/results/h1_estimates.csv").set_index("label")
res["H1"] = dict(e08_point=h1["b1_primary"], e04_point=float(e04.loc["Direct (with log wind)", "estimate"]),
                 e08_joint_nc=h1["b_nc"], e04_nc=float(e04.loc["Negative control: coefficient on S(t+24), given S(t)", "estimate"]))
# H2: per-pair D (shift 0) via the shared library on the full development period vs E05; pooled with E05 weights
FAM = pair_table(ST, 30.0).reset_index(drop=True); W = {s: composite(P[s]) for s in ST}
e05 = pd.read_csv(ROOT / "experiments/E05_directional_coupling/results/h2_pair_statistics.csv").set_index("pair"); D = []
for _, r in FAM.iterrows():
    Ri, Rj = h2.lpo_residual_levels(X, r.i, r.j, ST); dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
    up, cs = h2.pair_wind(W[r.i], W[r.j], r.bearing); al, rv, tau = h2.sets(r.km, up, cs); D.append(h2.D_stat(dri, drj, al, rv, h2.weights(tau, al, rv)))
D = np.array(D); e5 = e05.loc[[f"{a}->{b}" for a, b in zip(FAM.i, FAM.j)]]; w = (1 / e5.null_sd ** 2).values
res["H2"] = dict(max_abs_pair_D_difference=float(np.abs(D - e5.D.values).max()), pooled_with_E05_weights=float((w * D).sum() / w.sum()),
                 e05_pooled=0.1283)
# H3: E08 contrasts (2025 vs each of 2021-2024, Jan-Sep) vs E07-r3 contrasts for the same year pairs
src = (ROOT / "experiments/E08_confirmation/run_e08_descriptive.py").read_text()
start = src.index("def unit_counts("); end = src.index("devC = unit_counts(")
g = dict(np=np, pd=pd, P={s: P[s] for s in ST}, DEV=P, CFG=CFG, composite=composite, CUTS=S0.loc["2021":"2023"].quantile([1/3, 2/3]).values,
         P95=CH.loc["2021":"2023"].quantile(.95))
from wbea.solar import elevation_deg; g["elevation_deg"] = elevation_deg
exec(src[start:end], g)
cnt = g["unit_counts"](P, idx, [2021, 2022, 2023, 2024, 2025], ST)
devC = {s: {y: cnt[s][y] for y in (2021, 2022, 2023, 2024)} for s in ST}; conC = {s: {2025: cnt[s][2025]} for s in ST}
c8, s8, _, _ = e08.h3_run(conC, devC, [2021, 2022, 2023, 2024], 2025, ST, 0, np.random.default_rng(0))
r3 = pd.read_csv(ROOT / "experiments/PRE_E08/results/h3_jan_sep_contrasts.csv"); r3 = r3[r3.year_b == 2025].rename(columns={"year_a": "dev_year"})
m = c8.merge(r3, on=["station", "dev_year"], suffixes=("_e08", "_e07r3"))
m["d_comp"] = m.composition_e08 - m.composition_e07r3; m["d_total"] = m.total_e08 - m.total_e07r3
m[["station", "dev_year", "composition_e08", "composition_e07r3", "total_e08", "total_e07r3", "d_comp", "d_total", "n_groups_e08", "n_groups_e07r3"]].round(6).to_csv(OUT / "h3_contrast_comparison.csv", index=False)
res["H3"] = dict(contrasts=len(m), max_abs_d_composition=float(m.d_comp.abs().max()), max_abs_d_total=float(m.d_total.abs().max()),
                 same_n_groups=int((m.n_groups_e08 == m.n_groups_e07r3).sum()), share_e08_subset=s8,
                 share_e07r3_same_subset=e08.projection_share(m.composition_e07r3, m.total_e07r3))
(OUT / "crosscheck_results.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))
