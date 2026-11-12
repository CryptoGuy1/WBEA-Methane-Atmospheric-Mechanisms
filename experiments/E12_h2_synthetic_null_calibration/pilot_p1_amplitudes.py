"""Pre-registered P1 amplitude pilot (EXPERIMENT_PLAN.md section 4): 12 amplitudes (0.005-0.30), 20 replicates each,
lag 1, primary statistic only; median pooled D; linear interpolation to target medians 0.07, 0.13, 0.21, 0.29, 0.40.
Uses only P1 pooled-D medians (no null rejection rates). Seeds 20261212 + 9,000,000 + 1000 g + r (outside production)."""
import json, pathlib, numpy as np, pandas as pd, run_e12 as R
HERE = pathlib.Path(__file__).resolve().parent
grid = np.round(np.geomspace(0.005, 0.30, 12), 4); rows = []
for g, a in enumerate(grid):
    for r in range(20):
        o = R.run_one("P1_pilot", r, amp=float(a), lag=1, alternatives=False, seed=R.BASE + 9_000_000 + 1000 * g + r)
        rows.append(dict(amp=a, rep=r, D=o["D_primary"]))
df = pd.DataFrame(rows); df.to_csv(HERE / "results" / "pilot_p1_amplitude_grid.csv", index=False)
med = df.groupby("amp").D.median(); print(med.round(4).to_string())
mono = np.maximum.accumulate(med.values)                                   # monotone envelope for interpolation
targets = {"P1_t007": 0.07, "P1_t013": 0.13, "P1_t021": 0.21, "P1_t029": 0.29, "P1_t040": 0.40}
cfg = {k: dict(target_median_D=t, amp=float(np.interp(t, mono, med.index.values)), lag=1) for k, t in targets.items()}
cfg["P1_L2"] = dict(target_median_D=None, amp=cfg["P1_t021"]["amp"], lag=2, note="amplitude of the 0.21 target, lag 2")
cfg["P1_L3"] = dict(target_median_D=None, amp=cfg["P1_t021"]["amp"], lag=3, note="amplitude of the 0.21 target, lag 3")
(HERE / "p1_amplitudes.json").write_text(json.dumps(dict(procedure="pre-registered pilot; see pilot_p1_amplitudes.py", grid=grid.tolist(),
                                                         median_D=med.round(5).tolist(), configs=cfg), indent=1))
print(json.dumps(cfg, indent=1))
