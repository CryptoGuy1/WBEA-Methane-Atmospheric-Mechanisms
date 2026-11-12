"""P1T amplitude pilot (DEVIATIONS D3), same rule as the pre-registered P1 pilot: same 12-amplitude grid, 20 replicates,
primary statistic only, median pooled D, monotone linear interpolation to targets 0.13, 0.21, 0.29, 0.40.
Seeds 20261212 + 9,500,000 + 1000 g + r (outside production). No null outputs inspected."""
import json, pathlib, numpy as np, pandas as pd, run_e12 as R
HERE = pathlib.Path(__file__).resolve().parent
grid = np.round(np.geomspace(0.005, 0.30, 12), 4); rows = []
for g, a in enumerate(grid):
    for r in range(20):
        o = R.run_one("P1T_pilot", r, amp=float(a), lag="transit", alternatives=False, seed=R.BASE + 9_500_000 + 1000 * g + r)
        rows.append(dict(amp=a, rep=r, D=o["D_primary"]))
df = pd.DataFrame(rows); df.to_csv(HERE / "results" / "pilot_p1t_amplitude_grid.csv", index=False)
g = df.groupby("amp").D; print(pd.DataFrame({"median": g.median(), "q10": g.quantile(.1), "q90": g.quantile(.9)}).round(4).to_string())
