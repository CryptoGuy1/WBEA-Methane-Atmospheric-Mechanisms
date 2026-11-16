"""Graphical abstract v2: icon-led, minimal text (about 20 words). Pure vector shapes drawn in code; data from committed results.
No raster images or generative imagery."""
import sys, io, json, pathlib, subprocess, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Arc, Polygon
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(ROOT / "src"))
from wbea import e08
SRC = "17883015a4ed7e998701cf67a77a4a7c1c2754a4"; MS = "b61ffbfd35f9cc97626d8f92840e52ac4f7e74ad"
def g(ref, p): r = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{p}"], capture_output=True); assert r.returncode == 0, p; return r.stdout
C = "experiments/E08_confirmation/confirmation_2026/"
R = json.loads(g(SRC, C + "e08_results.json")); H1, H2, H3 = R["H1"], R["H2"], R["H3"]
D, pn, _ = e08.pooled_inverse_null_variance(np.load(io.BytesIO(g(SRC, C + "h2_Dobs.npy"))), np.load(io.BytesIO(g(SRC, C + "h2_null_matrix.npy"))))
assert abs(D - H2["pooled_D"]) < 1e-12 and len(pn) == 246
pairs26 = pd.read_csv(io.BytesIO(g(SRC, C + "h2_pairs.csv"))).pair.tolist(); assert len(pairs26) == 21
st = pd.read_csv(io.BytesIO(g(MS, "manuscript/data/section2/stations_study.csv"))).set_index("station_id")
h1d = pd.read_csv(io.BytesIO(g(SRC, "experiments/E04_stability_elasticity/results/h1_estimates.csv"))).set_index("label").loc["Direct (with log wind)"]
h3d = pd.read_csv(io.BytesIO(g(SRC, "experiments/E07_composition_decomposition/results/h3_sensitivity.csv"))).iloc[0]

plt.rcParams.update({"font.family": "Liberation Sans", "mathtext.fontset": "custom", "mathtext.rm": "Liberation Sans", "mathtext.bf": "Liberation Sans:bold",
                     "pdf.fonttype": 42, "svg.fonttype": "none"})
NAVY, BLUE, GREEN, ORANGE, GREY, PANEL, LINE = "#0b3a5b", "#2171b5", "#1a7f4b", "#c8621b", "#8a96a3", "#f2f6fa", "#c9d6e3"
fig = plt.figure(figsize=(265.6 / 25.4, 106.2 / 25.4)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 40); ax.set_aspect("equal"); ax.axis("off")
T = dict(color=NAVY, ha="center", va="center")

def panel(x, w, title):
    ax.add_patch(FancyBboxPatch((x, 8.0), w, 31.0, boxstyle="round,pad=0,rounding_size=1.4", fc=PANEL, ec=LINE, lw=1))
    ax.add_patch(FancyBboxPatch((x + w / 2 - 7, 35.6), 14, 2.9, boxstyle="round,pad=0,rounding_size=1.4", fc=NAVY, ec="none"))
    ax.text(x + w / 2, 37.05, title, fontsize=16, fontweight="bold", color="white", ha="center", va="center")
def arrow(x): ax.add_patch(FancyArrowPatch((x, 23.5), (x + 2.6, 23.5), arrowstyle="-|>,head_length=7,head_width=5", color=BLUE, lw=3.5))
# ---------- icons (pure geometry) ----------
def ch4(cx, cy, s=1.0):
    for dx, dy in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
        ax.plot([cx, cx + 1.25 * s * dx], [cy, cy + 1.25 * s * dy], c=GREY, lw=1.6, zorder=2); ax.add_patch(Circle((cx + 1.25 * s * dx, cy + 1.25 * s * dy), 0.5 * s, fc="white", ec=NAVY, lw=1.3, zorder=3))
    ax.add_patch(Circle((cx, cy), 0.85 * s, fc=NAVY, ec="none", zorder=3))
def wind(cx, cy, s=1.0, c=BLUE):
    for k, (L, r) in enumerate(((3.2, 0.55), (4.0, 0.7), (2.6, 0.45))):
        y = cy + (1 - k) * 1.1 * s; x0 = cx - 2.0 * s; x1 = x0 + L * s
        ax.plot([x0, x1], [y, y], c=c, lw=2.2, solid_capstyle="round")
        ax.add_patch(Arc((x1, y + r * s), 2 * r * s, 2 * r * s, theta1=-90, theta2=150, color=c, lw=2.2))
def tower(cx, cy, s=1.0, profile=False):
    ax.plot([cx, cx], [cy - 2.2 * s, cy + 2.2 * s], c=NAVY, lw=2.2, solid_capstyle="round")
    for yy in (cy - 1.2 * s, cy + 1.5 * s): ax.plot([cx - 0.7 * s, cx + 0.7 * s], [yy, yy], c=NAVY, lw=2.0); ax.add_patch(Circle((cx + 0.95 * s, yy), 0.32 * s, fc=ORANGE, ec="none"))
    ax.plot([cx - 1.4 * s, cx + 1.4 * s], [cy - 2.2 * s, cy - 2.2 * s], c=NAVY, lw=2.0)
    if profile:                                                             # warm air aloft over cool surface air (stable)
        yy = np.linspace(-2.0, 2.0, 30) * s; ax.plot(cx - 2.4 * s + 0.35 * s * (yy / s + 2) ** 1.2, cy + yy, c=ORANGE, lw=1.6)
def direction(cx, cy, s=1.0):
    ax.add_patch(Circle((cx, cy), 2.3 * s, fc="white", ec=LINE, lw=1.2))
    ax.add_patch(FancyArrowPatch((cx - 1.6 * s, cy - 1.0 * s), (cx + 1.6 * s, cy + 1.0 * s), arrowstyle="-|>,head_length=5,head_width=3.5", color=BLUE, lw=2.4))
    for px, py in ((-1.6, -1.0), (1.6, 1.0)): ax.add_patch(Circle((cx + px * s * 0.62, cy + py * s * 0.62 - 0.9 * s), 0.38 * s, fc=NAVY, ec="none"))
def regimes(cx, cy, s=1.0):
    cols = ["#9ecae1", "#4292c6", "#08519c"]
    for k, (h1, h2, h3) in enumerate(((1.0, 1.5, 0.9), (1.4, 1.0, 1.0), (0.8, 1.3, 1.3))):
        x = cx - 1.8 * s + k * 1.4 * s; b = cy - 2.0 * s
        for hh, cc in zip((h1, h2, h3), cols): ax.add_patch(Rectangle((x, b), 1.0 * s, hh * s, fc=cc, ec="white", lw=0.6)); b += hh * s
def padlock(cx, cy, s=1.0):
    ax.add_patch(Arc((cx, cy + 0.6 * s), 2.0 * s, 2.6 * s, theta1=0, theta2=180, color=NAVY, lw=2.4))
    ax.add_patch(FancyBboxPatch((cx - 1.5 * s, cy - 1.6 * s), 3.0 * s, 2.3 * s, boxstyle="round,pad=0,rounding_size=0.3", fc=NAVY, ec="none"))
    ax.add_patch(Circle((cx, cy - 0.5 * s), 0.3 * s, fc="white", ec="none"))
def status(cx, cy, ok):
    ax.add_patch(Circle((cx, cy), 1.3, fc=GREEN if ok else ORANGE, ec="none"))
    if ok: ax.plot([cx - 0.6, cx - 0.12, cx + 0.65], [cy, cy - 0.5, cy + 0.55], c="white", lw=2.6, solid_capstyle="round", solid_joinstyle="round")
    else: ax.plot([cx - 0.6, cx + 0.6], [cy, cy], c="white", lw=2.8, solid_capstyle="round")

# ---------- panels ----------
P1, P2, P3 = (1.0, 26.4), (30.6, 26.0), (60.8, 38.2)
for (x, w), t in zip((P1, P2, P3), ("Data", "Test", "2026")): panel(x, w, t)
arrow(27.7); arrow(57.6)

# panel 1: real network map + three input icons
m = fig.add_axes([0.03, 0.30, 0.13, 0.55]); m.axis("off")
la0, lo0 = st.loc["AMS 5", "latitude_deg_n"], st.loc["AMS 5", "longitude_deg_e"]
km = lambda s: ((st.loc[s, "longitude_deg_e"] - lo0) * 111.32 * np.cos(np.deg2rad(57)), (st.loc[s, "latitude_deg_n"] - la0) * 110.57)
for p in pairs26:
    i, j = p.split("->"); (a, b), (c, d) = km(i), km(j); m.plot([a, c], [b, d], c="#a9bccf", lw=0.9, zorder=1)
for s in st.index:
    if s in ("AMS 14", "AMS 18"): continue
    x, y = km(s); m.scatter(x, y, s=46, facecolor="white" if s == "AMS 2" else BLUE, edgecolor=BLUE, linewidth=1.5, zorder=3)
m.set_aspect("equal", adjustable="datalim")
ch4(21.2, 29.6, 1.0); ax.text(21.2, 26.4, "CH$_4$", fontsize=13, **T); wind(21.6, 20.6, 1.0); tower(21.2, 13.6, 1.0)
ax.text(8.6, 10.0, "12 stations", fontsize=14, **T)

# panel 2: three tested relationships (one word each) + held-out lock
for cx, draw, word in ((35.6, lambda: tower(35.8, 28.4, 1.0, profile=True), "Stability"), (43.6, lambda: direction(43.6, 28.4, 1.0), "Direction"),
                       (51.6, lambda: regimes(51.8, 28.6, 1.0), "Weather")):
    draw(); ax.text(cx, 23.9, word, fontsize=13, **T)
padlock(38.8, 14.4, 1.0); ax.text(46.6, 14.0, "2026\nheld out", fontsize=13, fontweight="bold", color=NAVY, ha="center", va="center", linespacing=1.1)

# panel 3: real-data thumbnails + status
rows = [("H1", True, f"{H1['b1_primary']:.3f}"), ("H2", True, f"D = {D:.3f}"), ("H3", False, f"{H3['share']:.3f}")]
for k, (lab, ok, val) in enumerate(rows):
    y = 29.6 - k * 8.6
    ax.add_patch(FancyBboxPatch((62.0, y - 3.4), 35.8, 7.6, boxstyle="round,pad=0,rounding_size=0.9", fc="white", ec=LINE, lw=0.8))
    ax.text(64.6, y + 0.4, lab, fontsize=16, fontweight="bold", **T)
    ax.text(88.6, y + 0.4, val, fontsize=14.5, fontweight="bold", color=GREEN if ok else ORANGE, ha="center", va="center")
    status(95.2, y + 0.4, ok)
def thumb(k): y = 29.6 - k * 8.6; return fig.add_axes([0.672, (y - 2.6) / 40, 0.15, 0.16])
def interval(t, dev, conf, col, xl):
    e, lo, hi = conf; t.plot([lo, hi], [0, 0], c=col, lw=3.0, solid_capstyle="round"); t.plot(e, 0, "o", c=col, ms=8)   # 2026 registered estimate and 95% interval
    t.axvline(0, c=NAVY, lw=1.2); t.set_xlim(*xl); t.set_ylim(-1, 1); t.axis("off")
interval(thumb(0), (h1d.estimate, h1d.ci_lo, h1d.ci_hi), (H1["b1_primary"], *H1["b1_primary_ci"]), GREEN, (-0.01, 0.08))
t = thumb(1); t.hist(pn, bins=np.arange(-0.12, 0.135, 0.02), color="#a9bccf", ec="white", lw=0.5); t.axvline(D, c=GREEN, lw=3); t.set_xlim(-0.13, 0.31); t.axis("off")
t.plot([-0.13, 0.31], [0, 0], c=NAVY, lw=1.0)
interval(thumb(2), (h3d.share, h3d.ci_lo, h3d.ci_hi), (H3["share"], H3["ci_lo"], H3["ci_hi"]), ORANGE, (-0.06, 0.14))

# footer: statistical direction is not proven transport
ax.add_patch(FancyBboxPatch((1.0, 0.8), 98.0, 5.8, boxstyle="round,pad=0,rounding_size=1.2", fc="#e6f0f2", ec="none"))
for x in (30.0, 37.0): ax.add_patch(Circle((x, 3.7), 0.75, fc=BLUE, ec="none"))
xx = np.linspace(31.1, 35.6, 60); ax.plot(xx, 3.7 + 0.45 * np.sin((xx - 31.1) * 2.6), c=GREY, lw=2)
ax.add_patch(FancyArrowPatch((35.4, 3.7), (36.1, 3.7), arrowstyle="-|>,head_length=4,head_width=3", color=GREY, lw=2))
ax.plot([32.0, 35.0], [2.2, 5.2], c=ORANGE, lw=2.6); ax.plot([32.0, 35.0], [5.2, 2.2], c=ORANGE, lw=2.6)
ax.text(40.0, 3.7, "Statistical direction ≠ proven transport", fontsize=16, fontweight="bold", color=NAVY, ha="left", va="center")
for ext in ("pdf", "svg"): fig.savefig(OUT / f"graphical_abstract_v2.{ext}")
fig.savefig(OUT / "graphical_abstract_v2.png", dpi=300); print("ok")
