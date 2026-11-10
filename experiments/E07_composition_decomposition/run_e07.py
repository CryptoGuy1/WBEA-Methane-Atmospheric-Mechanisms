"""E07 - H3: how much of the year-to-year difference in station CH4 excursion rates is explained by the
mix of meteorological regimes (Kitagawa decomposition; specification D-40). Development data; exploratory.
The within-regime term is NOT an emission change: it mixes background growth, local emissions,
instrument drift and anything else not captured by the 18 regimes."""
import sys, pathlib, itertools, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(EXP.parents[1] / "src"))
from wbea.config import CFG
from wbea.io import load_dev, load_fire_days
from wbea.wind import composite
from wbea.solar import elevation_deg
from wbea import runmeta
from wbea.plotstyle import plt, save
from sklearn.ensemble import HistGradientBoostingClassifier

RES = EXP / "results"; FIG = EXP / "figures"; RES.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
SEED = CFG["project"]["seed"] + 7; rng = np.random.default_rng(SEED); NB = 1000; MINH = CFG["h3"]["min_cell_hours"]
P = load_dev(); ST = CFG["stations"]["usable"]; idx = P["AMS 1"].index
YEARS = [2021, 2022, 2023, 2024, 2025]
WIN = np.asarray((idx.month <= 11) | ((idx.month == 12) & (idx.day == 1) & (idx.hour == 0)))   # 1 Jan - 30 Nov (hour-ending)
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); REF = CH.loc["2021":"2023"]
S5 = P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"]
stab = pd.Series(np.digitize(S5, S5.loc["2021":"2023"].quantile([1 / 3, 2 / 3]).values), index=idx).where(S5.notna())
night = (elevation_deg(idx) <= 0).astype(int)
YR = np.asarray(idx.year); BLK = YR * 100 + (np.asarray(idx.dayofyear) - 1) // CFG["bootstrap"]["block_days"]
UB = np.unique(BLK); BI = np.searchsorted(UB, BLK); BYEAR = UB // 100
fire = load_fire_days(); pm = pd.DataFrame({s: P[s]["PM2.5 (ug/m3)"] for s in ST if "PM2.5 (ug/m3)" in P[s]}).median(1)
PWIP = (pd.Series(idx.normalize().isin(fire), index=idx) | (pm > CFG["smoke"]["pm25_network_median_ugm3"])).to_numpy()
CELL = {}
for s in ST:
    wc = pd.Series(np.digitize(composite(P[s]).ws, CFG["h3"]["wind_classes_ms"]), index=idx).where(composite(P[s]).ws.notna())
    c = stab * 6 + wc * 2 + night                     # cell id 0..17 = stab*6 + wind*2 + night
    CELL[s] = c.to_numpy()

def counts(indicator, extra_mask=None, manski=None):
    """Arrays H, Xn of shape (station, block, 18): valid hours and excursions per cell."""
    H = np.zeros((len(ST), len(UB), 18)); Xn = np.zeros_like(H)
    for k, s in enumerate(ST):
        e = indicator[s].to_numpy(); c = CELL[s]; ok = np.isfinite(c) & WIN
        if extra_mask is not None: ok &= extra_mask
        if manski is None: ok &= np.isfinite(e); ev = np.nan_to_num(e)
        else: ev = np.where(np.isfinite(e), e, 1.0 if manski == "upper" else 0.0)
        key = BI[ok] * 18 + c[ok].astype(int)
        H[k] = np.bincount(key, minlength=len(UB) * 18).reshape(len(UB), 18)
        Xn[k] = np.bincount(key, ev[ok], minlength=len(UB) * 18).reshape(len(UB), 18)
    return H, Xn

def by_year(A, w=None):
    w = np.ones(len(UB)) if w is None else w
    return np.stack([(A[:, BYEAR == y, :] * w[BYEAR == y][None, :, None]).sum(1) for y in YEARS], 1)   # (st, year, 18)

def groups_for(ha, hb):
    """Merge rule D-40. Returns a list of cell-id arrays."""
    out = []
    for nt in (0, 1):
        # step 1: pool wind classes within any (stability, day/night) group containing a sparse cell
        g1 = []
        for st in range(3):
            grp = [st * 6 + w * 2 + nt for w in range(3)]
            if all(min(ha[c], hb[c]) >= MINH for c in grp): g1 += [[c] for c in grp]
            else: g1.append(grp)
        # step 2: if any resulting group is still sparse, pool everything within this day/night half
        if any(min(ha[grp].sum(), hb[grp].sum()) < MINH for grp in g1): g1 = [[st * 6 + w * 2 + nt for st in range(3) for w in range(3)]]
        out += g1
    return [np.array(x) for x in out]

def kitagawa(ha, xa, hb, xb, groups):
    Ha = np.array([ha[g].sum() for g in groups]); Hb = np.array([hb[g].sum() for g in groups])
    Xa = np.array([xa[g].sum() for g in groups]); Xb = np.array([xb[g].sum() for g in groups])
    pa, pb = Ha / Ha.sum(), Hb / Hb.sum()
    with np.errstate(invalid="ignore", divide="ignore"):
        qa, qb = Xa / Ha, Xb / Hb
    comp = np.nansum((pa - pb) * (qa + qb) / 2); within = np.nansum((pa + pb) * (qa - qb) / 2)
    return comp, within, Xa.sum() / Ha.sum() - Xb.sum() / Hb.sum()

PAIRS = list(itertools.combinations(range(len(YEARS)), 2))

def analyse(H, Xn, groups=None, nb=0, years_idx=None):
    yi = [k for k in range(len(YEARS))] if years_idx is None else years_idx
    prs = [p for p in PAIRS if p[0] in yi and p[1] in yi]
    Hy, Xy = by_year(H), by_year(Xn); rows = []; G = {} if groups is None else groups
    for k, s in enumerate(ST):
        for a, b in prs:
            key = (s, a, b)
            if groups is None: G[key] = groups_for(Hy[k, b], Hy[k, a])
            c, w, t = kitagawa(Hy[k, b], Xy[k, b], Hy[k, a], Xy[k, a], G[key])     # later year minus earlier year
            rows.append(dict(station=s, year_a=YEARS[a], year_b=YEARS[b], composition=c, within=w, total=t,
                             n_groups=len(G[key])))
    df = pd.DataFrame(rows); share = (df.composition * df.total).sum() / (df.total ** 2).sum()
    boots = []
    for _ in range(nb):
        w = np.zeros(len(UB))
        for y in YEARS:
            ids = np.where(BYEAR == y)[0]; w[ids] += np.bincount(rng.integers(0, len(ids), len(ids)), minlength=len(ids))
        Hb_, Xb_ = by_year(H, w), by_year(Xn, w); cs = ts = 0.0
        for k, s in enumerate(ST):
            for a, b in prs:
                c, _, t = kitagawa(Hb_[k, b], Xb_[k, b], Hb_[k, a], Xb_[k, a], G[(s, a, b)]); cs += c * t; ts += t * t
        boots.append(cs / ts)
    return df, share, np.array(boots), G

# ---------------- primary
E95 = CH.gt(REF.quantile(.95)).astype(float).where(CH.notna())
H, Xn = counts(E95); prim, s_prim, bs_prim, G = analyse(H, Xn, nb=NB)
prim.round(6).to_csv(RES / "h3_contrasts_primary.csv", index=False)
merges = pd.DataFrame([dict(station=k[0], year_a=YEARS[k[1]], year_b=YEARS[k[2]], n_groups=len(v)) for k, v in G.items()])
merges.to_csv(RES / "h3_merge_log.csv", index=False)
per_station = prim.groupby("station").apply(lambda d: pd.Series(dict(
    share=(d.composition * d.total).sum() / (d.total ** 2).sum(), mean_abs_total_pp=100 * d.total.abs().mean(),
    mean_abs_composition_pp=100 * d.composition.abs().mean()))).reset_index()
per_station.round(4).to_csv(RES / "h3_per_station.csv", index=False)

# ---------------- sensitivities
sens = [dict(analysis="Primary (raw P95, Jan-Nov, 2021-2025)", share=s_prim, ci_lo=np.percentile(bs_prim, 2.5), ci_hi=np.percentile(bs_prim, 97.5))]
for side in ("lower", "upper"):
    Hm, Xm = counts(E95, manski=side); _, sm, _, _ = analyse(Hm, Xm, groups=G)
    sens.append(dict(analysis=f"Manski {side} (missing CH4 as {'non-exceedance' if side == 'lower' else 'exceedance'})", share=sm))
aft = CH[CH.index.hour.isin(range(12, 18))].stack(); B = aft.groupby(aft.index.get_level_values(0).normalize()).quantile(0.10)
XB = CH.sub(B.reindex(idx.normalize()).values, axis=0); EB = XB.gt(XB.loc["2021":"2023"].quantile(.95)).astype(float).where(XB.notna())
Hb_, Xb_ = counts(EB); dfb, sb, bsb, _ = analyse(Hb_, Xb_, nb=300)
sens.append(dict(analysis="Background-adjusted excess C - B_t (D-16)", share=sb, ci_lo=np.percentile(bsb, 2.5), ci_hi=np.percentile(bsb, 97.5)))
dfb.round(6).to_csv(RES / "h3_contrasts_background_adjusted.csv", index=False)
Hp, Xp = counts(E95, extra_mask=~PWIP); _, sp, bsp, _ = analyse(Hp, Xp, nb=300)
sens.append(dict(analysis="PWIP hours excluded", share=sp, ci_lo=np.percentile(bsp, 2.5), ci_hi=np.percentile(bsp, 97.5)))
WIN_FULL = WIN.copy(); WIN[:] = True
Hf, Xf = counts(E95); _, sf, bsf, _ = analyse(Hf, Xf, nb=300, years_idx=[0, 1, 2, 3])
WIN[:] = WIN_FULL
sens.append(dict(analysis="Full calendar years 2021-2024 only", share=sf, ci_lo=np.percentile(bsf, 2.5), ci_hi=np.percentile(bsf, 97.5)))

# ---------------- deweathering baseline (gradient boosting, per station)
dw_rows = []
for s in ST:
    w = composite(P[s])
    F = pd.DataFrame({"S": S5, "ws": w.ws, "wds": np.sin(np.deg2rad(w.wd)), "wdc": np.cos(np.deg2rad(w.wd)),
                      "at2": P[s]["AT2 (C)"], "hour": idx.hour, "doy": idx.dayofyear, "year": idx.year}, index=idx)
    ok = F.notna().all(1) & E95[s].notna() & WIN
    clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, random_state=SEED).fit(F[ok], E95[s][ok])
    base = F[F.notna().all(1) & WIN]
    rate = {}
    for y in YEARS:
        Fy = base.copy(); Fy["year"] = y; rate[y] = clf.predict_proba(Fy)[:, 1].mean()
    for a, b in PAIRS:
        dw_rows.append(dict(station=s, year_a=YEARS[a], year_b=YEARS[b], deweathered_change=rate[YEARS[b]] - rate[YEARS[a]]))
dw = pd.DataFrame(dw_rows).merge(prim, on=["station", "year_a", "year_b"])
s_rf = 1 - (dw.deweathered_change * dw.total).sum() / (dw.total ** 2).sum()
dw.round(6).to_csv(RES / "baseline_deweathered_changes.csv", index=False)
sens.append(dict(analysis="Baseline: boosted-tree deweathering, implied meteorology share", share=s_rf))
sens = pd.DataFrame(sens); sens.round(4).to_csv(RES / "h3_sensitivity.csv", index=False)
r_within_dw = np.corrcoef(dw.within, dw.deweathered_change)[0, 1]

dec = pd.DataFrame([dict(criterion="H3: 95% CI of pooled meteorology-mix share excludes 0", value=f"{s_prim:.3f} ({sens.ci_lo[0]:.3f} to {sens.ci_hi[0]:.3f})",
                         met=bool(sens.ci_lo[0] > 0 or sens.ci_hi[0] < 0))])
dec.to_csv(RES / "h3_decision.csv", index=False)

# ---------------- Figure 9
fig = plt.figure(figsize=(7.4, 5.4)); gs = fig.add_gridspec(2, 1, height_ratios=[1, 1.5], hspace=0.55)
a = fig.add_subplot(gs[0]); sv = sens.iloc[::-1].reset_index(drop=True)
for i, r in sv.iterrows():
    a.plot(r.share, i, "o", c="k" if i == len(sv) - 1 else "0.4", ms=4)
    if np.isfinite(r.get("ci_lo", np.nan)): a.plot([r.ci_lo, r.ci_hi], [i, i], c="k" if i == len(sv) - 1 else "0.4", lw=1.2)
a.axvline(0, c="0.6", lw=0.6); a.set_yticks(range(len(sv)), sv.analysis, fontsize=6)
a.set_xlabel("Meteorology-mix share of between-year variation in P95 excursion rate"); a.set_title("a  Pooled share (120 station-year contrasts; 95% block-bootstrap CI)")
b = fig.add_subplot(gs[1]); cons = prim[prim.year_b - prim.year_a == 1].reset_index(drop=True); x = np.arange(len(cons))
b.bar(x, 100 * cons.composition, color="C0", label="meteorology mix"); b.bar(x, 100 * cons.within, bottom=np.where(np.sign(cons.within) == np.sign(cons.composition), 100 * cons.composition, 0), color="C1", label="within regime")
b.plot(x, 100 * cons.total, "k_", ms=7, label="total change"); b.axhline(0, c="0.6", lw=0.6)
b.set_xticks([4 * k + 1.5 for k in range(len(ST))], [s.replace("AMS ", "") for s in ST], fontsize=7)
for k in range(1, len(ST)): b.axvline(4 * k - 0.5, c="0.9", lw=0.6)
b.set_xlabel("Station (bars: 2021-22, 22-23, 23-24, 24-25)"); b.set_ylabel("Change in excursion rate (pp)")
b.legend(fontsize=6, frameon=False, ncol=3); b.set_title("b  Consecutive-year changes split by Kitagawa decomposition")
fig.text(0.01, 0.0, "P95 excursions (station 2021-2023 thresholds), 1 Jan - 30 Nov each year, 18 regimes (AMS 5 stability tercile x station wind class x solar "
         "day/night). Within-regime change is not an emission change. Development data.", fontsize=6.0)
save(fig, FIG / "figure09_composition_decomposition")

# ---------------- Figure S3: baselines for H1 (E04) and H3 (this experiment)
e04 = EXP.parents[0] / "E04_stability_elasticity" / "results"
ff = pd.read_csv(e04 / "h1_functional_form.csv"); rf = pd.read_csv(e04 / "baseline_rf_partial_dependence.csv")
fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.9))
ax[0].plot(ff.S_sd, ff.linear_effect_ppm, "k--", label="fixed-effects linear (E04)"); ax[0].plot(ff.S_sd, ff.spline_effect_ppm, "C0-", label="spline")
ax[0].plot(rf.S_sd, rf.rf_partial_dependence_ppm, "C2-", label="random-forest normalisation")
ax[0].set_xlabel("Stability S (SD)"); ax[0].set_ylabel("Effect on network CH$_4$ (ppm)"); ax[0].legend(fontsize=6, frameon=False); ax[0].set_title("a  H1: fixed effects vs deweathering")
ax[1].scatter(100 * dw.within, 100 * dw.deweathered_change, s=8, c="k"); lim = 100 * max(dw.within.abs().max(), dw.deweathered_change.abs().max())
ax[1].plot([-lim, lim], [-lim, lim], ":", c="0.6"); ax[1].set_xlabel("Kitagawa within-regime change (pp)"); ax[1].set_ylabel("Deweathered change (pp)")
ax[1].set_title(f"b  H3: 120 contrasts, r = {r_within_dw:.2f}")
save(fig, FIG / "figureS3_baseline_comparison")

runmeta.write(EXP, dict(experiment="E07_composition_decomposition", status="exploratory", seed_used=SEED, n_boot=NB))
print(sens.round(4).to_string(index=False)); print(per_station.round(3).to_string(index=False)); print(dec.to_string(index=False))
print("merge groups distribution", merges.n_groups.value_counts().to_dict(), "| r(within, deweathered) =", round(r_within_dw, 3))
print(cons[["station", "year_a", "year_b", "composition", "within", "total"]].assign(**{c: lambda d, c=c: (100 * d[c]).round(2) for c in ["composition", "within", "total"]}).to_string(index=False))
