"""EXPLORATORY (post hoc, not part of any gate): why do observed lag centroids fall below the A = 3
simulated reference (E06 criterion 3(ii) failed)? Two candidate explanations:
 H-a  signal-to-noise: at realistic amplitude (A = 0.3, matching observed pooled D) the synchronous
      background correlation pulls simulated centroids down as well;
 H-b  effective transport is faster than the 10 m wind implies: simulate with transit tau / k for
      k in {1.0, 1.25, 1.5, 2.0} (wind speed in the transport layer k times the 10 m value).
Results are exploratory and must be confirmed independently before any claim."""
import sys, pathlib, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(EXP.parents[1] / "src"))
import importlib.util
spec = importlib.util.spec_from_file_location("e06", EXP / "run_e06.py")
src = (EXP / "run_e06.py").read_text().split("# ---------------- detectability")[0]   # setup and helpers only
g = {"__file__": str(EXP / "run_e06.py"), "__name__": "e06_setup"}; exec(compile(src, "run_e06_setup", "exec"), g)
from wbea import h2, runmeta
rng = np.random.default_rng(g["SEED"] + 100); g["rng"] = rng
setup, BINS, pooled_profile, inject = g["setup"], g["BINS"], g["pooled_profile"], g["inject"]
obs = pd.read_csv(EXP / "results" / "e06_observed_vs_reference_kernel.csv")

def centroids(A, mem, k, reps):
    out = []
    for rep in range(reps):
        items = {b: [] for b in range(len(BINS) - 1)}
        for s in setup:
            dri, drj = inject(s["Ri"], s["Rj"], s["al"], s["rv"], s["tau"] / k, A, mem, s["sd"])
            for b in range(len(BINS) - 1):          # bins remain defined on the 10 m-wind transit time
                items[b].append((dri, drj, s["al"] & (s["tau"] >= BINS[b]) & (s["tau"] < BINS[b + 1])))
        out.append([h2.centroid(pooled_profile(items[b])) for b in range(len(BINS) - 1)])
    return np.array(out)

rows = []
for A, mem, k, reps in [(0.3, 20, 1.0, 3), (0.3, 180, 1.0, 3), (3.0, 180, 1.25, 2), (3.0, 180, 1.5, 2), (3.0, 180, 2.0, 2),
                        (0.3, 180, 1.25, 2), (0.3, 180, 1.5, 2), (0.3, 180, 2.0, 2)]:
    c = centroids(A, mem, k, reps).mean(0)
    rows.append(dict(A=A, memory_min=mem, speed_factor_k=k, **{f"centroid_bin{b}": c[b] for b in range(5)},
                     sse_vs_observed=float(np.nansum((c - obs.centroid.values) ** 2))))
out = pd.DataFrame(rows); out.round(4).to_csv(EXP / "results" / "exploratory_kernel_diagnostic.csv", index=False)
runmeta.write(EXP / "results", dict(experiment="E06 exploratory kernel diagnostic (post hoc)", status="EXPLORATORY"))
(EXP / "results" / "run_metadata.json").rename(EXP / "results" / "exploratory_run_metadata.json")
print("observed", obs.centroid.round(3).tolist()); print(out.round(3).to_string(index=False))
