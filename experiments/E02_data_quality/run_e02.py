"""E02 - Data completeness, calibration gaps and measurement quality (development data only).
Questions
 Q1 How complete is every variable the hypotheses need, by station and year?
 Q2 Which station-months fail Alberta's 90% operational criterion, with and without QA/QC hours?
 Q3 How are missing hours distributed by hour of day and across stations (simultaneity, run lengths)?
 Q4 Is the nightly Z gap ignorable given hour of day? (CH4 bracketing Z hours vs same hour/month without Z)
 Q5 How many hours are usable for H1 under the frozen core rule and the expanded sensitivity rule?
"""
import sys, pathlib, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(EXP.parents[1] / "src"))
from wbea.config import CFG
from wbea.io import load_dev
from wbea.wind import composite
from wbea.stats import block_ids, block_bootstrap_indices, pct_ci
from wbea import runmeta
from wbea.plotstyle import plt, save

RES = EXP / "results"; FIG = EXP / "figures"; RES.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
rng = np.random.default_rng(CFG["project"]["seed"] + 2)
P = load_dev(); ST = CFG["stations"]["usable"]
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); TK = pd.DataFrame({s: P[s]["CH4 (ppm)__token"] for s in ST})
idx = CH.index

# ---------------------------------------------------------------- Q1 variable completeness by station-year
rows = []
for s in ST:
    d = P[s]; w = composite(d)
    vars_ = {"CH4": d["CH4 (ppm)"], "NMHC": d.get("NMHC (ppm)"), "AT2": d.get("AT2 (C)"), "wind_composite": w.ws,
             "PM2.5": d.get("PM2.5 (ug/m3)")}
    if s == "AMS 5":
        vars_["S_T90_minus_T20"] = d["AT90 (C)"] - d["AT20 (C)"]
    if "AT_Delta (C)" in d:
        vars_["dT_10m_minus_2m"] = d["AT_Delta (C)"]
    for v, x in vars_.items():
        if x is None: continue
        for y, g in x.groupby(x.index.year):
            rows.append(dict(station=s, variable=v, year=y, pct_valid=round(100 * g.notna().mean(), 1)))
q1 = pd.DataFrame(rows).pivot_table(index=["station", "variable"], columns="year", values="pct_valid").reset_index()
q1.to_csv(RES / "q1_variable_completeness_station_year.csv", index=False)

# ---------------------------------------------------------------- Q2 monthly operational completeness (AMD DQ 4-C)
qa = TK.isin(["Z", "C", "SP"])
m_all = CH.notna().groupby(idx.to_period("M")).mean()
m_exqa = (CH.notna().groupby(idx.to_period("M")).sum() / (~qa).groupby(idx.to_period("M")).sum())
q2 = pd.DataFrame({"station": np.repeat(ST, len(m_all)), "month": np.tile(m_all.index.astype(str), len(ST)),
                   "pct_valid_all_hours": np.concatenate([100 * m_all[s].values for s in ST]),
                   "pct_valid_excl_QA": np.concatenate([100 * m_exqa[s].values for s in ST])}).round(1)
q2["below_90_excl_QA"] = q2.pct_valid_excl_QA < 90; q2["below_75_all_hours"] = q2.pct_valid_all_hours < 75
q2.to_csv(RES / "q2_monthly_completeness.csv", index=False)
q2s = q2.groupby("station").agg(months=("month", "size"), below_90_excl_QA=("below_90_excl_QA", "sum"),
                                below_75_all_hours=("below_75_all_hours", "sum")).reset_index()
q2s.to_csv(RES / "q2_monthly_completeness_summary.csv", index=False)

# ---------------------------------------------------------------- Q3 gap structure
hours = idx.hour
tok_hour = pd.DataFrame({t: (TK == t).sum(1).groupby(hours).sum() / (len(ST) * pd.Series(hours).value_counts().sort_index().values)
                         for t in ["Z", "C", ".", "SP"]})
tok_hour["any_missing"] = CH.isna().sum(1).groupby(hours).sum().values / (len(ST) * pd.Series(hours).value_counts().sort_index().values)
(100 * tok_hour).round(2).to_csv(RES / "q3_missing_share_by_hour_pct.csv")
zsim = (TK == "Z").sum(1); missim = CH.isna().sum(1)
q3b = pd.DataFrame({"n_stations": range(0, 13),
                    "hours_with_n_stations_in_Z": [int((zsim == k).sum()) for k in range(13)],
                    "hours_with_n_stations_missing_CH4": [int((missim == k).sum()) for k in range(13)]})
q3b.to_csv(RES / "q3_simultaneity.csv", index=False)
runs = []
for s in ST:
    m = CH[s].isna(); g = (m != m.shift()).cumsum(); r = m.groupby(g).agg(["first", "size"]); r = r[r["first"]]["size"]
    runs.append(dict(station=s, gaps=len(r), single_hour=int((r == 1).sum()), h2_6=int(r.between(2, 6).sum()),
                     h7_48=int(r.between(7, 48).sum()), longer_48=int((r > 48).sum()), longest_h=int(r.max())))
pd.DataFrame(runs).to_csv(RES / "q3_gap_run_lengths.csv", index=False)

# ---------------------------------------------------------------- Q4 ignorability of Z given hour (and month)
# For each station: CH4 at t-1 and t+1 around a Z hour vs CH4 at t-1/t+1 for non-Z hours with same hour-of-day and month.
blk = block_ids(idx, CFG["bootstrap"]["block_days"]); q4 = []
for s in ST:
    z = (TK[s] == "Z"); prev = CH[s].shift(1); nxt = CH[s].shift(-1)
    bracket = (prev + nxt) / 2
    key = pd.Series(idx.hour * 100 + idx.month, index=idx)
    ref = bracket[~z & CH[s].notna()].groupby(key[~z & CH[s].notna()]).mean()
    diff = (bracket - key.map(ref))[z].dropna()
    db = blk[np.isin(idx, diff.index)]
    bs = [diff.iloc[ix].mean() for ix in block_bootstrap_indices(db, 1000, rng)]
    lo, hi = pct_ci(bs)
    q4.append(dict(station=s, z_hours_with_bracket=len(diff), mean_diff_ppm=round(diff.mean(), 4),
                   ci_lo=round(lo, 4), ci_hi=round(hi, 4)))
q4 = pd.DataFrame(q4); q4.to_csv(RES / "q4_z_ignorability.csv", index=False)

# ---------------------------------------------------------------- Q5 usable hours for H1
S = P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"]; U5 = composite(P["AMS 5"]).ws
core = CFG["stations"]["h1_core_response"]; exp_ = CFG["stations"]["h1_expanded_response"]
q5 = pd.DataFrame([
    dict(rule="core: >=5 of 7 (v2.0 set), S and U5 valid",
         hours=int((CH[core].notna().sum(1).ge(CFG["stations"]["h1_core_kmin"]) & S.notna() & U5.notna()).sum())),
    dict(rule="expanded: >=8 of 11, S and U5 valid",
         hours=int((CH[exp_].notna().sum(1).ge(8) & S.notna() & U5.notna()).sum())),
    dict(rule="total development hours", hours=len(idx))])
q5.to_csv(RES / "q5_h1_usable_hours.csv", index=False)

# ---------------------------------------------------------------- NMHC censoring
nm = pd.DataFrame({s: P[s]["NMHC (ppm)"] for s in ST})
pd.DataFrame({"station": ST, "pct_NMHC_exactly_zero_of_valid": [round(100 * (nm[s] == 0).sum() / nm[s].notna().sum(), 1) for s in ST]}) \
    .to_csv(RES / "nmhc_zero_share.csv", index=False)

# ---------------------------------------------------------------- Figure 2 (main): coverage and gap timing
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={"width_ratios": [2.3, 1]})
mm = (100 * m_all[ST]).T
im = ax[0].imshow(mm.values, aspect="auto", cmap="viridis", vmin=50, vmax=100, interpolation="none")
ax[0].set_yticks(range(len(ST)), ST); xt = [i for i, p in enumerate(mm.columns) if p.month == 1]
ax[0].set_xticks(xt, [str(mm.columns[i].year) for i in xt]); ax[0].set_title("a  Valid CH$_4$ hours per station-month (%)")
cb = fig.colorbar(im, ax=ax[0], orientation="horizontal", fraction=0.05, pad=0.12, aspect=40); cb.set_label("Valid hours (%)")
fig.subplots_adjust(wspace=0.35)
for t, c in [("Z", "C3"), (".", "C0"), ("C", "C2")]:
    ax[1].plot(range(24), 100 * tok_hour[t].values, marker="o", ms=2.5, color=c, label=f"'{t}'")
ax[1].set_xlabel("Hour ending (MST)"); ax[1].set_ylabel("Share of station-hours (%)"); ax[1].set_xticks(range(0, 24, 6))
ax[1].set_title("b  Missing CH$_4$ by code and hour"); ax[1].legend(frameon=False)
fig.text(0.01, -0.04, f"12 WBEA stations, 2021-01-01 to 2025-12-02 (development data); n = {len(idx):,} hours per station. "
         "Codes as exported; meanings of Z and '.' not yet confirmed by WBEA.", fontsize=6.5)
save(fig, FIG / "figure02_coverage_and_gap_timing")
runmeta.write(EXP, dict(experiment="E02_data_quality", status="exploratory", seed_used=CFG["project"]["seed"] + 2))
print(q2s.to_string(index=False)); print(q3b.head(6).to_string(index=False)); print(pd.DataFrame(runs).to_string(index=False))
print(q4.to_string(index=False)); print(q5.to_string(index=False)); print((100 * tok_hour).round(2).loc[[0, 2, 4, 6, 12, 18]])
