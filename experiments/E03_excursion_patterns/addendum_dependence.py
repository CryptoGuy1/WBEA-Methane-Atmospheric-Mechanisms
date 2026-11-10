"""E03 addendum (review correction 2, 2026-11-10): uncertainty for the co-occurrence-distance relation
that respects (a) temporal autocorrelation and common weather, via a joint 14-day block bootstrap that
recomputes all 66 month-x-hour-conditional lifts from the same block draws; (b) dependence among pairs
sharing stations, via a Mantel-type permutation of station labels and leave-one-station-out ranges.
Original E03 results are not modified; outputs go to results/addendum_*."""
import sys, pathlib, itertools, numpy as np, pandas as pd
from scipy.stats import spearmanr, rankdata
EXP = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(EXP.parents[1] / "src"))
from wbea.config import CFG
from wbea.io import load_dev
from wbea.geometry import stations, haversine_km
from wbea import runmeta

RES = EXP / "results"; SEED = CFG["project"]["seed"] + 31; rng = np.random.default_rng(SEED)
P = load_dev(); ST = CFG["stations"]["usable"]; idx = P["AMS 1"].index
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); ref = CH.loc["2021":"2023"]
E = CH.gt(ref.quantile(.95)).astype(float).where(CH.notna())
blk = ((idx - idx[0]).days // CFG["bootstrap"]["block_days"]).to_numpy(); nb = blk.max() + 1
cell = ((idx.month - 1) * 24 + idx.hour).to_numpy(); nc = 288
XY = stations(); pairs = list(itertools.combinations(ST, 2))
km = np.array([haversine_km(XY[a], XY[b]) for a, b in pairs])

# sufficient statistics per (block, cell) for each pair: n, sum Ei, sum Ej, sum EiEj
A = np.zeros((nb, len(pairs), nc, 4))
for p, (a, b) in enumerate(pairs):
    ea, eb = E[a].to_numpy(), E[b].to_numpy(); ok = np.isfinite(ea) & np.isfinite(eb)
    key = blk[ok] * nc + cell[ok]
    for k, v in enumerate((np.ones(ok.sum()), ea[ok], eb[ok], ea[ok] * eb[ok])):
        A[:, p, :, k] = np.bincount(key, v, minlength=nb * nc).reshape(nb, nc)

def lifts(T):                                   # T: (pairs, cells, 4) totals
    n, sa, sb, sab = np.moveaxis(T, -1, 0)
    with np.errstate(invalid="ignore", divide="ignore"):
        exp_joint = np.nansum(np.where(n > 0, sa * sb / n, 0), 1); obs = sab.sum(1)
    return obs / exp_joint

L0 = lifts(A.sum(0)); rho0 = spearmanr(km, L0)[0]
flat = A.reshape(nb, -1); NBOOT = 2000; rhos = np.empty(NBOOT); Lb = np.empty((NBOOT, len(pairs)))
for b in range(NBOOT):
    w = np.bincount(rng.integers(0, nb, nb), minlength=nb).astype(float)
    Lb[b] = lifts((w @ flat).reshape(len(pairs), nc, 4)); rhos[b] = spearmanr(km, Lb[b])[0]

# Mantel-type permutation: permute station labels in the distance matrix, keep lifts fixed
Dm = np.zeros((12, 12)); Lm = np.zeros((12, 12)); si = {s: k for k, s in enumerate(ST)}
for p, (a, b) in enumerate(pairs):
    Dm[si[a], si[b]] = Dm[si[b], si[a]] = km[p]; Lm[si[a], si[b]] = Lm[si[b], si[a]] = L0[p]
iu = np.triu_indices(12, 1); rl = rankdata(Lm[iu]); NP = 9999; cnt = 0
for _ in range(NP):
    pm = rng.permutation(12); r = np.corrcoef(rankdata(Dm[np.ix_(pm, pm)][iu]), rl)[0, 1]
    cnt += r <= rho0
p_mantel = (cnt + 1) / (NP + 1)

loso = []
for s in ST:
    keep = np.array([s not in pr for pr in pairs])
    loso.append(dict(station_dropped=s, n_pairs=int(keep.sum()), spearman=spearmanr(km[keep], L0[keep])[0]))
loso = pd.DataFrame(loso)

core = set(CFG["stations"]["h1_core_response"]) | {"AMS 5", "AMS 9", "AMS 30"}
within = np.array([a in core and b in core for a, b in pairs])
out = pd.DataFrame([
    dict(quantity="Spearman(lift | month x hour, distance), 66 pairs", estimate=rho0,
         ci_lo=np.percentile(rhos, 2.5), ci_hi=np.percentile(rhos, 97.5), note="joint 14-day block bootstrap, 2,000"),
    dict(quantity="Mantel permutation p (one-sided, negative association)", estimate=p_mantel, ci_lo=np.nan, ci_hi=np.nan,
         note="9,999 permutations of station labels"),
    dict(quantity="Leave-one-station-out Spearman, min..max", estimate=np.nan, ci_lo=loso.spearman.min(), ci_hi=loso.spearman.max(), note="12 refits"),
    dict(quantity="Spearman within the 10-station oil-sands core only", estimate=spearmanr(km[within], L0[within])[0],
         ci_lo=np.percentile([spearmanr(km[within], x[within])[0] for x in Lb], 2.5),
         ci_hi=np.percentile([spearmanr(km[within], x[within])[0] for x in Lb], 97.5), note=f"{within.sum()} pairs, excludes AMS 14/18")])
out.round(4).to_csv(RES / "addendum_distance_dependence_uncertainty.csv", index=False)
loso.round(4).to_csv(RES / "addendum_leave_one_station_out.csv", index=False)
pd.DataFrame({"pair": [f"{a}-{b}" for a, b in pairs], "km": km, "lift_given_month_hour": L0,
              "ci_lo": np.percentile(Lb, 2.5, 0), "ci_hi": np.percentile(Lb, 97.5, 0)}).round(4) \
  .to_csv(RES / "addendum_pair_lift_block_bootstrap.csv", index=False)
runmeta.write(EXP / "results", dict(experiment="E03 addendum (review correction 2)", seed_used=SEED))
(EXP / "results" / "run_metadata.json").rename(EXP / "results" / "addendum_run_metadata.json")
print(out.round(4).to_string(index=False)); print(loso.round(3).to_string(index=False))
