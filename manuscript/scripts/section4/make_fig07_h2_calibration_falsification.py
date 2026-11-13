"""Fig. 7 - Synthetic calibration, detection power and falsification of the directional test. PLOTTING ONLY.
Source (read-only, from the unmerged E12 branch via `git show`, no merge or copy):
  research/e12-h2-null-calibration:experiments/E12_h2_synthetic_null_calibration/results/summary_by_scenario_method.csv
  research/e12-h2-null-calibration:.../results/verdicts.json
Wilson intervals are the saved values; they are re-derived from the saved counts only as a consistency check.
Rates are shown in percent (rate x 100). Internal scenario codes are mapped to descriptive labels (table in FIG07_VERIFICATION.md)."""
import sys, io, json, subprocess, pathlib, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "section2"))
import common
from common import plt, MM
ROOT = common.ROOT; OUT = ROOT / "manuscript/figures/section4"
BR, PATH = "research/e12-h2-null-calibration", "experiments/E12_h2_synthetic_null_calibration/results/"
def gshow(f): return subprocess.run(["git", "-C", str(ROOT), "show", f"{BR}:{PATH}{f}"], capture_output=True, text=True, check=True).stdout
S = pd.read_csv(io.StringIO(gshow("summary_by_scenario_method.csv"))); V = json.loads(gshow("verdicts.json"))
C_NEU, C_ALT, C_FAL, C_POW, C_GRID = "#4d4d4d", "#7f7f7f", "#d95f02", "#2171b5", "#d9d9d9"

def row(sc, m="primary"):
    r = S[(S.scenario == sc) & (S.method == m)]; assert len(r) == 1, (sc, m); return r.iloc[0]
def wilson(k, n, z=1.959963984540054):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return c - h, c + h
for _, r in S.iterrows():                                                     # saved Wilson limits are consistent with the saved counts
    lo, hi = wilson(r.rejections, r.n); assert abs(lo - r.wilson_lo) < 1e-6 and abs(hi - r.wilson_hi) < 1e-6, r.scenario
assert V["total_replicates"] == 4100 and V["total_not_evaluable"] == 0 and V["Q1_null_calibration"] == "inconclusive"
NULLS = [("N0", "Baseline null"), ("N1a", "Wind-independent delayed\ncommon driver"), ("N2a", "Seasonal drift"),
         ("N3", "Strong autocorrelation,\ndiurnal structure, missingness")]
for (sc, _), rate in zip(NULLS, (0.046, 0.054, 0.048, 0.046)): r = row(sc); assert r.role == "Q1 null calibration" and r.rate == rate and r.n == 500
assert abs(row("N1a").wilson_hi - 0.077427) < 1e-6 and V["Q1_by_scenario"] == {"N0": "calibrated", "N1a": "inconclusive", "N2a": "calibrated", "N3": "calibrated"}
SEAS = [("primary", "Whole-period shifts\n(frozen test)"), ("within-season shift", "Within-season shifts\n(exploratory)"), ("truncated shift", "Truncated shifts\n(exploratory)")]
for (m, _), rate in zip(SEAS, (0.238, 0.052, 0.068)): assert row("N2b", m).rate == rate
FAL = [("N1a", "Wind-independent delayed\ncommon driver (null)"), ("N1b", "Wind-advected shared driver,\nno methane transfer")]
assert (row("N1a").rejections, row("N1a").n, row("N1b").rejections, row("N1b").n) == (27, 500, 200, 200)
POW = [("P1_t007", "1h"), ("P1_t013", "1h"), ("P1_ceiling", "1h"), ("P1_L2", "2h"), ("P1_L3", "3h"), ("P1T_t013", "tr"), ("P1T_ceiling", "tr")]
for (sc, _), D, pw in zip(POW, (0.069, 0.131, 0.195, 0.108, -0.040, 0.131, 0.177), (1, 1, 1, 1, 0, 1, 1)):
    r = row(sc); assert r.role == "Q3 power" and round(r.D_q50, 3) == D and r.rate == pw and r.n == 200
CLS = {"calibrated": "calibrated", "inconclusive": "inconclusive", "inflated": "inflated"}

fig = plt.figure(figsize=(174.5 * MM, 118.0 * MM))
axs = [fig.add_axes(p) for p in ([0.215, 0.585, 0.255, 0.375], [0.695, 0.585, 0.215, 0.375], [0.215, 0.09, 0.255, 0.375], [0.695, 0.09, 0.255, 0.375])]
for a, l in zip(axs, "abcd"):
    a.text(-0.02 if l in "bd" else -0.62, 1.03, f"({l})", transform=a.transAxes, fontsize=8, fontweight="bold", ha="right" if l in "bd" else "left", va="bottom")
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
    a.tick_params(length=2.5, width=0.5)
def interval_rows(ax, items, colors, filled, cls=None):
    ys = np.arange(len(items))[::-1]
    for y, (r, c, f) in zip(ys, zip(items, colors, filled)):
        ax.plot([100 * r.wilson_lo, 100 * r.wilson_hi], [y, y], c=c, lw=1.1, solid_capstyle="butt")
        ax.plot(100 * r.rate, y, "o", ms=4.0, c=c, mec=c, mfc=c if f else "white", mew=1.0)
    if cls:
        for y, t in zip(ys, cls): ax.text(1.01, y, t, transform=ax.get_yaxis_transform(), fontsize=5.8, color="#5f5f5f", va="center", ha="left", style="italic")
    ax.set_ylim(-0.6, len(items) - 0.4); ax.tick_params(axis="y", length=0)
    return ys
# (a) statistical-null calibration
ax = axs[0]; rows_a = [row(sc) for sc, _ in NULLS]
ax.axvline(5, c=C_NEU, lw=0.8, zorder=0); ax.axvline(7.5, c=C_ALT, lw=0.7, ls=(0, (2, 2)), zorder=0)
ys = interval_rows(ax, rows_a, [C_NEU] * 4, [True] * 4, [V["Q1_by_scenario"][sc] for sc, _ in NULLS])
ax.set_yticks(ys, [l for _, l in NULLS], fontsize=6.3); ax.set_xlim(0, 10); ax.set_xlabel("Rejection rate (%; Wilson 95% CI)")
ax.text(5, len(NULLS) - 0.45, "5%", ha="center", va="bottom", fontsize=5.8, color=C_NEU); ax.text(7.5, len(NULLS) - 0.45, "7.5% margin", ha="center", va="bottom", fontsize=5.8, color=C_ALT)
# (b) seasonal-confounding vulnerability
ax = axs[1]; rows_b = [row("N2b", m) for m, _ in SEAS]
ax.axvline(5, c=C_NEU, lw=0.8, zorder=0); ax.axvline(7.5, c=C_ALT, lw=0.7, ls=(0, (2, 2)), zorder=0)
ys = interval_rows(ax, rows_b, [C_NEU, C_ALT, C_ALT], [True, False, False], [V["Q2_alternatives"][m] for m, _ in SEAS])
ax.set_yticks(ys, [l for _, l in SEAS], fontsize=6.3); ax.set_xlim(0, 30); ax.set_xlabel("Rejection rate (%; Wilson 95% CI)")
ax.text(5, len(SEAS) - 0.45, "5%", ha="right", va="bottom", fontsize=5.8, color=C_NEU); ax.text(7.5, len(SEAS) - 0.45, "7.5%", ha="left", va="bottom", fontsize=5.8, color=C_ALT)
# (c) physical-specificity falsification
ax = axs[2]; rows_c = [row(sc) for sc, _ in FAL]
ax.axvline(5, c=C_NEU, lw=0.8, zorder=0)
ys = interval_rows(ax, rows_c, [C_NEU, C_FAL], [True, True])
ax.set_yticks(ys, [l for _, l in FAL], fontsize=6.3); ax.set_xlim(0, 104); ax.set_xticks(range(0, 101, 20)); ax.spines["bottom"].set_bounds(0, 100); ax.set_ylim(-0.7, 1.7); ax.set_xlabel("Rejection rate (%; Wilson 95% CI)")
# (d) detection power vs median D (seven discrete configurations; no interpolation)
ax = axs[3]; ax.axhline(0, c=C_GRID, lw=0.5, zorder=0); ax.axvline(0, c=C_GRID, lw=0.5, zorder=0)
mk = {"1h": ("o", "Fixed 1-h lag", True), "2h": ("s", "Fixed 2-h lag", True), "3h": ("v", "Fixed 3-h lag", True), "tr": ("D", "Transit-dependent lag", False)}
done = set()
for sc, kind in POW:
    r = row(sc); m, lab, f = mk[kind]; c = C_FAL if kind == "3h" else C_POW
    ax.plot([r.D_q50] * 2, [100 * r.wilson_lo, 100 * r.wilson_hi], c=c, lw=1.0, zorder=2)
    ax.plot(r.D_q50, 100 * r.rate, m, ms=4.6 if kind != "tr" else 5.6, c=c, mec=c, mfc=c if f else "none", mew=1.0, alpha=0.85 if f else 1, zorder=3 if f else 4,
            label=None if kind in done else lab); done.add(kind)
ax.set_xlim(-0.08, 0.24); ax.set_ylim(-6, 106); ax.set_xlabel("Median pooled statistic $D$ of the configuration"); ax.set_ylabel("Detection power (%; Wilson 95% CI)")
ax.legend(frameon=False, loc="center left", fontsize=6.0, handletextpad=0.4, borderaxespad=0.2, bbox_to_anchor=(0.02, 0.5))
for ext in ("pdf", "svg"):
    fig.savefig(OUT / f"fig07_h2_calibration_falsification.{ext}", metadata={"Date": None} if ext == "svg" else {"CreationDate": None})
fig.savefig(OUT / "fig07_h2_calibration_falsification.png", dpi=600)
fig.savefig(OUT / "fig07_h2_calibration_falsification.tiff", dpi=600, pil_kwargs={"compression": "tiff_lzw"})
print("fig07 written 174.5 x 118.0 mm")
