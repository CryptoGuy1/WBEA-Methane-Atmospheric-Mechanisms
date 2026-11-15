"""E14 (Experiment B): empirical year-swapped null for the frozen H2 shifted-wind test. POST-CONFIRMATION EXPLORATORY.
Development data only. The H2 statistic is the frozen one, reached through the E13 helpers (pair_data, D_whole, D_blocks,
summarise), which use src/wbea/h2.py, src/wbea/e08.py and E12's parity-tested fast routines. All are imported read-only."""
import sys, pathlib, numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
for p in (ROOT / "src", ROOT / "experiments/E12_h2_synthetic_null_calibration", ROOT / "experiments/E13_h2_seasonal_shift_sensitivity"):
    sys.path.insert(0, str(p))
from wbea.config import CFG
from wbea.io import load_dev
from wbea.wind import composite
from wbea.geometry import pair_table
import e13                                                            # frozen-statistic helpers (read-only)

YEARS = [2021, 2022, 2023, 2024, 2025]
N_HOURS = 6552                                                        # 273 days, matching the confirmation window
TEMPLATE = pd.date_range("2023-01-01 01:00", periods=N_HOURS, freq="h")   # neutral non-leap labels (calendar date and hour only)
K_WHOLE = np.arange(14, 260)                                          # all admissible whole-day shifts for 273 days (K = 246)
CONF_EXCLUDED = ["AMS 2"]                                             # 2026 coverage-rule exclusion (cited, not recomputed)

def window(df, year):
    """Hours ending 1 Jan {year} 01:00 .. 1 Oct {year} 00:00; in 2024 the 24 hours of 29 Feb are dropped (hour-ending: the hour
    belongs to the date of (timestamp - 1 h)). Returns exactly 6,552 rows relabelled onto TEMPLATE."""
    w = df.loc[pd.Timestamp(f"{year}-01-01 01:00"):pd.Timestamp(f"{year}-10-01 00:00")]
    d = (w.index - pd.Timedelta(hours=1))
    w = w[~((d.month == 2) & (d.day == 29))]
    assert len(w) == N_HOURS, (year, len(w))
    out = w.copy(); out.index = TEMPLATE; return out

def build_inputs(DEV, ch4_year, wind_year, station_set="coverage_rule"):
    ST = CFG["stations"]["usable"]
    MED = pd.DataFrame({s: DEV[s]["CH4 (ppm)"] for s in ST}).loc["2021":"2023"].median()     # frozen reference medians
    CH = pd.DataFrame({s: window(DEV[s][["CH4 (ppm)"]], ch4_year)["CH4 (ppm)"] for s in ST})
    cov = CH.notna().mean()
    if station_set == "coverage_rule": STU = [s for s in ST if cov[s] >= 0.5]                 # frozen rule on the methane window
    elif station_set == "confirmation_network": STU = [s for s in ST if s not in CONF_EXCLUDED and cov[s] >= 0.5]
    else: raise ValueError(station_set)
    W = {s: window(composite(DEV[s]), wind_year) for s in STU}
    FAM = pair_table(STU, CFG["h2"]["max_pair_km"]).reset_index(drop=True)
    return dict(X=CH[STU] - MED[STU], W=W, FAM=FAM, STU=STU, excluded=[s for s in ST if s not in STU], coverage=cov)

def run_one(DEV, ch4_year, wind_year, station_set="coverage_rule", seasonal=True):
    inp = build_inputs(DEV, ch4_year, wind_year, station_set)
    pdl = e13.pair_data(inp)
    whole, pn, w = e13.summarise("whole-period", e13.D_whole(pdl, K_WHOLE))
    rec = dict(ch4_year=ch4_year, wind_year=wind_year, kind="same-year anchor" if ch4_year == wind_year else "swap",
               station_set=station_set, n_stations=len(inp["STU"]), excluded=";".join(inp["excluded"]), pairs=whole["pairs"],
               pairs_dropped=len(inp["FAM"]) - whole["pairs"], K=whole["K"], D=whole["pooled_D"], p=whole["p"],
               n_ge=whole["n_surrogates_ge_obs"], null_mean=whole["null_mean"], null_sd=whole["null_sd"], null_max=whole["null_max"], z=whole["z"])
    if seasonal:
        for tag, blocks, ks in (("C1", e13.C1, e13.C1_K), ("C2", e13.C2, e13.C2_K)):
            s, _, _ = e13.summarise(tag, e13.D_blocks(pdl, blocks, ks))
            rec.update({f"{tag}_D": s["pooled_D"], f"{tag}_p": s["p"], f"{tag}_K": s["K"], f"{tag}_n_ge": s["n_surrogates_ge_obs"]})
    return rec, pn
