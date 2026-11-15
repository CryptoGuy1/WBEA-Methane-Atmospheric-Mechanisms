"""E14 production: all 25 (methane year, wind year) combinations x 2 station sets, whole-period + C1/C2 references.
Deterministic (no random numbers). Writes results/replicates.csv, results/null_pooled_<set>.npz, results/run_log.json."""
import sys, json, time, platform, pathlib, subprocess, hashlib, numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import e14
from wbea.io import load_dev
OUT = HERE / "results"; OUT.mkdir(exist_ok=True)
t0 = time.time(); DEV = load_dev(); rows, nulls, fails = [], {}, []
for ss in ("coverage_rule", "confirmation_network"):
    for y in e14.YEARS:
        for yw in e14.YEARS:
            try:
                rec, pn = e14.run_one(DEV, y, yw, ss); rows.append(rec); nulls[f"{ss}|{y}|{yw}"] = pn
            except Exception as ex:                                   # never silently discard: record and continue
                fails.append(dict(station_set=ss, ch4_year=y, wind_year=yw, error=repr(ex)))
R = pd.DataFrame(rows); R.to_csv(OUT / "replicates.csv", index=False)
for ss in ("coverage_rule", "confirmation_network"):
    np.savez_compressed(OUT / f"null_pooled_{ss}.npz", **{k.split("|", 1)[1].replace("|", "_"): v for k, v in nulls.items() if k.startswith(ss)})
commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()
log = dict(commit=commit, python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__, platform=platform.platform(),
           runtime_s=round(time.time() - t0, 1), replicates_attempted=50, replicates_completed=len(rows), failures=fails,
           randomness="none (deterministic recombination of observed data)")
(OUT / "run_log.json").write_text(json.dumps(log, indent=1)); print(json.dumps({k: log[k] for k in ("runtime_s", "replicates_completed", "failures")}))
