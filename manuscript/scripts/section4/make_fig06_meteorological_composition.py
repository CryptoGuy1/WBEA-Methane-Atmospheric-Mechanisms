"""Fig. 6 - Meteorological-regime composition of methane-excursion changes. PLOTTING ONLY (no H3 rerun).
Sources (read-only):
 (a) experiments/E07_composition_decomposition/results/h3_contrasts_primary.csv  (120 development contrasts; later minus earlier year)
 (b) experiments/E08_confirmation/confirmation_2026/h3_contrasts.csv            (55 confirmation contrasts; 2026 minus development year)
 (c) experiments/E08_post_confirmation_exploratory/results/h3_2026_denominator_by_station.csv (post-confirmation exploratory)
 Checks: e08_results.json, descriptive_results.json, h3_sensitivity.csv, PRE_E08 h3_jan_sep_benchmark.csv, h3_weight_concentration.json.
Fractional rate changes are multiplied by 100 to give percentage points (pp). t = c + w (Kitagawa identity, wbea.e08.kitagawa_groups)."""
import sys, json, pathlib, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "section2"))
import common
from common import plt, MM
ROOT = common.ROOT; OUT = ROOT / "manuscript/figures/section4"; E = ROOT / "experiments"; C = E / "E08_confirmation/confirmation_2026"
C_DEV, C_CONF, C_A18, C_GRID = "#4d4d4d", "#2171b5", "#d95f02", "#d9d9d9"

# ------------------------------------------------ load and verify
dv = pd.read_csv(E / "E07_composition_decomposition/results/h3_contrasts_primary.csv")
cf = pd.read_csv(C / "h3_contrasts.csv"); den = pd.read_csv(E / "E08_post_confirmation_exploratory/results/h3_2026_denominator_by_station.csv")
sens = pd.read_csv(E / "E07_composition_decomposition/results/h3_sensitivity.csv").set_index("analysis")
bench = pd.read_csv(E / "PRE_E08/results/h3_jan_sep_benchmark.csv").set_index("version")
h3 = json.loads((C / "e08_results.json").read_text())["H3"]; ds = json.loads((C / "descriptive/descriptive_results.json").read_text())["h3_descriptive"]
wc = json.loads((E / "E08_post_confirmation_exploratory/results/h3_weight_concentration.json").read_text())
assert len(dv) == 120 and len(cf) == 55 and cf.estimable.all() and h3["contrasts_estimable"] == 55 and (cf.station == "AMS 18").sum() == 5
for d in (dv, cf): assert (d.composition + d.within - d.total).abs().max() <= 1.5e-6        # identity within 6-dp rounding
assert round(100 * dv.composition.abs().mean(), 2) == 0.45 and round(100 * dv.within.abs().mean(), 2) == 1.61
pr = sens.loc["Primary (raw P95, Jan-Nov, 2021-2025)"]; assert (pr.share, pr.ci_lo, pr.ci_hi) == (0.0269, -0.0396, 0.1264)
js = bench.loc["E07-r3 (Jan-Sep, D-54)"]; assert (js.share, js.ci_lo, js.ci_hi) == (0.0261, -0.0284, 0.1238)
assert round(h3["share"], 4) == 0.0110 and round(h3["ci_lo"], 4) == -0.0199 and round(h3["ci_hi"], 4) == 0.0428
assert round(ds["share_6_regimes"], 4) == 0.0123 and [round(v, 4) for v in ds["ci_6_regimes"]] == [-0.0214, 0.0416]
t2 = (cf.total ** 2).groupby(cf.station).sum(); shr = t2 / t2.sum()
den = den.sort_values("denominator_share", ascending=True)
assert len(den) == 11 and (den.set_index("station").denominator_share - shr).abs().max() < 1e-5
assert round(wc["AMS18_denominator_share_2026"], 4) == 0.9293 and round(wc["AMS18_denominator_share_development_JanSep"], 4) == 0.3905
assert round(wc["share_excluding_AMS18_point"], 4) == -0.0852
pp = lambda s: 100 * s

fig = plt.figure(figsize=(174.5 * MM, 132.0 * MM))
ax_a = fig.add_axes([0.085, 0.47, 0.36, 0.49]); ax_b = fig.add_axes([0.58, 0.47, 0.36, 0.49]); ax_c = fig.add_axes([0.085, 0.085, 0.855, 0.26])
for a, l in ((ax_a, "(a)"), (ax_b, "(b)"), (ax_c, "(c)")):
    a.text(-0.02, 1.02, l, transform=a.transAxes, fontsize=8, fontweight="bold", ha="right", va="bottom")
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
    a.tick_params(length=2.5, width=0.5)
XLAB, YLAB = "Composition contribution, $c$ (pp)", "Within-regime contribution, $w$ (pp)"
# (a) development: equal scales on both axes to show relative magnitudes
ax_a.axhline(0, c=C_GRID, lw=0.6, zorder=0); ax_a.axvline(0, c=C_GRID, lw=0.6, zorder=0)
ax_a.scatter(pp(dv.composition), pp(dv.within), s=11, c=C_DEV, alpha=0.5, lw=0, zorder=2)
ax_a.set_xlim(-10, 10); ax_a.set_ylim(-10, 10); ax_a.set_aspect("equal", adjustable="box")
ax_a.set_xlabel(XLAB); ax_a.set_ylabel(YLAB)
# (b) 2026: same x scale; AMS 18 distinguished; inset reuses the other 50 contrasts
oth, a18 = cf[cf.station != "AMS 18"], cf[cf.station == "AMS 18"]
ax_b.axhline(0, c=C_GRID, lw=0.6, zorder=0); ax_b.axvline(0, c=C_GRID, lw=0.6, zorder=0)
ax_b.scatter(pp(oth.composition), pp(oth.within), s=11, c=C_CONF, alpha=0.6, lw=0, zorder=2, label="Other stations (50)")
ax_b.scatter(pp(a18.composition), pp(a18.within), s=16, marker="D", c=C_A18, alpha=0.85, lw=0, zorder=3, label="AMS 18 (5)")
ax_b.set_xlim(-10, 10); ax_b.set_ylim(-10, 50); ax_b.set_xlabel(XLAB); ax_b.set_ylabel(YLAB)
ax_b.legend(frameon=False, loc="lower right", fontsize=6.2, handletextpad=0.3, borderaxespad=0.3)
XI, YI = (-2.5, 1.5), (-6.0, 12.5)
ins = ax_b.inset_axes([0.12, 0.43, 0.30, 0.42])
ins.axhline(0, c=C_GRID, lw=0.5, zorder=0); ins.axvline(0, c=C_GRID, lw=0.5, zorder=0)
ins.scatter(pp(oth.composition), pp(oth.within), s=7, c=C_CONF, alpha=0.6, lw=0)
ins.set_xlim(*XI); ins.set_ylim(*YI); ins.tick_params(labelsize=5.6, length=2, width=0.4, pad=1)
for sp in ins.spines.values(): sp.set_linewidth(0.5)
ax_b.add_patch(plt.Rectangle((XI[0], YI[0]), XI[1] - XI[0], YI[1] - YI[0], fill=False, ec="#8c8c8c", lw=0.5, ls=(0, (2, 1.5)), zorder=1))
assert oth.composition.between(XI[0] / 100, XI[1] / 100).all() and oth.within.between(YI[0] / 100, YI[1] / 100).all()   # inset shows all 50
# (c) post-confirmation diagnostic: station share of the 2026 estimator denominator
cols = [C_A18 if s == "AMS 18" else "#9ecae1" for s in den.station]
ax_c.barh(np.arange(11), 100 * den.denominator_share, color=cols, height=0.7, lw=0)
for k, v in enumerate(100 * den.denominator_share):
    ax_c.text(v + 0.8, k, f"{v:.1f}%" if v >= 1 else f"{v:.2f}%", va="center", fontsize=5.9, color=C_A18 if den.station.iloc[k] == "AMS 18" else "#3a3a3a",
              fontweight="bold" if den.station.iloc[k] == "AMS 18" else "normal")
ax_c.set_yticks(np.arange(11), den.station); ax_c.tick_params(axis="y", length=0, labelsize=6.2)
ax_c.set_xlim(0, 100); ax_c.set_xlabel(r"Share of the 2026 estimator denominator $\sum_k t_k^2$ (%; post-confirmation diagnostic)")
for ext in ("pdf", "svg"):
    fig.savefig(OUT / f"fig06_meteorological_composition.{ext}", metadata={"Date": None} if ext == "svg" else {"CreationDate": None})
fig.savefig(OUT / "fig06_meteorological_composition.png", dpi=600)
fig.savefig(OUT / "fig06_meteorological_composition.tiff", dpi=600, pil_kwargs={"compression": "tiff_lzw"})
print("fig06 written 174.5 x 132.0 mm")
