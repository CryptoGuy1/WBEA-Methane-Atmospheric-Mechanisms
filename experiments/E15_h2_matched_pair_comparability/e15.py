"""E15 (Experiment A): matched-pair and temporal comparability of the H2 directional statistic. POST-CONFIRMATION EXPLORATORY.
The frozen statistic is reached through src/wbea (h2, e08), E12's parity-tested fast routines and the E13/E14 helpers, all
imported read-only. The only new construction is the pooled Jan-Sep development analysis (per-year sufficient statistics
summed over years; within-year joint circular shifts), declared exploratory in EXPERIMENT_PLAN.md."""
import sys, pathlib, numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
for p in (ROOT / "src", ROOT / "experiments/E12_h2_synthetic_null_calibration", ROOT / "experiments/E13_h2_seasonal_shift_sensitivity",
          ROOT / "experiments/E14_h2_empirical_yearswap_null"):
    sys.path.insert(0, str(p))
from wbea.config import CFG
from wbea.io import load_dev
from wbea.wind import composite
from wbea.geometry import pair_table
from wbea import h2, e08
from e12.fast_h2 import moment_matrix, D_from_sums, circ_sums
import e13, e14

ST12 = CFG["stations"]["usable"]; ST11 = [s for s in ST12 if s != "AMS 2"]
DEV_YEARS = [2021, 2022, 2023, 2024, 2025]
PANEL_2026 = ROOT / "sealed/e08_panel"                                  # read only here (named seal-test exemption, DEVIATIONS D1)
IDX26 = pd.date_range("2026-01-01 01:00", "2026-10-01 00:00", freq="h")

def ref_medians(DEV):
    return pd.DataFrame({s: DEV[s]["CH4 (ppm)"] for s in ST12}).loc["2021":"2023"].median()     # frozen reference (2021-2023)

def inputs(CH, W, universe, pairs, MED):
    """CH: DataFrame of CH4 (all 12 stations); W: dict of composite winds; universe: LPO station universe; pairs: pair ids kept."""
    FAM = pair_table(universe, CFG["h2"]["max_pair_km"]).reset_index(drop=True)
    FAM = FAM[(FAM.i + "->" + FAM.j).isin(pairs)].reset_index(drop=True)
    return dict(X=CH[universe] - MED[universe], W={s: W[s] for s in universe}, FAM=FAM, STU=universe)

def pair_raw(inp):
    """Per-pair inputs WITHOUT the eligibility filter (applied later on the analysis window as a whole)."""
    out = []
    for _, r in inp["FAM"].iterrows():
        Ri, Rj = h2.lpo_residual_levels(inp["X"], r.i, r.j, inp["STU"]); dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
        up, cs = h2.pair_wind(inp["W"][r.i], inp["W"][r.j], r.bearing); al, rv, tau = h2.sets(r.km, up, cs)
        ws = np.hypot((inp["W"][r.i].u + inp["W"][r.j].u).to_numpy() / 2, (inp["W"][r.i].v + inp["W"][r.j].v).to_numpy() / 2)
        out.append(dict(pair=f"{r.i}->{r.j}", km=r.km, dri=dri, drj=drj, al=al, rv=rv, tau=tau, ws=ws, M=moment_matrix(dri, drj)))
    return out

def analyse(windows, k_days, name):
    """windows: list of pair_raw outputs (one per contiguous window; same pair order). One window = the frozen procedure.
    Several windows = pooled construction: sums over windows, same within-window circular shift k for all windows and pairs."""
    sh = np.r_[0, k_days] * 24; rows, Dm = [], []
    for p in range(len(windows[0])):
        parts = [w[p] for w in windows]; nal = sum(int(q["al"].sum()) for q in parts); nrv = sum(int(q["rv"].sum()) for q in parts)
        if nal < 100 or nrv < 100: continue                                              # frozen eligibility rule
        wts = h2.weights(np.concatenate([q["tau"] for q in parts]), np.concatenate([q["al"] for q in parts]), np.concatenate([q["rv"] for q in parts]))
        Sal = sum(circ_sums(q["M"], q["al"], sh) for q in parts); Srv = sum(circ_sums(q["M"], q["rv"], sh) for q in parts)
        d = D_from_sums(Sal, Srv, wts); Dm.append(d)
        rows.append(dict(pair=parts[0]["pair"], km=parts[0]["km"], n_aligned=nal, n_reversed=nrv, D=d[0], null_mean=d[1:].mean(), null_sd=d[1:].std()))
    if not rows: return None, pd.DataFrame(), None                                    # no eligible pair: reported, never silently dropped
    Dm = np.array(Dm).T
    summ, pn, w = e13.summarise(name, Dm)
    P = pd.DataFrame(rows); P["weight"] = w; P["contribution"] = w * P.D
    summ.update(eff_pairs=float(1 / np.sum(w ** 2)), pooled_null_sd=float(pn.std()))
    return summ, P, pn

def dev_full(DEV):
    return {s: DEV[s] for s in ST12}

def load_2026():
    pan = {}
    for f in sorted(PANEL_2026.glob("AMS*.parquet")):
        d = pd.read_parquet(f); pan[d.station.iloc[0]] = d.set_index("time_mst_hour_ending").reindex(IDX26)
    return pan

def dev_year_raw(DEV, year, universe, pairs, MED):
    """Jan-Sep window of one development year (E14 calendar window: hours ending 1 Jan 01:00 .. 1 Oct 00:00; 29 Feb removed)."""
    CH = pd.DataFrame({s: e14.window(DEV[s][["CH4 (ppm)"]], year)["CH4 (ppm)"] for s in ST12})
    W = {s: e14.window(composite(DEV[s]), year) for s in ST12}
    return pair_raw(inputs(CH, W, universe, pairs, MED)), CH

def raw_2026(PAN, universe, pairs, MED):
    CH = pd.DataFrame({s: PAN[s]["CH4 (ppm)"] for s in ST12}); W = {s: composite(PAN[s]) for s in ST12}
    return pair_raw(inputs(CH, W, universe, pairs, MED)), CH

def pool_fixed(D, weights):
    """Descriptive pooled D with externally fixed weights (normalised): sum(w D) / sum(w). Not a test."""
    w = np.asarray(weights, float); return float(np.sum(w * np.asarray(D, float)) / w.sum())
