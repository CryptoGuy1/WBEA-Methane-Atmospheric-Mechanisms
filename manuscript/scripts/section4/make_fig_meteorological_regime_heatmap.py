"""Meteorological-regime heatmap of observed methane-excursion frequency (development period, descriptive). PLOTTING ONLY.
Source (authoritative, read-only): experiments/E03_excursion_patterns/results/q4_regime_table.csv
  regime = stability tercile | wind class | solar regime; rate_pct = 100 x excursions / valid station-hours.
  Classification per run_e03.py lines 77-93: AMS 5 T90 - T20 terciles (2021-2023 cut points, stability_tercile_cutpoints_degC.csv),
  station composite wind classes (<1, 1-2.5, >=2.5 m/s), night = solar elevation <= 0; hours need valid CH4, stability and wind.
Unadjusted descriptive frequencies; not causal effects and not emission rates. Each cell is mapped by name from its source row."""
import sys, json, pathlib, colorsys, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "section2"))
import common
from common import plt, MM
import matplotlib as mpl
ROOT = common.ROOT; OUT = ROOT / "manuscript/figures/section4"
T = pd.read_csv(ROOT / "experiments/E03_excursion_patterns/results/q4_regime_table.csv").set_index("regime")
STAB, WIND, SOL = ["unstable", "neutral", "stable"], ["<1", "1-2.5", ">=2.5"], ["day", "night"]
assert len(T) == 18 and set(T.index) == {f"{s}|{w}|{d}" for s in STAB for w in WIND for d in SOL}
assert ((100 * T.excursions / T.hours) - T.rate_pct).abs().max() <= 0.005                       # rate = excursions / hours (2-dp)
M = {d: np.array([[T.loc[f"{s}|{w}|{d}", "rate_pct"] for w in WIND] for s in STAB]) for d in SOL}   # rows: unstable, neutral, stable
checks = {("stable", "<1", "day"): 18.28, ("stable", "<1", "night"): 15.59, ("unstable", ">=2.5", "day"): 0.57,
          ("unstable", ">=2.5", "night"): 1.64, ("neutral", "<1", "day"): 9.89, ("neutral", "<1", "night"): 8.90}
for (s, w, d), v in checks.items(): assert M[d][STAB.index(s), WIND.index(w)] == v == T.loc[f"{s}|{w}|{d}", "rate_pct"]
VMIN, VMAX = float(T.rate_pct.min()), float(T.rate_pct.max()); assert (VMIN, VMAX) == (0.57, 18.28)
(OUT / "fig_meteorological_regime_heatmap_values.json").write_text(json.dumps({d: M[d].tolist() for d in SOL} | {"rows": STAB, "cols": WIND, "vmin": VMIN, "vmax": VMAX}))

cmap = mpl.colormaps["cividis"]; norm = mpl.colors.Normalize(VMIN, VMAX)
def _lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def text_color(v):                                                      # pick the text colour with the higher WCAG contrast ratio
    r, g, b, _ = cmap(norm(v)); L = 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)
    return "#111111" if (L + 0.05) / (0.0067 + 0.05) >= 4.0 else "white"           # dark wherever it reaches >= 4:1 (consistent across the grey mid-range)
W, H = 174.5, 83.0
fig = plt.figure(figsize=(W * MM, H * MM))
PH = 0.72; PW = PH * H / W; B0 = 0.15
ax_a = fig.add_axes([0.12, B0, PW, PH]); ax_b = fig.add_axes([0.12 + PW + 0.035, B0, PW, PH])
cax = fig.add_axes([0.12 + 2 * PW + 0.06, B0, 0.016, PH])
for ax, d, lab, desc in ((ax_a, "day", "(a)", "Daytime"), (ax_b, "night", "(b)", "Nighttime")):
    for i in range(3):                                                      # vector cells (no embedded bitmap)
        for j in range(3): ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fc=cmap(norm(M[d][i, j])), ec="none", zorder=1))
    ax.set_xlim(-0.5, 2.5); ax.set_ylim(2.5, -0.5); ax.set_aspect("equal")
    for i in range(3):
        for j in range(3):
            v = M[d][i, j]; ax.text(j, i, f"{v:.1f}%", ha="center", va="center", fontsize=7.2, color=text_color(v))
    ax.set_xticks(range(3), ["<1", "1–2.5", "≥2.5"]); ax.set_yticks(range(3), ["Unstable", "Neutral", "Stable"] if d == "day" else [])
    ax.set_xticks(np.arange(-0.5, 3), minor=True); ax.set_yticks(np.arange(-0.5, 3), minor=True)
    ax.grid(which="minor", color="white", lw=1.6, zorder=2); ax.set_axisbelow(False); ax.tick_params(which="both", length=0, labelsize=7)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.text(-0.02, 1.03, lab, transform=ax.transAxes, fontsize=8, fontweight="bold", ha="right", va="bottom")
    ax.text(0.5, 1.03, desc, transform=ax.transAxes, fontsize=6.8, color="#4d4d4d", ha="center", va="bottom", style="italic")
fig.text(0.12 + PW + 0.0175, 0.025, "Wind speed (m s$^{-1}$)", ha="center", va="bottom", fontsize=7.5)
fig.text(0.012, B0 + PH / 2, "Atmospheric stability", rotation=90, ha="left", va="center", fontsize=7.5)
lev = np.linspace(VMIN, VMAX, 257)                                         # vector colour bar: 256 filled segments
for k in range(256): cax.add_patch(plt.Rectangle((0, lev[k]), 1, lev[k + 1] - lev[k], fc=cmap(norm(0.5 * (lev[k] + lev[k + 1]))), ec=cmap(norm(0.5 * (lev[k] + lev[k + 1]))), lw=0.2))
cax.set_xlim(0, 1); cax.set_ylim(VMIN, VMAX); cax.set_xticks([]); cax.yaxis.tick_right(); cax.yaxis.set_label_position("right")
cax.set_yticks([1, 5, 10, 15]); cax.tick_params(labelsize=6.5, length=2, width=0.5)
for sp in cax.spines.values(): sp.set_visible(False)
cax.set_ylabel("Methane-excursion frequency (%)", fontsize=7)
for ext in ("pdf", "svg"):
    fig.savefig(OUT / f"fig_meteorological_regime_heatmap.{ext}", metadata={"Date": None} if ext == "svg" else {"CreationDate": None})
fig.savefig(OUT / "fig_meteorological_regime_heatmap.png", dpi=600)
fig.savefig(OUT / "fig_meteorological_regime_heatmap.tiff", dpi=600, pil_kwargs={"compression": "tiff_lzw"})
print("written", W, "x", H, "mm")
