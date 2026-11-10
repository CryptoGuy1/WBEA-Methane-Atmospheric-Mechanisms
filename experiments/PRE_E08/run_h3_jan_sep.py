"""E07-r3 (D-54): H3 development benchmark on the common 1 Jan - 30 Sep window, registered E07 code path."""
import sys, pathlib, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent; ROOT = EXP.parents[1]; RES = EXP / "results"
sys.path.insert(0, str(ROOT / "src"))
from wbea.config import CFG
from wbea import runmeta
src = (ROOT / "experiments/E07_composition_decomposition/run_e07.py").read_text().split("# ---------------- primary")[0]
g = {"__file__": str(ROOT / "experiments/E07_composition_decomposition/run_e07.py"), "__name__": "e07_setup"}
exec(compile(src, "run_e07_setup", "exec"), g); g["rng"] = np.random.default_rng(CFG["project"]["seed"] + 72)
idx = g["idx"]; g["WIN"][:] = np.asarray((idx.month <= 9) | ((idx.month == 10) & (idx.day == 1) & (idx.hour == 0)))
E95 = g["CH"].gt(g["REF"].quantile(.95)).astype(float).where(g["CH"].notna())
H, Xn = g["counts"](E95); df, share, bs, G = g["analyse"](H, Xn, nb=1000)
out = pd.DataFrame([dict(version="E07-r3 (Jan-Sep, D-54)", share=share, ci_lo=np.percentile(bs, 2.5), ci_hi=np.percentile(bs, 97.5),
                         contrasts=len(df), median_effective_regimes=float(np.median([len(v) for v in G.values()]))),
                    dict(version="E07-r2 (Jan-Oct, D-47)", share=0.0193, ci_lo=-0.0351, ci_hi=0.1174, contrasts=120, median_effective_regimes=12.0),
                    dict(version="E07 original (Jan-Nov, D-40)", share=0.0269, ci_lo=-0.0396, ci_hi=0.1264, contrasts=120, median_effective_regimes=12.0)])
out.round(4).to_csv(RES / "h3_jan_sep_benchmark.csv", index=False); df.round(6).to_csv(RES / "h3_jan_sep_contrasts.csv", index=False)
runmeta.write(RES, dict(experiment="E07-r3 Jan-Sep H3 benchmark (D-54)", seed_used=CFG["project"]["seed"] + 72))
(RES / "run_metadata.json").rename(RES / "h3_jan_sep_run_metadata.json"); print(out.round(4).to_string(index=False))
