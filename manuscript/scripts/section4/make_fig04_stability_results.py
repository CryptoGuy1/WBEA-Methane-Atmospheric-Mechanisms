"""Fig. 4 - Atmospheric stability and regional methane variability. PLOTTING ONLY: reads saved results, refits nothing.
Sources (all read-only):
  (a) experiments/E04_stability_elasticity/results/h1_functional_form.csv   (saved linear and piecewise-linear spline effects)
      The original partial-residual hexbin and quantile-bin means were computed at plot time and NOT saved; they are
      not reproduced here (see manuscript/figures/section4/FIG04_VERIFICATION.md for the proposed extraction).
  (b) experiments/E04_stability_elasticity/results/h1_estimates.csv          (annual 2021-2025 and pooled development)
      experiments/E08_confirmation/confirmation_2026/e08_results.json         (registered 2026 estimate)
  (c) h1_estimates.csv (development joint negative-control model) and e08_results.json (2026 joint model).
      The 2026 contemporaneous joint coefficient has no saved interval and is drawn as a point only."""
import sys, json, pathlib, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "section2"))
import common
from common import plt, MM
ROOT = common.ROOT; OUT = ROOT / "manuscript/figures/section4"; OUT.mkdir(parents=True, exist_ok=True)
E04 = ROOT / "experiments/E04_stability_elasticity/results"; E08 = ROOT / "experiments/E08_confirmation/confirmation_2026/e08_results.json"
C_DEV, C_CONF, C_LIN, C_SPL, C_GRID = "#4d4d4d", "#2171b5", "#252525", "#d95f02", "#d9d9d9"

# ------------------------------------------------ load and verify source values
est = pd.read_csv(E04 / "h1_estimates.csv").set_index("label"); ff = pd.read_csv(E04 / "h1_functional_form.csv")
h1 = json.loads(E08.read_text())["H1"]
dev = est.loc["Direct (with log wind)"]; years = [est.loc[f"Direct, {y}"] for y in range(2021, 2026)]
nc_dev = est.loc["Negative control: coefficient on S(t+24), given S(t)"]; jt_dev = est.loc["Coefficient on S(t) in the negative-control model"]
expected = {"dev": (0.04752, 0.04106, 0.05203), "2021": (0.05859, 0.0455, 0.0694), "2022": (0.03724, 0.02895, 0.04718), "2023": (0.04418, 0.03349, 0.05142),
            "2024": (0.05082, 0.03683, 0.06556), "2025": (0.04851, 0.03435, 0.06367), "nc_dev": (-4e-05, -0.00477, 0.00264), "jt_dev": (0.04747, 0.0414, 0.0523)}
got = {"dev": dev, **{str(y): r for y, r in zip(range(2021, 2026), years)}, "nc_dev": nc_dev, "jt_dev": jt_dev}
for k, (e, lo, hi) in expected.items():
    r = got[k]; assert (r.estimate, r.ci_lo, r.ci_hi) == (e, lo, hi), (k, r.estimate, r.ci_lo, r.ci_hi)
assert abs(h1["b1_primary"] - 0.05203865514163186) < 1e-15 and abs(h1["b_nc"] - (-0.018721921849912438)) < 1e-15 and abs(h1["b1_joint"] - 0.054621589756653266) < 1e-15
assert abs(ff.linear_effect_ppm.iloc[-1] / ff.S_sd.iloc[-1] - dev.estimate) < 1e-3          # saved linear curve has slope = pooled estimate

fig = plt.figure(figsize=(174.5 * MM, 64.0 * MM))
ax_a = fig.add_axes([0.085, 0.20, 0.245, 0.72]); ax_b = fig.add_axes([0.445, 0.20, 0.225, 0.72]); ax_c = fig.add_axes([0.762, 0.20, 0.205, 0.72])
for a, l in ((ax_a, "(a)"), (ax_b, "(b)"), (ax_c, "(c)")):
    a.text(-0.02, 1.02, l, transform=a.transAxes, fontsize=8, fontweight="bold", ha="right", va="bottom")
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
    a.tick_params(length=2.5, width=0.5)

# ------------------------------------------------ (a) saved functional-form curves
ax_a.axhline(0, c=C_GRID, lw=0.6, zorder=0); ax_a.axvline(0, c=C_GRID, lw=0.6, zorder=0)
ax_a.plot(ff.S_sd, ff.linear_effect_ppm, c=C_LIN, lw=1.0, ls=(0, (4, 2)), label=f"Linear ({dev.estimate:.3f} ppm per SD)")
ax_a.plot(ff.S_sd, ff.spline_effect_ppm, c=C_SPL, lw=1.3, label="Piecewise-linear spline")
ax_a.set_xlabel("Stability, $Z_S$ (reference SD)"); ax_a.set_ylabel("Adjusted effect on CH$_4$ anomaly (ppm)")
ax_a.set_xlim(-1.5, 3.5); ax_a.legend(frameon=False, loc="upper left", fontsize=6.3, handlelength=2.2)

# ------------------------------------------------ (b) annual, pooled development, 2026 confirmation
rows = [(str(y), r.estimate, r.ci_lo, r.ci_hi, C_DEV, "o", 3.4) for y, r in zip(range(2021, 2026), years)]
rows += [("2021–2025", dev.estimate, dev.ci_lo, dev.ci_hi, C_DEV, "D", 4.0), ("2026", h1["b1_primary"], *h1["b1_primary_ci"], C_CONF, "D", 4.4)]
ypos = [7.4, 6.4, 5.4, 4.4, 3.4, 1.9, 0.6]
ax_b.axvline(0, c=C_GRID, lw=0.6, zorder=0); ax_b.axvspan(dev.ci_lo, dev.ci_hi, color="#efefef", zorder=0, lw=0)
for (lab, e, lo, hi, c, m, ms), y in zip(rows, ypos):
    ax_b.plot([lo, hi], [y, y], c=c, lw=1.1, solid_capstyle="butt"); ax_b.plot(e, y, m, c=c, ms=ms, mec=c)
ax_b.set_yticks(ypos, [r[0] for r in rows]); ax_b.set_ylim(-0.2, 8.2); ax_b.set_xlim(0, 0.08)
for t, (lab, *_rest) in zip(ax_b.get_yticklabels(), rows):
    if lab == "2026": t.set_color(C_CONF); t.set_fontweight("bold")
    if lab == "2021–2025": t.set_fontweight("bold")
ax_b.axhline(2.65, c="#bdbdbd", lw=0.5, ls=(0, (2, 2))); ax_b.axhline(1.25, c="#bdbdbd", lw=0.5, ls=(0, (2, 2)))
ax_b.text(0.079, 7.95, "Development years", fontsize=6.0, color=C_DEV, ha="right", va="center")
ax_b.text(0.079, 2.25, "Pooled development", fontsize=6.0, color=C_DEV, ha="right", va="center")
ax_b.text(0.079, 1.0, "Independent confirmation", fontsize=6.0, color=C_CONF, ha="right", va="center")
ax_b.set_xlabel(r"$\hat\beta_S$ (ppm per reference SD; 95% CI)"); ax_b.tick_params(axis="y", length=0)

# ------------------------------------------------ (c) joint negative-control model: next-day vs contemporaneous coefficient
ax_c.axvline(0, c=C_GRID, lw=0.6, zorder=0)
groups = [("2021–2025", 2.3, C_DEV, nc_dev.estimate, nc_dev.ci_lo, nc_dev.ci_hi, jt_dev.estimate, (jt_dev.ci_lo, jt_dev.ci_hi)),
          ("2026", 0.8, C_CONF, h1["b_nc"], *h1["b_nc_ci"], h1["b1_joint"], None)]
for lab, y, c, ne, nlo, nhi, je, jci in groups:
    yn, yj = y + 0.30, y - 0.30
    ax_c.plot([nlo, nhi], [yn, yn], c=c, lw=1.1, solid_capstyle="butt"); ax_c.plot(ne, yn, "o", c=c, ms=3.8, mec=c)
    if jci is not None: ax_c.plot(jci, [yj, yj], c=c, lw=1.1, solid_capstyle="butt")
    ax_c.plot(je, yj, "D", ms=3.8, mfc="white", mec=c, mew=1.0)
    thr = -0.5 * je; ax_c.plot([thr, thr], [yn - 0.22, yn + 0.22], c=c, lw=0.9, ls=(0, (1.2, 1.2)))
ax_c.set_yticks([2.3, 0.8], ["2021–2025", "2026"]); ax_c.set_ylim(-0.2, 4.6); ax_c.set_xlim(-0.035, 0.07)
ax_c.get_yticklabels()[1].set_color(C_CONF); ax_c.get_yticklabels()[1].set_fontweight("bold"); ax_c.tick_params(axis="y", length=0)
ax_c.set_xlabel("Joint-model coefficient (ppm per SD)")
h = [plt.Line2D([], [], c="#555555", marker="o", ms=3.8, lw=1.1, label="Next-day, $Z_S(t+24)$ (95% CI)"),
     plt.Line2D([], [], c="#555555", marker="D", ms=3.8, mfc="white", lw=1.1, label="Contemporaneous, $Z_S(t)$"),
     plt.Line2D([], [], c="#555555", lw=0.9, ls=(0, (1.2, 1.2)), label="$-0.5\\times$ contemporaneous")]
ax_c.legend(handles=h, frameon=False, loc="upper left", fontsize=5.9, handlelength=1.8, borderaxespad=0.0, labelspacing=0.35)

for ext in ("pdf", "svg"):
    fig.savefig(OUT / f"fig04_stability_results.{ext}", metadata={"Date": None} if ext == "svg" else {"CreationDate": None})
fig.savefig(OUT / "fig04_stability_results_600dpi.png", dpi=600)
fig.savefig(OUT / "fig04_stability_results_600dpi.tiff", dpi=600, pil_kwargs={"compression": "tiff_lzw"})
print("fig04 written: 174.5 x 64.0 mm")
