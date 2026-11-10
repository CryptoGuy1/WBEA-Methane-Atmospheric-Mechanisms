"""E04 review checkpoint (2026-11-10). Technical checks on the H1 estimate without modifying E04 results:
 1. Analytic cluster-robust (CR1) SE with 14-day clusters vs the block-bootstrap SE.
 2. Missing-data sensitivity (review correction 1): exclude hours ending 01-06 (the nightly Z window);
    restrict to hours with all 7 core stations valid (fixed response composition).
 3. Robust response: Huber-type downweighting check via median regression on cell-demeaned data (IRLS).
Outputs: results/review_*."""
import sys, pathlib, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(EXP.parents[1] / "src"))
from wbea.config import CFG
from wbea.io import load_dev
from wbea.wind import composite
from wbea import runmeta

RES = EXP / "results"; SEED = CFG["project"]["seed"] + 41; rng = np.random.default_rng(SEED)
P = load_dev(); ST = CFG["stations"]["usable"]; idx = P["AMS 1"].index
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); X = CH - CH.loc["2021":"2023"].median()
CORE = CFG["stations"]["h1_core_response"]; A5 = P["AMS 5"]
S0 = A5["AT90 (C)"] - A5["AT20 (C)"]; S = (S0 - S0.loc["2021":"2023"].mean()) / S0.loc["2021":"2023"].std()
LU = np.log(composite(A5).ws + 0.5); CELL = pd.Series(idx.year * 10000 + idx.month * 100 + idx.hour, index=idx)

def build(kmin=5, mask=None):
    y = X[CORE].median(1).where(X[CORE].notna().sum(1) >= kmin)
    d = pd.concat([y.rename("y"), S.rename("s"), LU.rename("lu"), CELL.rename("cell")], axis=1).dropna()
    return d if mask is None else d[mask.reindex(d.index).fillna(False).astype(bool)]

def demean(d):
    return d[["y", "s", "lu"]] - d.groupby("cell")[["y", "s", "lu"]].transform("mean")

def ols_cr1(d):
    Z = demean(d); Xm = Z[["s", "lu"]].values; y = Z.y.values
    XtX = np.linalg.inv(Xm.T @ Xm); b = XtX @ Xm.T @ y; e = y - Xm @ b
    cl = ((d.index - idx[0]).days // 14).to_numpy(); G = len(np.unique(cl))
    U = np.column_stack([np.bincount(cl, Xm[:, k] * e) for k in range(2)])
    V = XtX @ (U.T @ U) @ XtX * G / (G - 1) * (len(y) - 1) / (len(y) - 2 - d.cell.nunique())
    return b[0], np.sqrt(V[0, 0]), len(d), G

def boot_se(d, nb=1000):
    arr = d[["y", "s", "lu"]].values; c = pd.factorize(d.cell)[0]; bl = ((d.index - idx[0]).days // 14).to_numpy()
    ub, inv = np.unique(bl, return_inverse=True); pos = [np.where(inv == u)[0] for u in range(len(ub))]; out = []
    for _ in range(nb):
        ii = np.concatenate([pos[u] for u in rng.integers(0, len(ub), len(ub))]); cc = c[ii]; A = arr[ii]
        n = np.bincount(cc, minlength=c.max() + 1)
        m = np.vstack([np.bincount(cc, A[:, j], minlength=len(n)) for j in range(3)]).T / np.maximum(n, 1)[:, None]
        Zb = A - m[cc]; out.append(np.linalg.lstsq(Zb[:, 1:], Zb[:, 0], rcond=None)[0][0])
    out = np.array(out); return out.std(), np.percentile(out, [2.5, 97.5])

def lad(d, it=50):
    Z = demean(d); Xm = Z[["s", "lu"]].values; y = Z.y.values; b = np.linalg.lstsq(Xm, y, rcond=None)[0]
    for _ in range(it):
        w = 1 / np.maximum(np.abs(y - Xm @ b), 1e-4); b = np.linalg.solve(Xm.T @ (Xm * w[:, None]), Xm.T @ (w * y))
    return b[0]

rows = []
for lab, d in [("Primary (as E04)", build()),
               ("Exclude hours ending 01-06 (nightly Z window)", build(mask=pd.Series(~idx.hour.isin(range(1, 7)), index=idx))),
               ("All 7 core stations valid (fixed composition)", build(kmin=7))]:
    b, se, n, G = ols_cr1(d); bse, ci = boot_se(d)
    rows.append(dict(analysis=lab, n_hours=n, clusters=G, estimate=b, se_cluster_CR1=se,
                     ci_cluster_lo=b - 1.96 * se, ci_cluster_hi=b + 1.96 * se, se_block_bootstrap=bse,
                     ci_boot_lo=ci[0], ci_boot_hi=ci[1]))
rev = pd.DataFrame(rows)
rev.loc[len(rev)] = dict(analysis="Median (LAD, IRLS) on cell-demeaned data, primary sample", n_hours=rows[0]["n_hours"],
                         estimate=lad(build()))
rev.round(5).to_csv(RES / "review_h1_checks.csv", index=False)
runmeta.write(RES, dict(experiment="E04 review checkpoint", seed_used=SEED))
(RES / "run_metadata.json").rename(RES / "review_run_metadata.json")
print(rev.round(4).to_string(index=False))
