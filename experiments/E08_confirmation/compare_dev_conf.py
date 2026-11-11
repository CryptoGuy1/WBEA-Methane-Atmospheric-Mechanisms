"""Development vs confirmation comparison (frozen protocol section 5: reduced-network development benchmarks are
descriptive, like-for-like comparisons only; they do not alter any E08 decision)."""
import sys, pathlib, json, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "src"))
from wbea.config import CFG
from wbea.io import load_dev
from wbea.wind import composite
from wbea import e08
C = ROOT / "experiments/E08_confirmation/confirmation_2026"; conf = json.loads((C / "e08_results.json").read_text()); EXCL = conf["log"]["excluded_stations"]
P = load_dev(); ST = CFG["stations"]["usable"]; idx = P["AMS 1"].index; CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); X = CH - CH.loc["2021":"2023"].median()
core = [s for s in CFG["stations"]["h1_core_response"] if s not in EXCL]; Y = X[core].median(1).where(X[core].notna().sum(1) >= 5)
S0 = P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"]; Sz = (S0 - S0.loc["2021":"2023"].mean()) / S0.loc["2021":"2023"].std(); LU = np.log(composite(P["AMS 5"]).ws + 0.5)
h1r = e08.h1_estimate(Y.to_numpy(), Sz.to_numpy(), Sz.shift(-24).to_numpy(), LU.to_numpy(), idx, 500, np.random.default_rng(20261190 + 11))
e04 = pd.read_csv(ROOT / "experiments/E04_stability_elasticity/results/h1_estimates.csv").set_index("label")
e05 = pd.read_csv(ROOT / "experiments/E05_directional_coupling/results/h2_pair_statistics.csv"); keep = ~(e05.i.isin(EXCL) | e05.j.isin(EXCL)); w = 1 / e05.null_sd ** 2
r3 = pd.read_csv(ROOT / "experiments/PRE_E08/results/h3_jan_sep_contrasts.csv"); r3r = r3[~r3.station.isin(EXCL)]
rows = [
 dict(estimand="H1 wind-adjusted association (ppm/SD)", development_full="0.048 (0.041 to 0.052) [E04]", development_reduced_network=f"{h1r['b1_primary']:.3f} ({h1r['b1_primary_ci'][0]:.3f} to {h1r['b1_primary_ci'][1]:.3f})",
      confirmation_2026=f"{conf['H1']['b1_primary']:.3f} ({conf['H1']['b1_primary_ci'][0]:.3f} to {conf['H1']['b1_primary_ci'][1]:.3f})", decision=conf["H1"]["decision"]["confirmed"]),
 dict(estimand="H1 next-day negative control (ppm/SD)", development_full="0.000 (-0.005 to 0.003) [E04]", development_reduced_network=f"{h1r['b_nc']:.4f} ({h1r['b_nc_ci'][0]:.4f} to {h1r['b_nc_ci'][1]:.4f})",
      confirmation_2026=f"{conf['H1']['b_nc']:.4f} ({conf['H1']['b_nc_ci'][0]:.4f} to {conf['H1']['b_nc_ci'][1]:.4f}); ratio {conf['H1']['ratio_nc']:.2f} ({conf['H1']['ratio_nc_ci'][0]:.2f} to {conf['H1']['ratio_nc_ci'][1]:.2f})", decision="not flagged (|ratio| < 0.5)"),
 dict(estimand="H2 pooled directional contrast D", development_full="0.128 (0.108 to 0.155) [E05, 27 pairs]", development_reduced_network=f"{float((w[keep] * e05.D[keep]).sum() / w[keep].sum()):.3f} [E05 weights, {int(keep.sum())} pairs]",
      confirmation_2026=f"{conf['H2']['pooled_D']:.3f}, p = {conf['H2']['p']:.4f} (K = {conf['H2']['K']}), {conf['H2']['pairs_used']} pairs", decision=conf["H2"]["confirmed"]),
 dict(estimand="H2 lag centroids (h) by transit bin", development_full="0.25, 0.39, 0.73, 1.11, 1.51 [E06]", development_reduced_network="-",
      confirmation_2026=", ".join(f"{c:.2f}" for c in conf["H2"]["centroids"]), decision=conf["H2"]["centroid_rule"]["met"]),
 dict(estimand="H3 meteorology-mix share (Jan-Sep)", development_full="0.026 (-0.028 to 0.124) [E07-r3, all year pairs]",
      development_reduced_network=f"{e08.projection_share(r3r.composition, r3r.total):.3f} [E07-r3 contrasts, {len(r3r)} without {', '.join(EXCL)}]",
      confirmation_2026=f"{conf['H3']['share']:.3f} ({conf['H3']['ci_lo']:.3f} to {conf['H3']['ci_hi']:.3f}), {conf['H3']['contrasts_estimable']} contrasts", decision=conf["H3"]["confirmed"])]
pd.DataFrame(rows).to_csv(C / "development_vs_confirmation.csv", index=False); print(pd.DataFrame(rows).to_string(index=False))
