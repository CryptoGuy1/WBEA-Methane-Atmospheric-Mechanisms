"""E12 command-line runner. Seeds follow EXPERIMENT_PLAN.md section 6. Appends one row per replicate to the CSV.
Examples:  python run_e12.py --scenario N0 --reps 500 --out results/raw_N0.csv
           python run_e12.py --scenario P1 --config P1_t021 --reps 200 --out results/raw_P1.csv"""
import argparse, json, pathlib, sys, time, numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from e12 import generator as G, fast_h2 as F
from e12.setup_network import COORDS, FAM, SEASON_BLOCKS, residual_input
from wbea import h2
BASE = 20261212
SCEN_INDEX = {"N0": 1, "N1a": 2, "N2a": 3, "N3": 4, "N2b": 5, "N1b": 6,
              "P1_t007": 7, "P1_t013": 8, "P1_ceiling": 9, "P1_L2": 12, "P1_L3": 13, "P1T_t013": 14, "P1T_ceiling": 15}

def run_one(name, rep, amp=0.0, lag=1, alternatives=True, seed=None):
    seed = BASE + 100000 * SCEN_INDEX.get(name, 0) + rep if seed is None else seed
    gen = "P1" if name.startswith("P1") else name; t0 = time.time()   # P1 and P1T share the generator; lag="transit" selects P1T
    d = G.generate(gen, seed, COORDS, pair_wind_fn=h2.pair_wind, pairs=FAM, amp=amp, lag=lag)
    r = F.evaluate(residual_input(d["ch4"]), d["winds"], G.STATIONS, FAM, SEASON_BLOCKS, run_alternatives=alternatives)
    r.pop("pair_D", None); r.update(scenario=name, rep=rep, seed=seed, amp=amp, lag=lag, runtime_s=round(time.time() - t0, 3))
    r["excluded_stations"] = ";".join(r.get("excluded_stations", [])); return r

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--scenario", required=True); ap.add_argument("--reps", type=int, required=True)
    ap.add_argument("--start", type=int, default=0); ap.add_argument("--out", required=True)
    ap.add_argument("--no-alternatives", action="store_true"); a = ap.parse_args()
    amp, lag = 0.0, 1
    if a.scenario.startswith("P1"):
        cfg = json.loads((HERE / "p1_amplitudes.json").read_text())["configs"][a.scenario]; amp, lag = cfg["amp"], cfg["lag"]
    out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    for rep in range(a.start, a.start + a.reps):
        row = run_one(a.scenario, rep, amp, lag, alternatives=not a.no_alternatives)
        pd.DataFrame([row]).to_csv(out, mode="a", header=not out.exists(), index=False)
