"""E04 - H1: association between near-surface stability and the regional CH4 level, net of
year x month x hour cycles (specification D-21, D-22; baselines D-23). Development data; exploratory.
Estimand: b1 = change in the network-median CH4 anomaly (ppm) per 1 SD of AMS 5 T90 - T20 within
year x month x hour cells; total (no wind term) and direct (with log wind)."""
import sys, pathlib, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(EXP.parents[1] / "src"))
from wbea.config import CFG
from wbea.io import load_dev, load_era5, load_fire_days
from wbea.wind import composite
from wbea import runmeta
from wbea.plotstyle import plt, save

RES = EXP / "results"; FIG = EXP / "figures"; RES.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
SEED = CFG["project"]["seed"] + 4; rng = np.random.default_rng(SEED); NB = CFG["bootstrap"]["n_boot"]
P = load_dev(); ST = CFG["stations"]["usable"]; idx = P["AMS 1"].index
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST})
REF = slice(str(CFG["split"]["reference_years"][0]), str(CFG["split"]["reference_years"][-1]))
X = CH - CH.loc[REF].median()
CORE, KMIN = CFG["stations"]["h1_core_response"], CFG["stations"]["h1_core_kmin"]
A5 = P["AMS 5"]

def z(s):
    return (s - s.loc[REF].mean()) / s.loc[REF].std()

S = z(A5["AT90 (C)"] - A5["AT20 (C)"]); LU = np.log(composite(A5).ws + 0.5)
CELL = pd.Series(idx.year * 10000 + idx.month * 100 + idx.hour, index=idx)

def response(stations=CORE, kmin=KMIN, data=X):
    return data[stations].median(axis=1).where(data[stations].notna().sum(1) >= kmin)

def design(y, xs, mask=None):
    d = pd.concat([y.rename("y")] + [x.rename(f"x{k}") for k, x in enumerate(xs)] + [CELL.rename("cell")], axis=1).dropna()
    if mask is not None:
        d = d[mask.reindex(d.index).fillna(False).astype(bool)]
    return d

def fit(d):
    """OLS of y on x* after absorbing cell means (FWL). Returns coefficient vector."""
    cols = [c for c in d.columns if c.startswith("x")]
    g = d.groupby("cell")[["y"] + cols].transform("mean")
    Z = d[["y"] + cols].values - g.values
    return np.linalg.lstsq(Z[:, 1:], Z[:, 0], rcond=None)[0]

def boot(d, block_days=CFG["bootstrap"]["block_days"], nb=NB, k=0):
    """Non-overlapping block bootstrap; cells re-absorbed in each replicate."""
    cols = [c for c in d.columns if c.startswith("x")]; arr = d[["y"] + cols].values
    cell = pd.factorize(d.cell)[0]; blk = ((d.index - idx[0]).days // block_days).to_numpy()
    ub, inv = np.unique(blk, return_inverse=True); pos = [np.where(inv == u)[0] for u in range(len(ub))]
    out = np.empty(nb)
    for b in range(nb):
        ii = np.concatenate([pos[u] for u in rng.integers(0, len(ub), len(ub))])
        c = cell[ii]; A = arr[ii]; n = np.bincount(c, minlength=cell.max() + 1)
        m = np.vstack([np.bincount(c, A[:, j], minlength=len(n)) for j in range(A.shape[1])]).T / np.maximum(n, 1)[:, None]
        Zb = A - m[c]; out[b] = np.linalg.lstsq(Zb[:, 1:], Zb[:, 0], rcond=None)[0][k]
    return out

rows = []
def record(label, group, d, k=0, nb=NB, block_days=CFG["bootstrap"]["block_days"]):
    est = fit(d)[k]; bs = boot(d, block_days, nb, k)
    rows.append(dict(group=group, label=label, n_hours=len(d), n_cells=d.cell.nunique(), estimate=est,
                     se_boot=bs.std(), ci_lo=np.percentile(bs, 2.5), ci_hi=np.percentile(bs, 97.5)))
    return est, bs

Y = response()
# ---------------- primary estimands
d_tot = design(Y, [S]); d_dir = design(Y, [S, LU])
b_tot, _ = record("Total (no wind term)", "primary", d_tot)
b_dir, bs_dir = record("Direct (with log wind)", "primary", d_dir)
for bd in CFG["bootstrap"]["sensitivity_block_days"]:
    record(f"Direct, {bd}-day blocks", "uncertainty", d_dir, block_days=bd, nb=1000)
# ---------------- replication across years and seasons
for yr in range(2021, 2026):
    record(f"Direct, {yr}", "year", d_dir[d_dir.index.year == yr], nb=1000)
for name, mos in [("DJF", [12, 1, 2]), ("MAM", [3, 4, 5]), ("JJA", [6, 7, 8]), ("SON", [9, 10, 11])]:
    record(f"Direct, {name}", "season", d_dir[d_dir.index.month.isin(mos)], nb=1000)
# ---------------- response definition
for s in CORE:
    record(f"Direct, response without {s}", "response", design(response([c for c in CORE if c != s], KMIN - 1), [S, LU]), nb=500)
record("Direct, expanded 11-station response (Kmin 8)", "response",
       design(response(CFG["stations"]["h1_expanded_response"], 8), [S, LU]), nb=1000)
aft = CH[CH.index.hour.isin(range(12, 18))].stack(); B = aft.groupby(aft.index.get_level_values(0).normalize()).quantile(0.10)
XB = CH.sub(B.reindex(idx.normalize()).values, axis=0)
record("Direct, background-subtracted response (C - B_t)", "response", design(response(data=XB), [S, LU]), nb=1000)
mon = CH.notna().groupby(idx.to_period("M")).transform("mean"); Xm = X.where(mon >= 0.75)
record("Direct, station-months < 75% removed", "response", design(response(data=Xm), [S, LU]), nb=1000)
fire = load_fire_days(); pm = pd.DataFrame({s: P[s]["PM2.5 (ug/m3)"] for s in ST if "PM2.5 (ug/m3)" in P[s]}).median(1)
smoke = pd.Series(idx.normalize().isin(fire), index=idx) | (pm > CFG["smoke"]["pm25_network_median_ugm3"])
record("Direct, smoke hours excluded", "response", design(Y, [S, LU], mask=~smoke), nb=1000)
# ---------------- alternative stability proxies (each standardised)
for lev in ("45", "75"):
    record(f"Proxy AMS 5 T{lev} - T20", "proxy", design(Y, [z(A5[f"AT{lev} (C)"] - A5["AT20 (C)"]), LU]), nb=1000)
record("Proxy AMS 1 T10 - T2 (response without AMS 1)", "proxy",
       design(response([c for c in CORE if c != "AMS 1"], KMIN - 1), [z(P["AMS 1"]["AT_Delta (C)"]), np.log(composite(P["AMS 1"]).ws + 0.5)]), nb=1000)
era = load_era5()["AMS 5"].reindex(idx)
record("Proxy ERA5 -log(BLH), AMS 5 cell", "proxy", design(Y, [z(-np.log(era.blh)), LU]), nb=1000)
# ---------------- negative-control exposure: next-day stability given today's
nc = design(Y, [S, S.shift(-24), LU])
b_nc_s, _ = record("Negative control: coefficient on S(t+24), given S(t)", "negative control", nc, k=1)
record("Coefficient on S(t) in the negative-control model", "negative control", nc, k=0)
res = pd.DataFrame(rows); res.round(5).to_csv(RES / "h1_estimates.csv", index=False)

# ---------------- functional form: piecewise-linear spline in S (cell- and wind-adjusted)
kn = d_dir.x0.quantile([.1, .3, .5, .7, .9]).values
def basis(s): return np.column_stack([s] + [np.maximum(s - k, 0) for k in kn])
dd = d_dir.copy(); Bm = basis(dd.x0.values)
for j in range(Bm.shape[1]): dd[f"x{j + 10}"] = Bm[:, j]
dd = dd.drop(columns=["x0"]); coef = fit(dd)               # x1 = log wind, x10.. = spline basis
grid = np.linspace(d_dir.x0.quantile(.01), d_dir.x0.quantile(.99), 60)
curve = basis(grid) @ coef[1:]; curve -= np.interp(0, grid, curve)
pd.DataFrame({"S_sd": grid, "spline_effect_ppm": curve, "linear_effect_ppm": b_dir * grid}).round(5).to_csv(RES / "h1_functional_form.csv", index=False)

# ---------------- baselines: climatology-only R2 and partial R2 of S; RF meteorological normalisation
yv = d_dir.y; cm = d_dir.groupby("cell").y.transform("mean")
ry = yv - cm; rs = d_dir.x0 - d_dir.groupby("cell").x0.transform("mean"); rl = d_dir.x1 - d_dir.groupby("cell").x1.transform("mean")
rl_y = ry - np.polyval(np.polyfit(rl, ry, 1), rl); rl_s = rs - np.polyval(np.polyfit(rl, rs, 1), rl)
partial_r2 = np.corrcoef(rl_y, rl_s)[0, 1] ** 2
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import partial_dependence
wd5 = composite(A5).wd
F = pd.DataFrame({"S": S, "logU": LU, "wd_sin": np.sin(np.deg2rad(wd5)), "wd_cos": np.cos(np.deg2rad(wd5)),
                  "AT2": A5["AT2 (C)"], "RH2": P["AMS 5"]["RH2 (%)"], "hour": idx.hour, "doy": idx.dayofyear,
                  "t_years": (idx - idx[0]).days / 365.25, "y": Y}).dropna()
rf = RandomForestRegressor(n_estimators=300, min_samples_leaf=20, max_features=0.5, oob_score=True,
                           n_jobs=-1, random_state=SEED).fit(F.drop(columns="y"), F.y)
pdp = partial_dependence(rf, F.drop(columns="y"), ["S"], grid_resolution=40, percentiles=(0.05, 0.95))
gx, gy = pdp["grid_values"][0], pdp["average"][0]
rf_slope = np.polyfit(gx, gy, 1)[0]
pd.DataFrame({"S_sd": gx, "rf_partial_dependence_ppm": gy - np.interp(0, gx, gy)}).round(5).to_csv(RES / "baseline_rf_partial_dependence.csv", index=False)
base = pd.DataFrame([dict(model="climatology only (year x month x hour cell means)", r2=1 - ((yv - cm) ** 2).sum() / ((yv - yv.mean()) ** 2).sum()),
                     dict(model="partial R2 of S given cells and log wind", r2=partial_r2),
                     dict(model="random forest OOB R2 (Grange-Carslaw style normalisation)", r2=rf.oob_score_),
                     dict(model="RF partial-dependence slope of S (ppm per SD, 5-95% range)", r2=rf_slope)])
base.round(4).to_csv(RES / "baselines.csv", index=False)

# ---------------- pre-registered decision rule (D-22)
prim = res[(res.group == "primary") & res.label.str.startswith("Direct")].iloc[0]
yrs = res[res.group == "year"]; ncr = res[res.label.str.startswith("Negative control")].iloc[0]
c1 = prim.ci_lo > 0 or prim.ci_hi < 0
c2 = (np.sign(yrs.estimate) != np.sign(prim.estimate)).sum() < 2
c3 = not ((ncr.ci_lo > 0 or ncr.ci_hi < 0) and abs(ncr.estimate) >= 0.5 * abs(prim.estimate))
dec = pd.DataFrame([dict(criterion="Direct-effect 95% CI excludes 0", met=bool(c1)),
                    dict(criterion="Sign agrees in at least 4 of 5 years", met=bool(c2)),
                    dict(criterion="Negative control not >= 50% of effect with CI excluding 0", met=bool(c3)),
                    dict(criterion="H1 gate (all three)", met=bool(c1 and c2 and c3))])
dec.to_csv(RES / "h1_decision.csv", index=False)

# ---------------- Figure 4: partial-residual plot with linear and spline fits
q = pd.qcut(rl_s, 25, labels=False); bx = rl_s.groupby(q).mean(); by = rl_y.groupby(q).mean()
fr = pd.read_csv(RES / "h1_functional_form.csv")
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
ax[0].hexbin(rl_s, rl_y, gridsize=55, bins="log", cmap="Greys", mincnt=1, extent=(-3, 4, -0.4, 0.8))
ax[0].plot(bx, by, "o", c="C3", ms=3, label="25 quantile-bin means")
ax[0].plot(fr.S_sd, fr.linear_effect_ppm - np.interp(0, fr.S_sd, fr.linear_effect_ppm), "k-", lw=1, label=f"linear, {b_dir:.3f} ppm/SD")
ax[0].set_xlim(-3, 4); ax[0].set_ylim(-0.4, 0.8)
ax[0].set_xlabel("Stability S (SD units, adjusted)"); ax[0].set_ylabel("Network CH$_4$ anomaly (ppm, adjusted)")
ax[0].legend(fontsize=6, frameon=False); ax[0].set_title("a  Partial residuals (cells and log wind removed)")
ax[1].plot(fr.S_sd, fr.spline_effect_ppm, "C0-", label="piecewise-linear spline")
ax[1].plot(fr.S_sd, fr.linear_effect_ppm, "k--", label="linear")
ax[1].plot(gx, gy - np.interp(0, gx, gy), "C2-", label="random-forest partial dependence")
ax[1].axhline(0, c="0.8", lw=0.6); ax[1].set_xlabel("Stability S (SD units)"); ax[1].set_ylabel("Effect relative to S = 0 (ppm)")
ax[1].legend(fontsize=6, frameon=False); ax[1].set_title("b  Functional form and RF baseline")
fig.text(0.01, -0.06, f"Response: median CH$_4$ anomaly over 7 core stations (Kmin 5); S = AMS 5 T90 - T20 standardised on 2021-2023. "
         f"n = {len(d_dir):,} hours, {d_dir.cell.nunique():,} year x month x hour cells; development data 2021-2025.", fontsize=6.2)
save(fig, FIG / "figure04_stability_elasticity")

# ---------------- Figure 5: forest plot
fp = res[res.group != "uncertainty"].iloc[::-1].reset_index(drop=True)
fig, ax = plt.subplots(figsize=(6.4, 0.2 * len(fp) + 0.8))
colors = {"primary": "k", "year": "C0", "season": "C1", "response": "C2", "proxy": "C4", "negative control": "C3"}
for i, r in fp.iterrows():
    ax.plot([r.ci_lo, r.ci_hi], [i, i], c=colors[r.group], lw=1.2); ax.plot(r.estimate, i, "o", c=colors[r.group], ms=3)
ax.axvline(0, c="0.5", lw=0.6); ax.axvline(b_dir, c="0.8", lw=0.6, ls="--")
ax.set_yticks(range(len(fp)), fp.label, fontsize=6); ax.set_xlabel("ppm per SD of stability proxy (95% block-bootstrap CI)")
ax.set_title("H1 robustness: estimates by replication, response, proxy and negative control", fontsize=8)
save(fig, FIG / "figure05_h1_robustness")

runmeta.write(EXP, dict(experiment="E04_stability_elasticity", status="exploratory", seed_used=SEED, n_boot=NB))
print(res[["group", "label", "n_hours", "estimate", "ci_lo", "ci_hi"]].round(4).to_string(index=False))
print(base.round(4).to_string(index=False)); print(dec.to_string(index=False))
