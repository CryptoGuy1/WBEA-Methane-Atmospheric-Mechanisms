"""POST-CONFIRMATION EXPLORATORY (v1, 2026-11-10; authorised item C). Does a change in the covariance between
contemporaneous and next-day stability help explain the negative 2026 next-day coefficient? Uses the frozen E08
estimator (wbea.e08.h1_estimate) and frozen references, per Jan-Sep window. Does NOT modify the registered H1
interpretation, inference or confirmation result."""
import sys, pathlib, json, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "src")); OUT = pathlib.Path(__file__).resolve().parent / "results"
from wbea.config import CFG
from wbea.io import load_dev
from wbea.wind import composite
from wbea import e08
DEV = load_dev(); ST = CFG["stations"]["usable"]
CORE = [s for s in CFG["stations"]["h1_core_response"] if s != "AMS 2"]          # same 6-station core as the 2026 run
REF = pd.DataFrame({s: DEV[s]["CH4 (ppm)"] for s in ST}).loc["2021":"2023"]; MED = REF.median()
S_REF = (DEV["AMS 5"]["AT90 (C)"] - DEV["AMS 5"]["AT20 (C)"]).loc["2021":"2023"]; MU, SD = S_REF.mean(), S_REF.std()
CONF = {d.station.iloc[0]: d.set_index("time_mst_hour_ending") for d in (pd.read_parquet(f) for f in (ROOT / "sealed/e08_panel").glob("AMS*.parquet"))}

def window(src, y):
    idx = pd.date_range(f"{y}-01-01 01:00", f"{y}-10-01 00:00", freq="h"); P = {s: src[s].reindex(idx) for s in ST}
    X = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}) - MED
    Y = X[CORE].median(1).where(X[CORE].notna().sum(1) >= 5)
    Sz = ((P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"]) - MU) / SD; LU = np.log(composite(P["AMS 5"]).ws + 0.5)
    return idx, Y, Sz, LU

def within(v, idx):
    cell = (idx.year * 10000 + idx.month * 100 + idx.hour); s = pd.Series(v, index=idx)
    return s - s.groupby(cell).transform("mean")

rows = []
for y in [2021, 2022, 2023, 2024, 2025, 2026]:
    idx, Y, Sz, LU = window(CONF if y == 2026 else DEV, y); Sn = Sz.shift(-24)
    ok = Y.notna() & Sz.notna() & Sn.notna() & LU.notna()
    wS, wN, wL, wY = (within(v.where(ok), idx) for v in (Sz, Sn, LU, Y))
    h = e08.h1_estimate(Y.to_numpy(), Sz.to_numpy(), Sn.to_numpy(), LU.to_numpy(), idx, 300, np.random.default_rng(20261190 + 900 + y))
    rows.append(dict(period=f"{y} Jan-Sep", source="confirmation (2026)" if y == 2026 else "development", n_joint=h["n_joint"],
                     corr_S_Snext_raw=float(Sz[ok].corr(Sn[ok])), corr_S_Snext_within_cell=float(wS.corr(wN)),
                     corr_Snext_logU_within_cell=float(wN.corr(wL)), corr_Y_Snext_within_cell=float(wY.corr(wN)),
                     sd_S_within=float(wS.std()), sd_Snext_within=float(wN.std()),
                     b1_primary=h["b1_primary"], b1_joint=h["b1_joint"], b_nc=h["b_nc"], b_nc_ci_lo=h["b_nc_ci"][0], b_nc_ci_hi=h["b_nc_ci"][1],
                     ratio_nc=h["ratio_nc"]))
r = pd.DataFrame(rows); r.round(4).to_csv(OUT / "h1_nc_covariance_by_period.csv", index=False)
dev = r[r.source == "development"]
summary = dict(label="POST-CONFIRMATION EXPLORATORY; registered H1 result unchanged",
               dev_b_nc_range=[float(dev.b_nc.min()), float(dev.b_nc.max())],
               dev_corr_within_range=[float(dev.corr_S_Snext_within_cell.min()), float(dev.corr_S_Snext_within_cell.max())],
               conf_b_nc=float(r.b_nc.iloc[-1]), conf_corr_within=float(r.corr_S_Snext_within_cell.iloc[-1]),
               spearman_bnc_vs_corrwithin_6_periods=float(r[["b_nc", "corr_S_Snext_within_cell"]].corr("spearman").iloc[0, 1]))
(OUT / "h1_nc_covariance_summary.json").write_text(json.dumps(summary, indent=1)); print(r.round(3).to_string(index=False)); print(json.dumps(summary, indent=1))
