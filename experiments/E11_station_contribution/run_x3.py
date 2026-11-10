"""X3 (D-57): descriptive station-contribution tables from saved E04 and E05 outputs. No optimisation and no
siting or decommissioning statements. Development data; exploratory."""
import sys, pathlib, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent; ROOT = EXP.parents[1]; RES = EXP / "results"; RES.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "src"))
from wbea import runmeta
from wbea.geometry import stations
e04 = pd.read_csv(ROOT / "experiments/E04_stability_elasticity/results/h1_estimates.csv")
prim = e04[e04.label == "Direct (with log wind)"].iloc[0]
h1 = e04[e04.group == "response"].copy()
h1["change_vs_primary"] = h1.estimate - prim.estimate; h1["ci_width"] = h1.ci_hi - h1.ci_lo
h1["ci_width_ratio_vs_primary"] = h1.ci_width / (prim.ci_hi - prim.ci_lo)
h1[["label", "n_hours", "estimate", "ci_lo", "ci_hi", "change_vs_primary", "ci_width_ratio_vs_primary"]].round(4) \
  .to_csv(RES / "x3_h1_station_contribution.csv", index=False)
e05 = pd.read_csv(ROOT / "experiments/E05_directional_coupling/results/h2_pair_statistics.csv")
null = pd.read_csv(ROOT / "experiments/E05_directional_coupling/results/h2_null_distribution.csv.gz")
prec = 1 / e05.null_sd ** 2; XY = stations(); rows = []
for s in sorted(set(e05.i) | set(e05.j), key=lambda x: int(x.split()[1])):
    keep = ~((e05.i == s) | (e05.j == s)); k = keep.values
    pooled = float((prec[k] * e05.D[k]).sum() / prec[k].sum()); pn = null.values[:, k] @ prec[k].values / prec[k].sum()
    rem = e05[keep]; lat = [(XY[a][0] + XY[b][0]) / 2 for a, b in zip(rem.i, rem.j)]
    rows.append(dict(station_omitted=s, pairs_removed=int((~keep).sum()), pairs_remaining=int(keep.sum()),
                     pooled_D=pooled, p_one_sided=(1 + (pn >= pooled).sum()) / (len(pn) + 1),
                     remaining_pairs_lat_range=f"{min(lat):.2f}-{max(lat):.2f} N",
                     remaining_pairs_north_of_57N=int(sum(l > 57.0 for l in lat))))
h2t = pd.DataFrame(rows); h2t.round(4).to_csv(RES / "x3_h2_station_contribution.csv", index=False)
runmeta.write(EXP, dict(experiment="E11 X3 station contribution (descriptive)", inputs="E04 h1_estimates.csv; E05 pair statistics and null"))
print(h1[["label", "estimate", "change_vs_primary", "ci_width_ratio_vs_primary"]].round(3).to_string(index=False)); print(h2t.round(3).to_string(index=False))
