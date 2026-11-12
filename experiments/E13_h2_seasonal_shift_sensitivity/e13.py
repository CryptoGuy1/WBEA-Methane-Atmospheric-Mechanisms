"""E13 post-confirmation exploratory seasonal-shift sensitivity (EXPERIMENT_PLAN.md). Uses frozen H2 functions
(src/wbea) and E12's parity-tested fast routines (imported read-only; E12 files are not modified)."""
import sys, pathlib, numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "experiments/E12_h2_synthetic_null_calibration"))
from wbea.config import CFG
from wbea.io import load_dev
from wbea.wind import composite
from wbea.geometry import pair_table
from wbea import h2, e08
from e12.fast_h2 import moment_matrix, D_from_sums, circ_sums

START, END = pd.Timestamp("2026-01-01 01:00"), pd.Timestamp("2026-10-01 00:00")
IDX = pd.date_range(START, END, freq="h"); N = len(IDX)
C1 = [(0, 2160), (2160, 4344), (4344, 6552)]          # Jan-Mar 90 d, Apr-Jun 91 d, Jul-Sep 92 d
C2 = [(0, 2880), (2880, 6552)]                        # Jan-Apr 120 d, May-Sep 153 d
C1_K = np.arange(14, 77); C2_K = np.arange(14, 107)

def roll_within_blocks(x, blocks, k_days):
    """Reference implementation of the joint within-season circular shift (used in tests)."""
    out = np.array(x, copy=True)
    for a, b in blocks: out[a:b] = np.roll(x[a:b], 24 * k_days)
    return out

def load_inputs(panel_dir=ROOT / "sealed/e08_panel"):
    ST = CFG["stations"]["usable"]; DEV = load_dev()
    MED = pd.DataFrame({s: DEV[s]["CH4 (ppm)"] for s in ST}).loc["2021":"2023"].median()
    PAN = {d.station.iloc[0]: d.set_index("time_mst_hour_ending") for d in (pd.read_parquet(f) for f in pathlib.Path(panel_dir).glob("AMS*.parquet"))}
    P = {s: PAN[s].reindex(IDX) for s in ST}; CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST})
    cov = CH.notna().mean(); STU = [s for s in ST if cov[s] >= 0.5]; X = CH[STU] - MED[STU]
    W = {s: composite(P[s]) for s in STU}; FAM = pair_table(STU, CFG["h2"]["max_pair_km"]).reset_index(drop=True)
    return dict(X=X, W=W, FAM=FAM, STU=STU, excluded=[s for s in ST if s not in STU], coverage=cov)

def pair_data(inp, sl=slice(None)):
    """Per-pair inputs on the whole window (sl = all) or within a season slice (residual levels sliced, then differenced)."""
    out = []
    for _, r in inp["FAM"].iterrows():
        Ri, Rj = h2.lpo_residual_levels(inp["X"], r.i, r.j, inp["STU"]); Ri, Rj = Ri[sl], Rj[sl]
        dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
        up, cs = h2.pair_wind(inp["W"][r.i], inp["W"][r.j], r.bearing); up, cs = up[sl], cs[sl]
        al, rv, tau = h2.sets(r.km, up, cs)
        if al.sum() < 100 or rv.sum() < 100: continue
        out.append(dict(pair=f"{r.i}->{r.j}", dri=dri, drj=drj, al=al, rv=rv, tau=tau, w=h2.weights(tau, al, rv), M=moment_matrix(dri, drj)))
    return out

def D_whole(pd_list, k_days):
    sh = np.r_[0, k_days] * 24
    return np.array([D_from_sums(circ_sums(p["M"], p["al"], sh), circ_sums(p["M"], p["rv"], sh), p["w"]) for p in pd_list]).T

def D_blocks(pd_list, blocks, k_days):
    sh = np.r_[0, k_days] * 24; out = []
    for p in pd_list:
        sal = sum(circ_sums(p["M"][a:b], p["al"][a:b], sh) for a, b in blocks); srv = sum(circ_sums(p["M"][a:b], p["rv"][a:b], sh) for a, b in blocks)
        out.append(D_from_sums(sal, srv, p["w"]))
    return np.array(out).T                                           # (1 + K, pairs); row 0 = observed

def summarise(name, Dmat, weights=None):
    obs, null = Dmat[0], Dmat[1:]
    if weights is None: pooled, pn, w = e08.pooled_inverse_null_variance(obs, null)
    else: w = np.asarray(weights) / np.sum(weights); pooled, pn = float((w * obs).sum()), null @ w
    return dict(configuration=name, pairs=len(obs), K=null.shape[0], p_floor=1 / (null.shape[0] + 1), pooled_D=pooled,
                p=e08.finite_shift_p(pooled, pn), n_surrogates_ge_obs=int((pn >= pooled).sum()), null_mean=float(pn.mean()),
                null_sd=float(pn.std()), null_q05=float(np.quantile(pn, .05)), null_q50=float(np.median(pn)), null_q95=float(np.quantile(pn, .95)),
                null_q99=float(np.quantile(pn, .99)), null_max=float(pn.max()), z=float((pooled - pn.mean()) / pn.std())), pn, w
