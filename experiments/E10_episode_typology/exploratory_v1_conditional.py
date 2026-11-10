"""EXPLORATORY, post hoc (not part of any decision): is V1's failure driven by eligibility? Compares, under real
and wind-shifted wind, (a) the share of episodes with an assessable upstream pair and (b) the lead rate
P(L = 1 | lead assessable). Uses the same 200 shifts and seed as E10."""
import sys, pathlib, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent
src = (EXP / "run_e10.py").read_text().split("# ---------------- primary classification")[0]
g = {"__file__": str(EXP / "run_e10.py"), "__name__": "e10_setup"}; exec(compile(src, "run_e10_setup", "exec"), g)
from wbea import runmeta
ep, _ = g["episodes"](95); N = g["N"]; rng = np.random.default_rng(g["SEED"]); ndays = N // 24
shifts = rng.choice(np.arange(14, ndays - 14), g["NPLAC"], replace=False) * 24
def rates(shift):
    L, AS = g["lead_arrays"](int(shift)); l = np.array([L[s][t] for s, t in zip(ep.station, ep.t)]); a = np.array([AS[s][t] for s, t in zip(ep.station, ep.t)])
    return a.mean(), l[a].mean() if a.any() else np.nan
real = rates(0); pl = np.array([rates(sh) for sh in shifts])
out = pd.DataFrame([dict(quantity="share of episodes with an assessable upstream pair", real=real[0], placebo_mean=pl[:, 0].mean(),
                         placebo_p5=np.percentile(pl[:, 0], 5), placebo_p95=np.percentile(pl[:, 0], 95)),
                    dict(quantity="P(upstream lead | assessable)", real=real[1], placebo_mean=np.nanmean(pl[:, 1]),
                         placebo_p5=np.nanpercentile(pl[:, 1], 5), placebo_p95=np.nanpercentile(pl[:, 1], 95))])
out.round(4).to_csv(EXP / "results" / "exploratory_v1_conditional.csv", index=False)
runmeta.write(EXP / "results", dict(experiment="E10 exploratory V1 conditional (post hoc)")); (EXP / "results" / "run_metadata.json").rename(EXP / "results" / "exploratory_run_metadata.json")
print(out.round(4).to_string(index=False))
