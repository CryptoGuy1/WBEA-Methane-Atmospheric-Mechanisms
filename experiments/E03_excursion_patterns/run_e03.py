"""E03 - Diurnal, seasonal, spatial and meteorological patterns of CH4 concentration excursions.
Descriptive only: no hypothesis test is decided here. Development data, all labelled exploratory.
Excursion: station CH4 above its own 2021-2023 P95 (P90/P99 as sensitivity). An excursion is a
concentration statistic, not an emission event."""
import sys, pathlib, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(EXP.parents[1] / "src"))
from wbea.config import CFG
from wbea.io import load_dev, load_era5, load_fire_days
from wbea.wind import composite
from wbea.geometry import pair_table
from wbea.solar import elevation_deg
from wbea.stats import block_ids
from wbea import runmeta
from wbea.plotstyle import plt, save

RES = EXP / "results"; FIG = EXP / "figures"; RES.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
rng = np.random.default_rng(CFG["project"]["seed"] + 3); NB = CFG["bootstrap"]["n_boot"]
P = load_dev(); ST = CFG["stations"]["usable"]
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); idx = CH.index
ref = CH.loc[str(CFG["split"]["reference_years"][0]):str(CFG["split"]["reference_years"][-1])]
Q = {q: ref.quantile(q / 100) for q in (90, 95, 99)}
pd.DataFrame(Q).round(4).to_csv(RES / "thresholds_ppm_2021_2023.csv")
EX = {q: CH.gt(Q[q]).astype(float).where(CH.notna()) for q in Q}   # 1.0/0.0/NaN
E = EX[95]; X = CH - ref.median()
elev = elevation_deg(idx); night = elev <= 0
blk = block_ids(idx, CFG["bootstrap"]["block_days"]); ub = np.unique(blk)

def boot_ratio(num_by_bg, den_by_bg):
    """num/den arrays shaped (n_blocks, n_groups); joint block bootstrap of the pooled ratio per group."""
    est = num_by_bg.sum(0) / den_by_bg.sum(0); draws = np.empty((NB, num_by_bg.shape[1]))
    for b in range(NB):
        k = rng.integers(0, len(ub), len(ub))
        draws[b] = num_by_bg[k].sum(0) / den_by_bg[k].sum(0)
    return est, np.percentile(draws, 2.5, 0), np.percentile(draws, 97.5, 0)

def by_block(group):                                      # pooled over stations
    num = E.sum(1).groupby([blk, group]).sum().unstack(fill_value=0)
    den = E.notna().sum(1).groupby([blk, group]).sum().unstack(fill_value=0)
    return num.reindex(ub, fill_value=0).values, den.reindex(ub, fill_value=0).values, num.columns

# ------------------------------------------------ Q1 hour and month profiles (pooled, 12 stations)
n, d, cols = by_block(idx.hour); h_est, h_lo, h_hi = boot_ratio(n, d)
n, d, mcols = by_block(idx.month); m_est, m_lo, m_hi = boot_ratio(n, d)
pd.DataFrame({"hour_ending": cols, "rate_pct": 100 * h_est, "ci_lo": 100 * h_lo, "ci_hi": 100 * h_hi}).round(2) \
  .to_csv(RES / "q1_p95_rate_by_hour.csv", index=False)
pd.DataFrame({"month": mcols, "rate_pct": 100 * m_est, "ci_lo": 100 * m_lo, "ci_hi": 100 * m_hi}).round(2) \
  .to_csv(RES / "q1_p95_rate_by_month.csv", index=False)
hm = (E.sum(1).groupby([idx.month, idx.hour]).sum() / E.notna().sum(1).groupby([idx.month, idx.hour]).sum()).unstack()
(100 * hm).round(2).to_csv(RES / "q1_p95_rate_month_by_hour.csv")

# ------------------------------------------------ Q2 station heterogeneity
q2 = []
for s in ST:
    e = E[s]; v = e.notna()
    row = dict(station=s, rate_p95_pct=round(100 * e.mean(), 2),
               night_share_of_excursions=round(float(e[night].sum() / e.sum()), 3),
               night_share_of_valid_hours=round(float(v[night].sum() / v.sum()), 3),
               peak_hour=int(e.groupby(idx.hour).mean().idxmax()), peak_month=int(e.groupby(idx.month).mean().idxmax()))
    for y in range(2021, 2026):
        row[f"rate_{y}_pct"] = round(100 * e[idx.year == y].mean(), 2)
    q2.append(row)
q2 = pd.DataFrame(q2); q2.to_csv(RES / "q2_station_heterogeneity.csv", index=False)

# ------------------------------------------------ Q3 spatial co-occurrence (all 66 pairs)
pt = pair_table(ST); lift = []
for _, r in pt.iterrows():
    a, b = E[r.i], E[r.j]; ok = a.notna() & b.notna(); a, b = a[ok], b[ok]
    pab = (a * b).mean()
    cell = a.index.month * 100 + a.index.hour                       # expected joint rate if independent WITHIN month x hour
    exp_joint = (a.groupby(cell).mean() * b.groupby(cell).mean() * a.groupby(cell).size()).sum() / len(a)
    lift.append(dict(i=r.i, j=r.j, km=round(r.km, 2), p_i=a.mean(), p_j=b.mean(), p_both=pab,
                     lift=pab / (a.mean() * b.mean()), lift_given_month_hour=pab / exp_joint, p_j_given_i=pab / a.mean()))
lift = pd.DataFrame(lift); lift.to_csv(RES / "q3_pairwise_cooccurrence.csv", index=False)
rho = lift[["km", "lift"]].corr("spearman").iloc[0, 1]; rho_c = lift[["km", "lift_given_month_hour"]].corr("spearman").iloc[0, 1]

# ------------------------------------------------ Q4 meteorological strata (fixed regimes, correction 5)
S = (P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"])
cut = S.loc["2021":"2023"].quantile([1 / 3, 2 / 3]).values
pd.Series(cut, index=["t1", "t2"]).round(4).to_csv(RES / "stability_tercile_cutpoints_degC.csv")
stab = pd.Series(np.digitize(S, cut), index=idx).where(S.notna())
era = load_era5(); rows = []
for s in ST:
    w = composite(P[s]).ws
    wc = pd.Series(np.digitize(w, CFG["h3"]["wind_classes_ms"]), index=idx).where(w.notna())
    blh = era[s]["blh"].reindex(idx)
    rows.append(pd.DataFrame({"station": s, "e": E[s], "stab": stab, "wind": wc, "night": night, "blh": blh}))
L = pd.concat(rows).dropna(subset=["e", "stab", "wind"])
L["regime"] = (L.stab.map({0: "unstable", 1: "neutral", 2: "stable"}) + "|" +
               L.wind.map({0: "<1", 1: "1-2.5", 2: ">=2.5"}) + "|" + np.where(L.night, "night", "day"))
g = L.groupby("regime").agg(hours=("e", "size"), excursions=("e", "sum"), rate=("e", "mean"))
g["share_of_hours_pct"] = 100 * g.hours / g.hours.sum(); g["share_of_excursions_pct"] = 100 * g.excursions / g.excursions.sum()
g["rate_pct"] = 100 * g.rate; g.drop(columns="rate").round(2).sort_values("rate_pct", ascending=False).to_csv(RES / "q4_regime_table.csv")
st3 = L.groupby("stab").e.agg(["mean", "size"]); wd3 = L.groupby("wind").e.agg(["mean", "size"])
L["blh_q"] = pd.qcut(L.blh, 5, labels=False); bq = L.groupby("blh_q").agg(blh_median=("blh", "median"), rate=("e", "mean"), n=("e", "size"))
bq.round(4).to_csv(RES / "q4_rate_by_era5_blh_quintile.csv")

# ------------------------------------------------ Q5 network covariance by stability tercile (Fig S1)
cors = {}; summ = []
for k, name in enumerate(["unstable", "neutral", "stable"]):
    c = X[stab == k].corr(min_periods=500); cors[name] = c
    off = c.values[~np.eye(len(ST), dtype=bool)]
    summ.append(dict(tercile=name, hours=int((stab == k).sum()), mean_offdiag_r=round(np.nanmean(off), 3),
                     min_r=round(np.nanmin(off), 3), max_r=round(np.nanmax(off), 3)))
    c.round(3).to_csv(RES / f"q5_anomaly_correlation_{name}.csv")
summ = pd.DataFrame(summ); summ.to_csv(RES / "q5_correlation_summary.csv", index=False)

# ------------------------------------------------ Q6 episode-definition sensitivity (Fig S4)
def onsets(c, thr, rule):
    above = c > thr; valid = c.notna(); below = valid & ~above
    if rule == "R1 crossing, missing counts as below":
        a = above.fillna(False); return a & ~a.shift(1, fill_value=False)
    if rule == "R2 crossing after valid below":
        return above & below.shift(1, fill_value=False)
    if rule in ("R3 single gaps bridged", "R5 6 h clearance, single gaps bridged"):
        gap1 = c.isna() & c.shift(1).notna() & c.shift(-1).notna()
        c = c.where(~gap1, (c.shift(1) + c.shift(-1)) / 2); above = c > thr; below = c.notna() & ~above
        if rule.startswith("R3"):
            return above & below.shift(1, fill_value=False)
    run = below.astype(int).groupby((~below).cumsum()).cumsum()
    return above & (run.shift(1, fill_value=0) >= 6)
RULES = ["R1 crossing, missing counts as below", "R2 crossing after valid below", "R3 single gaps bridged",
         "R4 6 h clearance", "R5 6 h clearance, single gaps bridged"]
q6 = pd.DataFrame({r: sum(onsets(CH[s], Q[95][s], r).groupby(idx.hour).sum() for s in ST) for r in RULES})
q6.index.name = "hour_ending"; q6.to_csv(RES / "q6_onsets_by_hour_by_rule.csv")
lower = E.fillna(0).sum(1).groupby(idx.hour).sum() / (len(ST) * idx.hour.value_counts().sort_index())
upper = (E.fillna(1)).sum(1).groupby(idx.hour).sum() / (len(ST) * idx.hour.value_counts().sort_index())
pd.DataFrame({"lower_pct": 100 * lower, "upper_pct": 100 * upper, "complete_case_pct": 100 * h_est}).round(2) \
  .to_csv(RES / "q6_manski_bounds_by_hour.csv")

# ------------------------------------------------ Q7 smoke sensitivity (D-11)
fire = load_fire_days(); pm = pd.DataFrame({s: P[s]["PM2.5 (ug/m3)"] for s in ST if "PM2.5 (ug/m3)" in P[s]}).median(1)
smoke = pd.Series(idx.normalize().isin(fire), index=idx) | (pm > CFG["smoke"]["pm25_network_median_ugm3"])
q7 = pd.DataFrame([dict(set=k, station_hours=int(E[m].notna().sum().sum()), rate_p95_pct=round(100 * float(E[m].stack().mean()), 2),
                        share_of_all_excursions_pct=round(100 * float(E[m].sum().sum() / E.sum().sum()), 2))
                   for k, m in [("smoke hours", smoke), ("non-smoke hours", ~smoke)]])
q7.to_csv(RES / "q7_smoke_sensitivity.csv", index=False)

# ------------------------------------------------ Figures
fig = plt.figure(figsize=(7.4, 5.8)); gs = fig.add_gridspec(2, 2, hspace=0.5, wspace=0.55)
a = fig.add_subplot(gs[0, 0]); im = a.imshow(100 * hm.values, aspect="auto", origin="lower", cmap="magma",
                                               extent=[-0.5, 23.5, 0.5, 12.5])
a.set_xlabel("Hour ending (MST)"); a.set_ylabel("Month"); a.set_xticks(range(0, 24, 6)); a.set_yticks(range(1, 13, 2))
fig.colorbar(im, ax=a, fraction=0.05).set_label("P95 excursion rate (%)"); a.set_title("a  Hour x month, 12 stations")
b = fig.add_subplot(gs[0, 1]); b.fill_between(range(24), 100 * h_lo, 100 * h_hi, alpha=.3); b.plot(range(24), 100 * h_est, "k-")
b.axhline(5, ls=":", c="grey"); b.set_xlabel("Hour ending (MST)"); b.set_ylabel("Rate (%)"); b.set_xticks(range(0, 24, 6))
b.set_title("b  Diurnal profile (95% CI)")
c = fig.add_subplot(gs[1, 0]); c.fill_between(mcols, 100 * m_lo, 100 * m_hi, alpha=.3); c.plot(mcols, 100 * m_est, "k-o", ms=3)
c.axhline(5, ls=":", c="grey"); c.set_xlabel("Month"); c.set_ylabel("Rate (%)"); c.set_xticks(range(1, 13))
c.set_title("c  Seasonal profile (95% CI)")
dd = fig.add_subplot(gs[1, 1]); dd.scatter(lift.km, lift.lift, s=9, c="lightgrey", label=f"unconditional (rho {rho:.2f})")
dd.scatter(lift.km, lift.lift_given_month_hour, s=9, c="k", label=f"given month x hour (rho {rho_c:.2f})")
dd.legend(fontsize=6, frameon=False); dd.axhline(1, ls=":", c="grey")
dd.set_xscale("log"); dd.set_xlabel("Station separation (km)"); dd.set_ylabel("Co-occurrence lift")
dd.set_title("d  Joint excursions vs distance (66 pairs)")
fig.text(0.01, 0.0, "Excursion = CH$_4$ above the station's 2021-2023 P95 (dotted line = 5% by construction in the reference years). "
         "Development data 2021-01-01 to 2025-12-02; 12 stations; 14-day joint block bootstrap, 2,000 replicates.", fontsize=6.3)
save(fig, FIG / "figure03_excursion_phenotype")

fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.6))
for k, (name, cmat) in enumerate(cors.items()):
    im = ax[k].imshow(cmat.values, vmin=-0.2, vmax=1, cmap="viridis")
    ax[k].set_xticks(range(len(ST)), [s.replace("AMS ", "") for s in ST], fontsize=6)
    ax[k].set_yticks(range(len(ST)), [s.replace("AMS ", "") for s in ST], fontsize=6)
    ax[k].set_title(f"{name} (mean r = {summ.mean_offdiag_r[k]:.2f})")
fig.colorbar(im, ax=ax, fraction=0.02).set_label("Pearson r of CH$_4$ anomaly")
fig.text(0.01, -0.05, "Anomaly = CH$_4$ minus station 2021-2023 median. Terciles of AMS 5 T90 - T20 with fixed 2021-2023 cut points "
         f"({cut[0]:.2f}, {cut[1]:.2f} degC). Development data.", fontsize=6.3)
save(fig, FIG / "figureS1_network_correlation_by_stability")

fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.8))
for r in RULES: ax[0].plot(q6.index, q6[r], marker="o", ms=2, label=r)
ax[0].set_xlabel("Hour ending (MST)"); ax[0].set_ylabel("P95 onsets (12 stations, 2021-2025)"); ax[0].set_xticks(range(0, 24, 6))
ax[0].legend(fontsize=5.5, frameon=False); ax[0].set_title("a  Episode onsets by definition")
ax[1].fill_between(range(24), 100 * lower, 100 * upper, alpha=.3, label="Manski bounds")
ax[1].plot(range(24), 100 * h_est, "k-", label="complete case"); ax[1].set_xticks(range(0, 24, 6))
ax[1].set_xlabel("Hour ending (MST)"); ax[1].set_ylabel("Excursion-hour rate (%)"); ax[1].legend(fontsize=6, frameon=False)
ax[1].set_title("b  Missing-data bounds")
save(fig, FIG / "figureS4_episode_definition_sensitivity")

runmeta.write(EXP, dict(experiment="E03_excursion_patterns", status="exploratory", seed_used=CFG["project"]["seed"] + 3,
                        external_manifest="manifests/external_derived_SHA256SUMS.txt"))
print("hour profile", (100 * h_est).round(2).tolist()); print("month profile", (100 * m_est).round(2).tolist())
print(q2.to_string(index=False)); print("lift~km spearman", round(rho, 3), "conditional", round(rho_c, 3)); print(lift.sort_values("lift", ascending=False).head(5).round(3).to_string(index=False))
print(lift.sort_values("km").head(8).round(3).to_string(index=False))
print("stab rates", (100 * st3["mean"]).round(2).to_dict(), "wind rates", (100 * wd3["mean"]).round(2).to_dict()); print(bq.round(3).to_string())
print(pd.read_csv(RES / "q4_regime_table.csv").head(8).to_string(index=False)); print(summ.to_string(index=False))
print(q6.sum().to_dict()); print(q6.loc[[2, 4, 6, 8, 12]].to_string()); print(q7.to_string(index=False)); print("cut", cut)
