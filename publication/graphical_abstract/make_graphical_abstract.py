"""Graphical abstract (EMS). All graphics drawn in code from saved, committed results; no raster images, no generative imagery.
Data: station coordinates (manuscript branch), 2026 H2 pairs and 246-shift null (frozen E08 outputs), registered H1-H3 estimates."""
import sys, io, json, pathlib, subprocess, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Polygon
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(ROOT / "src"))
from wbea import e08
SRC = "17883015a4ed7e998701cf67a77a4a7c1c2754a4"; MS = "b61ffbfd35f9cc97626d8f92840e52ac4f7e74ad"
def g(ref, p): r = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{p}"], capture_output=True); assert r.returncode == 0, p; return r.stdout
C = "experiments/E08_confirmation/confirmation_2026/"
R = json.loads(g(SRC, C + "e08_results.json")); H1, H2, H3 = R["H1"], R["H2"], R["H3"]
Do, Nm = np.load(io.BytesIO(g(SRC, C + "h2_Dobs.npy"))), np.load(io.BytesIO(g(SRC, C + "h2_null_matrix.npy")))
D, pn, _ = e08.pooled_inverse_null_variance(Do, Nm); assert abs(D - H2["pooled_D"]) < 1e-12 and len(pn) == 246
pairs26 = pd.read_csv(io.BytesIO(g(SRC, C + "h2_pairs.csv"))).pair.tolist(); assert len(pairs26) == 21
st = pd.read_csv(io.BytesIO(g(MS, "manuscript/data/section2/stations_study.csv"))).set_index("station_id")
h1dev = pd.read_csv(io.BytesIO(g(SRC, "experiments/E04_stability_elasticity/results/h1_estimates.csv"))).set_index("label").loc["Direct (with log wind)"]
h3dev = pd.read_csv(io.BytesIO(g(SRC, "experiments/E07_composition_decomposition/results/h3_sensitivity.csv"))).iloc[0]

plt.rcParams.update({"mathtext.fontset": "custom", "mathtext.rm": "Liberation Sans", "mathtext.it": "Liberation Sans:italic", "mathtext.bf": "Liberation Sans:bold", "font.family": "Liberation Sans", "pdf.fonttype": 42, "svg.fonttype": "none", "axes.linewidth": 0.8})
NAVY, BLUE, TEAL, ORANGE, GREEN, GREY, LIGHT = "#0b3a5b", "#2171b5", "#1b7f8c", "#c8621b", "#1a7f4b", "#6b7785", "#f2f6fa"
W, H = 265.6 / 25.4, 106.2 / 25.4                                   # 2x Elsevier display size (13.28 x 5.31 cm)
fig = plt.figure(figsize=(W, H)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 40); ax.axis("off")
def panel(x, w, title):
    ax.add_patch(FancyBboxPatch((x, 7.2), w, 31.6, boxstyle="round,pad=0,rounding_size=1.2", fc=LIGHT, ec="#c9d6e3", lw=1))
    ax.add_patch(FancyBboxPatch((x + 1.0, 35.3), w - 2.0, 3.0, boxstyle="round,pad=0,rounding_size=1.4", fc=NAVY, ec="none"))
    ax.text(x + w / 2, 36.8, title, ha="center", va="center", color="white", fontsize=13.5, fontweight="bold")
def arrow(x): ax.add_patch(FancyArrowPatch((x, 22.5), (x + 2.0, 22.5), arrowstyle="-|>,head_length=6,head_width=4", color=BLUE, lw=3))
P1, P2, P3 = (1.0, 26.6), (30.2, 25.8), (59.6, 39.4)
for (x, w), t in zip((P1, P2, P3), ("Monitoring network", "Tested framework", "Registered 2026 confirmation")): panel(x, w, t)
arrow(27.9); arrow(57.3)

# --- panel 1: real station map (km from AMS 5), 21 confirmation pairs
m = fig.add_axes([0.018, 0.335, 0.105, 0.52]); m.axis("off")
la0, lo0 = st.loc["AMS 5", "latitude_deg_n"], st.loc["AMS 5", "longitude_deg_e"]
km = lambda s: ((st.loc[s, "longitude_deg_e"] - lo0) * 111.32 * np.cos(np.deg2rad(57)), (st.loc[s, "latitude_deg_n"] - la0) * 110.57)
for p in pairs26:
    i, j = p.split("->"); (x1, y1), (x2, y2) = km(i), km(j); m.plot([x1, x2], [y1, y2], c="#9fb6cc", lw=0.8, zorder=1)
for s in st.index:
    if s in ("AMS 14", "AMS 18"): continue
    x, y = km(s); m.scatter(x, y, s=30, facecolor="white" if s == "AMS 2" else BLUE, edgecolor=BLUE, linewidth=1.3, zorder=3)
m.set_aspect("equal", adjustable="datalim")
tx = 13.4
ax.text(tx, 33.4, "WBEA network,\nAlberta", fontsize=12.5, fontweight="bold", color=NAVY, va="top", linespacing=1.15)
ax.text(tx, 27.6, "12 stations:\nhourly CH$_4$,\nwind, tower\nstability", fontsize=11, color="#2b3a4a", va="top", linespacing=1.2)
ax.text(tx, 19.6, "lines: 21 pairs\n≤ 30 km", fontsize=11, color="#2b3a4a", va="top", linespacing=1.2)
ax.scatter([tx + 0.6], [14.0], s=30, facecolor="white", edgecolor=BLUE, linewidth=1.3, transform=ax.transData, zorder=5, clip_on=False)
ax.text(tx + 1.6, 14.0, "AMS 2, excluded\nin 2026", fontsize=10, color=GREY, va="center", linespacing=1.1)
ax.add_patch(FancyBboxPatch((2.0, 8.2), 24.6, 4.4, boxstyle="round,pad=0,rounding_size=0.8", fc="white", ec="#c9d6e3", lw=0.8))
ax.text(14.3, 11.3, "2021–2025: development", ha="center", va="center", fontsize=10.5, color="#2b3a4a")
ax.text(14.3, 9.3, "Jan–Sep 2026: held out, frozen", ha="center", va="center", fontsize=10.5, color="#2b3a4a", fontweight="bold")

# --- panel 2: hypotheses and tests
hy = [("H1", "Stability association", "adjusted regression", TEAL), ("H2", "Wind directionality", "aligned vs reversed winds", BLUE),
      ("H3", "Regime composition", "between-year decomposition", ORANGE)]
for k, (h, t, sub, c) in enumerate(hy):
    y = 29.4 - k * 6.2
    ax.add_patch(FancyBboxPatch((31.4, y), 23.4, 5.2, boxstyle="round,pad=0,rounding_size=0.8", fc="white", ec="#d3dde8", lw=0.8))
    ax.add_patch(FancyBboxPatch((31.4, y), 0.8, 5.2, boxstyle="square,pad=0", fc=c, ec="none"))
    ax.text(33.0, y + 3.5, f"{h}  {t}", fontsize=12, fontweight="bold", color=NAVY, va="center")
    ax.text(33.0, y + 1.4, sub, fontsize=10.5, color=GREY, va="center")
ax.add_patch(FancyBboxPatch((31.4, 8.2), 23.4, 8.2, boxstyle="round,pad=0,rounding_size=0.8", fc="#e3ecf6", ec="none"))
ax.text(43.1, 14.6, "Tested against", ha="center", va="center", fontsize=10.5, color=GREY)
ax.text(43.1, 11.3, "frozen protocol\nshifted-wind reference\nsynthetic falsification", ha="center", va="center", fontsize=10.5, color=NAVY, fontweight="bold", linespacing=1.2)

# --- panel 3: registered results with real thumbnails
rows = [("H1 Stability", "Confirmed", GREEN, f"+{H1['b1_primary']:.3f} ppm/SD", f"95% CI {H1['b1_primary_ci'][0]:.3f}–{H1['b1_primary_ci'][1]:.3f}"),
        ("H2 Directionality", "Confirmed", GREEN, f"D = {D:.3f}", "p = 1/247 (minimum)"),
        ("H3 Composition", "Not confirmed", ORANGE, f"share = {H3['share']:.3f}", f"95% CI {H3['ci_lo']:.3f} to {H3['ci_hi']:.3f}".replace("-", "−"))]
for k, (lab, dec, c, val, sub) in enumerate(rows):
    y = 28.4 - k * 7.0
    ax.add_patch(FancyBboxPatch((60.6, y - 0.6), 37.4, 6.4, boxstyle="round,pad=0,rounding_size=0.8", fc="white", ec="#d3dde8", lw=0.8))
    ax.text(61.6, y + 4.3, lab, fontsize=12, fontweight="bold", color=NAVY, va="center")
    ax.text(61.6, y + 2.2, val, fontsize=12, color=c, fontweight="bold", va="center")
    ax.text(61.6, y + 0.4, sub, fontsize=10, color=GREY, va="center")
    bw = 7.6 if dec == "Confirmed" else 10.2
    ax.add_patch(FancyBboxPatch((75.0, y + 1.3), bw, 2.0, boxstyle="round,pad=0,rounding_size=0.9", fc=c, ec="none"))
    ax.text(75.0 + bw / 2, y + 2.3, dec, fontsize=10, color="white", fontweight="bold", ha="center", va="center")
def thumb(k): return fig.add_axes([0.862, (28.4 - k * 7.0 + 0.6) / 40, 0.112, 0.115])
def ci_thumb(t, dev, conf, col, xl, xt):
    for yy, (e, lo, hi), cc in ((1, dev, GREY), (0, conf, col)):
        t.plot([lo, hi], [yy, yy], c=cc, lw=1.8); t.plot(e, yy, "o", c=cc, ms=4.5)
    t.axvline(0, c="#9aa5b1", lw=0.8); t.set_xlim(*xl); t.set_ylim(-0.7, 1.7); t.set_yticks([])
    t.set_xticks(xt); t.tick_params(axis="x", labelsize=9, length=2); t.tick_params(axis="y", length=0)
    [t.spines[s].set_visible(False) for s in ("top", "right", "left")]
ci_thumb(thumb(0), (h1dev.estimate, h1dev.ci_lo, h1dev.ci_hi), (H1["b1_primary"], *H1["b1_primary_ci"]), GREEN, (-0.01, 0.08), [0, 0.04, 0.08])
t = thumb(1)                                                            # H2: real 246-shift null and observed D
t.hist(pn, bins=np.arange(-0.12, 0.13, 0.015), color="#9fb6cc", ec="white", lw=0.3); t.axvline(D, c=GREEN, lw=2.2)
t.set_xlim(-0.13, 0.32); t.set_yticks([]); t.set_xticks([0, 0.3]); t.tick_params(axis="x", labelsize=9, length=2); [t.spines[s].set_visible(False) for s in ("top", "right", "left")]
t.text(0.19, t.get_ylim()[1] * 0.55, "246\nshifts", fontsize=9, color=GREY, ha="right", va="center")
ax.plot([62.0, 63.6], [9.6, 9.6], c=GREY, lw=1.8); ax.plot(62.8, 9.6, "o", c=GREY, ms=4.5); ax.text(64.4, 9.6, "2021–2025 development", fontsize=10, color=GREY, va="center")
for xk, cc in ((80.0, GREEN), (81.6, ORANGE)): ax.plot(xk, 9.6, "o", c=cc, ms=4.5)
ax.text(82.8, 9.6, "2026 registered", fontsize=10, color=GREY, va="center")
ax.text(62.0, 11.7, "Bars: 95% intervals. H2 histogram: 246-shift null", fontsize=9.5, color=GREY, va="center")
ci_thumb(thumb(2), (h3dev.share, h3dev.ci_lo, h3dev.ci_hi), (H3["share"], H3["ci_lo"], H3["ci_hi"]), ORANGE, (-0.06, 0.14), [0, 0.1])

# --- caveat ribbon
ax.add_patch(FancyBboxPatch((1.0, 0.8), 98.0, 5.2, boxstyle="round,pad=0,rounding_size=1.0", fc="#e8f1f3", ec="none"))
ax.text(2.5, 3.4, "Falsification:", fontsize=12.5, fontweight="bold", color=TEAL, va="center")
ax.text(13.6, 3.4, "a wind-carried shared driver with no station-to-station transfer was detected in 200/200 simulations,\nso confirmed H2 directionality is statistical, not proof of methane transport.",
        fontsize=11.5, color="#1f2d3a", va="center", linespacing=1.15)
for ext in ("pdf", "svg"): fig.savefig(OUT / f"graphical_abstract.{ext}")
fig.savefig(OUT / "graphical_abstract.png", dpi=300)
print("ok", round(D, 4), H1["b1_primary"], H3["share"])
