"""Redraw E05 Figures 6 and 8 from saved result tables (no re-analysis)."""
import sys, pathlib, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(EXP.parents[1] / "src"))
from wbea.plotstyle import plt, save
RES = EXP / "results"; FIG = EXP / "figures"
prim = pd.read_csv(RES / "h2_pair_statistics.csv"); null = pd.read_csv(RES / "h2_null_distribution.csv.gz").values
pool = pd.read_csv(RES / "h2_pooled.csv").iloc[0]; modes = pd.read_csv(RES / "h2_residualisation_comparison.csv")
prec = 1 / prim.null_sd ** 2; pooled_null = null @ prec.values / prec.sum(); NS = len(null)
o = prim.sort_values("km")

fig = plt.figure(figsize=(7.4, 3.4)); gs = fig.add_gridspec(1, 2, width_ratios=[2.1, 1], wspace=0.3)
ax = fig.add_subplot(gs[0, 0])
ax.fill_between(o.km, np.percentile(null, 2.5, 0)[o.index], np.percentile(null, 97.5, 0)[o.index],
                color="0.88", step="mid", label="wind-shift null, 95% range")
sc = ax.scatter(o.km, o.D, c=o.median_tau, cmap="viridis", s=22, zorder=3)
ax.vlines(o.km, o.ci_lo, o.ci_hi, color="0.4", lw=0.7, zorder=2); ax.axhline(0, c="0.6", lw=0.6)
for _, r in o[o.p_maxT_familywise < 0.05].iterrows():
    ax.annotate("*", (r.km, r.ci_hi), ha="center", fontsize=8)
cb = fig.colorbar(sc, ax=ax, orientation="horizontal", fraction=0.06, pad=0.2, aspect=35)
cb.set_label("median predicted transit time (h)")
ax.set_xlabel("Station separation (km)"); ax.set_ylabel("Directional contrast D (lags 1-3)")
ax.set_title("a  27 pairs (* family-wise p < 0.05, max-T)"); ax.legend(fontsize=6, frameon=False, loc="upper right")
b = fig.add_subplot(gs[0, 1])
b.hist(pooled_null, bins=40, color="0.7"); b.axvline(pool.pooled_D, c="C3", lw=1.5)
b.set_xlabel("Pooled D"); b.set_ylabel("Wind-shift replicates")
b.set_title(f"b  Pooled D = {pool.pooled_D:.3f}; p <= {1 / (NS + 1):.3f}")
fig.text(0.01, -0.04, "Leave-pair-out residual CH$_4$ changes; aligned minus reversed flow; null from 1,000 whole-day wind shifts "
         "(p floor 1/1,001); bars: 14-day joint block bootstrap 95% CI. Development data 2021-2025.", fontsize=6.2)
save(fig, FIG / "figure06_directional_coupling")

fig, ax = plt.subplots(figsize=(6.8, 3.2)); xs = np.arange(len(o))
for k, (lab, col) in enumerate([("no common-mode removal", "0.6"), ("leave-one-out common mode", "C1"),
                                ("leave-pair-out (primary)", "k"), ("leave-pair-out, AMS 14/18 excluded", "C0")]):
    ax.plot(xs + (k - 1.5) * 0.18, modes.loc[o.index, lab], "o", ms=3, c=col, label=lab)
ax.axhline(0, c="0.6", lw=0.6)
ax.set_xticks(xs, [p.replace("AMS ", "").replace("->", "-") for p in o.pair], rotation=90, fontsize=6)
ax.set_ylabel("Directional contrast D"); ax.set_xlabel("Station pair (ordered by separation, 2.7-27.3 km)")
ax.legend(fontsize=6, frameon=False, ncol=2); ax.set_title("Directional signal under four definitions of the regional component")
save(fig, FIG / "figure08_residualisation_sensitivity")
print("figures redrawn")
