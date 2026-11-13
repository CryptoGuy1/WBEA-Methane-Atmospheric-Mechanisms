"""Fig. 5 - Wind-conditioned directional coupling and lag diagnostics. PLOTTING ONLY (no new statistics).
Sources (read-only):
 (a) experiments/E05_directional_coupling/results/h2_pair_statistics.csv (D, km, ci_lo/ci_hi, null_p95, p_maxT_familywise), h2_pooled.csv
 (b) experiments/E08_confirmation/confirmation_2026/h2_pairs.csv, h2_Dobs.npy, h2_null_matrix.npy, descriptive/h2_pairs_maxT.csv;
     distances from the E05 pair table (identical pair identifiers and orientation, verified)
 (c) h2_null_matrix.npy (246 shifts x 21 pairs; row k = admissible shift k, column p = h2_pairs.csv row p; run_e08.py lines 64-100)
     pooled with the frozen inverse-null-variance weights (wbea.e08.pooled_inverse_null_variance); the 5-dp CSV weights are checked
 (d) experiments/E06_detectability_kernel/results/e06_observed_vs_reference_kernel.csv (development centroids, range over years,
     signal-dominated A = 3 simulated reference range) and e08_results.json (2026 centroids)."""
import sys, json, pathlib, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "section2"))
import common
from common import plt, MM
from wbea import e08
ROOT = common.ROOT; OUT = ROOT / "manuscript/figures/section4"; E = ROOT / "experiments"; C = E / "E08_confirmation/confirmation_2026"
C_DEV, C_CONF, C_REF, C_NULL, C_GRID = "#4d4d4d", "#2171b5", "#f3c89f", "#9e9e9e", "#d9d9d9"

# ------------------------------------------------ load and verify
d5 = pd.read_csv(E / "E05_directional_coupling/results/h2_pair_statistics.csv"); p5 = pd.read_csv(E / "E05_directional_coupling/results/h2_pooled.csv").iloc[0]
h = pd.read_csv(C / "h2_pairs.csv"); mt = pd.read_csv(C / "descriptive/h2_pairs_maxT.csv"); N = np.load(C / "h2_null_matrix.npy"); Do = np.load(C / "h2_Dobs.npy")
r2 = json.loads((C / "e08_results.json").read_text())["H2"]; kern = pd.read_csv(E / "E06_detectability_kernel/results/e06_observed_vs_reference_kernel.csv")
assert len(d5) == 27 and int((d5.p_maxT_familywise < 0.05).sum()) == 21 == int(p5.pairs_familywise_lt_05)
assert (p5.pooled_D, p5.ci_lo, p5.ci_hi) == (0.1285, 0.1084, 0.15528)
assert N.shape == (246, 21) and len(h) == 21 and list(mt.pair) == list(h.pair) and np.allclose(Do, h.D, atol=5e-6)
assert int((mt.p_maxT_familywise < 0.05).sum()) == 14
pooled, pn, w = e08.pooled_inverse_null_variance(Do, N)
assert np.abs(w - h.weight).max() < 5e-6 and abs(w.sum() - 1) < 1e-12
assert abs(pooled - 0.2879317084641316) < 1e-15 and pooled == r2["pooled_D"] and len(pn) == 246
p_shift = (1 + int((pn >= pooled).sum())) / (len(pn) + 1); assert p_shift == r2["p"] == 1 / 247
km = d5.set_index("pair").km; assert set(h.pair) <= set(km.index)
h["km"] = h.pair.map(km); h["fw"] = mt.p_maxT_familywise.values < 0.05; h["null_p95"] = np.percentile(N, 95, axis=0)
c26 = np.array(r2["centroids"]); assert np.allclose(c26, [0.1295, 0.349, 0.5605, 0.9751, 1.118], atol=5e-5)
assert np.allclose(kern.centroid, [0.2468, 0.3848, 0.7255, 1.1102, 1.5126])
inside = ((kern.centroid >= kern.ref_centroid_min) & (kern.centroid <= kern.ref_centroid_max)).sum(); assert inside == 1

fig = plt.figure(figsize=(174.5 * MM, 122.0 * MM))
axs = [fig.add_axes(p) for p in ([0.075, 0.585, 0.40, 0.375], [0.585, 0.585, 0.40, 0.375], [0.075, 0.085, 0.40, 0.375], [0.585, 0.085, 0.40, 0.375])]
for a, l in zip(axs, "abcd"):
    a.text(-0.02, 1.03, f"({l})", transform=a.transAxes, fontsize=8, fontweight="bold", ha="right", va="bottom")
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
    a.tick_params(length=2.5, width=0.5)
YL = (-0.15, 0.95); XL = (0, 29)

def pair_panel(ax, x, y, fw, color, p95, lo=None, hi=None):
    ax.axhline(0, c=C_GRID, lw=0.6, zorder=0)
    ax.plot(x, p95, "_", c=C_NULL, ms=5.5, mew=1.0, zorder=1)
    if lo is not None: ax.vlines(x, lo, hi, color=color, lw=0.6, alpha=0.75, zorder=2)
    ax.plot(x[fw], y[fw], "o", c=color, ms=3.6, mec=color, zorder=3)
    ax.plot(x[~fw], y[~fw], "o", ms=3.6, mfc="white", mec=color, mew=0.8, zorder=3)
    ax.set_xlim(*XL); ax.set_ylim(*YL); ax.set_xlabel("Station separation (km)"); ax.set_ylabel(r"Pair statistic $D_{ij}$ (dimensionless)")
# (a) development
fwd = d5.p_maxT_familywise.values < 0.05
pair_panel(axs[0], d5.km.values, d5.D.values, fwd, C_DEV, d5.null_p95.values, d5.ci_lo.values, d5.ci_hi.values)
# (b) 2026 (no per-pair bootstrap CIs exist)
pair_panel(axs[1], h.km.values, h.D.values, h.fw.values, C_CONF, h.null_p95.values)
hdl = [plt.Line2D([], [], marker="o", ls="", c="#555555", ms=3.6, label="Family-wise $p<0.05$ (max-$T$)"),
       plt.Line2D([], [], marker="o", ls="", mfc="white", mec="#555555", ms=3.6, label="Not family-wise significant"),
       plt.Line2D([], [], c="#555555", lw=0.6, label="95% block-bootstrap CI (development only)"),
       plt.Line2D([], [], marker="_", ls="", c=C_NULL, ms=5.5, mew=1.0, label="Shifted-wind null, 95th percentile")]
axs[0].legend(handles=hdl, frameon=False, loc="upper right", fontsize=6.0, handlelength=1.4, labelspacing=0.35, borderaxespad=0.1)
axs[0].text(0.98, 0.50, "2021–2025, 27 pairs", transform=axs[0].transAxes, ha="right", fontsize=6.3, color=C_DEV)
axs[1].text(0.98, 0.93, "2026, 21 pairs", transform=axs[1].transAxes, ha="right", fontsize=6.3, color=C_CONF, fontweight="bold")
# (c) 2026 whole-period shifted-wind reference
ax = axs[2]; ax.axvline(0, c=C_GRID, lw=0.6, zorder=0)
ax.hist(pn, bins=np.arange(-0.12, 0.125, 0.01), color="#bdbdbd", ec="white", lw=0.4, zorder=1)
ax.axvline(pooled, c=C_CONF, lw=1.6, zorder=3)
ax.text(pooled - 0.006, ax.get_ylim()[1] * 0.40, f"Observed\n$D={pooled:.4f}$", color=C_CONF, ha="right", va="top", fontsize=6.4)
ax.text(0.545, 0.95, f"246 wind shifts\n0 of 246 $\\geq$ observed\n$p=1/247=0.0040$", transform=ax.transAxes, va="top", fontsize=6.2, color="#3a3a3a")
ax.set_xlim(-0.13, 0.31); ax.set_xlabel("Pooled statistic $D$ (dimensionless)"); ax.set_ylabel("Number of shifted-wind surrogates")
# (d) lag centroid vs nominal transit time
ax = axs[3]; mid = np.array([0.25, 0.75, 1.25, 1.75, 2.5]); wid = np.array([0.36, 0.36, 0.36, 0.36, 0.6])
ax.plot([0, 3], [0, 3], ls=(0, (1.5, 1.5)), c=C_NULL, lw=0.7, zorder=0)
for k in range(5):
    ax.add_patch(plt.Rectangle((mid[k] - wid[k] / 2, kern.ref_centroid_min[k]), wid[k], kern.ref_centroid_max[k] - kern.ref_centroid_min[k], fc=C_REF, ec="none", alpha=0.75, zorder=1))
ax.vlines(mid - 0.06, kern.centroid_min_by_year, kern.centroid_max_by_year, color=C_DEV, lw=0.7, zorder=2)
ax.plot(mid - 0.06, kern.centroid, "o", c=C_DEV, ms=3.8, zorder=3)
ax.plot(mid + 0.06, c26, "D", c=C_CONF, ms=3.8, zorder=3)
ax.set_xticks(mid, ["0–0.5", "0.5–1", "1–1.5", "1.5–2", "2–3"]); ax.set_xlim(0, 3); ax.set_ylim(0, 3.05)
ax.set_xlabel("Nominal transit-time class (h)"); ax.set_ylabel("Positive-part lag centroid (h)")
hd = [plt.Line2D([], [], marker="o", c=C_DEV, ms=3.8, lw=0.7, label="2021–2025 (bar: range over years)"),
      plt.Line2D([], [], marker="D", ls="", c=C_CONF, ms=3.8, label="2026"),
      plt.Rectangle((0, 0), 1, 1, fc=C_REF, alpha=0.75, label="Development simulated reference range"),
      plt.Line2D([], [], ls=(0, (1.5, 1.5)), c=C_NULL, lw=0.7, label="Centroid = transit time")]
ax.legend(handles=hd, frameon=False, loc="upper left", fontsize=5.9, handlelength=1.6, labelspacing=0.3, borderaxespad=0.0)
for ext in ("pdf", "svg"):
    fig.savefig(OUT / f"fig05_directional_coupling_results.{ext}", metadata={"Date": None} if ext == "svg" else {"CreationDate": None})
fig.savefig(OUT / "fig05_directional_coupling_results.png", dpi=600)
fig.savefig(OUT / "fig05_directional_coupling_results.tiff", dpi=600, pil_kwargs={"compression": "tiff_lzw"})
print(json.dumps(dict(pooled=pooled, p=p_shift, max_surrogate=float(pn.max()), dev_inside_ref=int(inside)), indent=0))
