"""E13 figures from saved results only (no recomputation)."""
import sys, pathlib, json, numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE.parents[1] / "src"))
from wbea.plotstyle import plt, save
R = HERE / "results"; F = HERE / "figures"; S = pd.read_csv(R / "e13_summary.csv").set_index("configuration"); C4 = pd.read_csv(R / "e13_per_season.csv").set_index("season")
plt.rcParams.update({"font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8.5, "legend.fontsize": 7})
def panel(ax, sur, obs, K, p, title, xmax):
    ax.hist(sur, bins=np.linspace(-0.2, xmax, 45), color="0.65", edgecolor="white", linewidth=0.3)
    ax.axvline(obs, color="#b2182b", lw=1.6); ax.axvline(0, color="0.3", lw=0.5, ls=":")
    ax.text(obs, ax.get_ylim()[1] * 0.55, f"observed\nD = {obs:.3f} ", color="#b2182b", ha="right", va="top", fontsize=7)
    ax.set_title(title, loc="left")
    ax.text(0.02, 0.95, f"K = {K} surrogates\n0 of {K} >= observed\np = 1/{K + 1} = {p:.4f}", transform=ax.transAxes, va="top", fontsize=6.8)
cfg = [("R0", "R0 frozen whole-period (reproduction)", "a  Frozen E08 reference:\n    whole-period shifts"),
       ("C1-w", "C1-w (season null, own weights)", "b  Exploratory: within\n    calendar quarters (C1)"),
       ("C2-w", "C2-w (season null, own weights)", "c  Exploratory: within\n    cold/warm halves (C2)")]
fig, axs = plt.subplots(1, 3, figsize=(7.4, 3.0), sharey=False)
for ax, (k, row, t) in zip(axs, cfg):
    sur = pd.read_csv(R / f"e13_surrogates_{k}.csv").iloc[:, 0].values; s = S.loc[row]
    panel(ax, sur, s.pooled_D, int(s.K), s.p, t, 0.34)
axs[0].set_ylabel("Number of surrogates")
fig.supxlabel("Pooled directional contrast D (dimensionless)", fontsize=8); fig.tight_layout(); save(fig, F / "e13_fig1_reference_distributions")
fig, axs = plt.subplots(1, 3, figsize=(7.4, 3.0))
for ax, q, lab in zip(axs, ["Jan-Mar", "Apr-Jun", "Jul-Sep"], "abc"):
    sur = pd.read_csv(R / f"e13_surrogates_C4_{q}.csv").iloc[:, 0].values; s = C4.loc[q]
    panel(ax, sur, s.pooled_D, int(s.K), s.p, f"{lab}  {q} 2026, analysed\n    separately ({int(s.pairs)} pairs)", 0.40)
axs[0].set_ylabel("Number of surrogates"); fig.supxlabel("Pooled directional contrast D (dimensionless)", fontsize=8); fig.tight_layout(); save(fig, F / "e13_fig2_per_season")
print("figures written")
