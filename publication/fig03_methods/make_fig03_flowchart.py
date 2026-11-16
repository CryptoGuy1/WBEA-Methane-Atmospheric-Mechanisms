"""Figure 3 (flowchart): data -> preprocessing -> H1/H2/H3 estimators -> registered decisions -> post-confirmation checks,
with a study-timeline band. Minimal text (2-4 words per box); vector shapes only; no data, icons or generated imagery."""
import pathlib, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon
OUT = pathlib.Path(__file__).resolve().parent
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "pdf.fonttype": 42, "svg.fonttype": "none"})
NAVY, BLUE, TEAL, ORANGE, GREY, LINE, PALE = "#0b3a5b", "#2171b5", "#1b7f8c", "#c8621b", "#5f6b78", "#b8c7d6", "#eef3f8"
W, H = 174.5, 74.0
fig = plt.figure(figsize=(W / 25.4, H / 25.4)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
def box(x, y, w, h, fc, ec="none", ls="-", lw=0.8, r=1.6): ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, ls=ls, lw=lw))
def txt(x, y, s, size=7.6, c=NAVY, bold=False): ax.text(x, y, s, fontsize=size, color=c, fontweight="bold" if bold else "normal", ha="center", va="center", linespacing=1.25)
def arr(p, q, c=GREY, ls="-", lw=1.1, rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>,head_length=3.2,head_width=2.0", color=c, lw=lw, ls=ls, connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))

# timeline band
yt = 62.0
for x, w, s, fc in ((14.0, 44.0, "Development  2021–2025", "#e3e8ee"), (70.0, 34.0, "      Frozen protocol", "#fbe3d3"), (116.0, 46.0, "Confirmation  Jan–Sep 2026", "#d6e6f5")):
    box(x, yt, w, 8.0, fc, r=4.0); txt(x + w / 2, yt + 4.0, s, 7.6, NAVY, True)
arr((58.6, yt + 4.0), (69.4, yt + 4.0)); arr((104.6, yt + 4.0), (115.4, yt + 4.0))
lx = 74.6; ax.add_patch(FancyBboxPatch((lx - 1.6, yt + 2.2), 3.2, 2.6, boxstyle="round,pad=0,rounding_size=0.4", fc=ORANGE, ec="none"))
ax.add_patch(matplotlib.patches.Arc((lx, yt + 4.8), 2.2, 2.8, theta1=0, theta2=180, color=ORANGE, lw=1.1))

# data -> preprocessing
box(4.0, 20.0, 28.0, 32.0, PALE, ec=LINE)
txt(18.0, 47.0, "Hourly data", 8.0, NAVY, True)
for k, s in enumerate(("CH$_4$, 12 stations", "Wind", "Tower stability")):
    box(7.0, 37.0 - k * 7.0, 22.0, 5.4, "white", ec=LINE, r=1.0); txt(18.0, 39.7 - k * 7.0, s, 7.0, NAVY)
arr((32.6, 36.0), (39.4, 36.0))
box(40.0, 26.0, 26.0, 20.0, "#dde8f3", ec=LINE)
txt(53.0, 36.0, "Quality control\n+\nRegional\nresidualisation", 7.4, NAVY, True)

# estimators
est = [("H1", "Stability\nregression", TEAL, 46.0), ("H2", "Shifted-wind\ntest", BLUE, 31.0), ("H3", "Regime\ndecomposition", ORANGE, 16.0)]
for h, s, c, y in est:
    arr((66.6, 36.0), (75.4, y + 5.0), rad=0.0)
    box(76.0, y, 34.0, 10.0, c); ax.text(80.0, y + 5.0, h, fontsize=9.0, color="white", fontweight="bold", ha="left", va="center")
    txt(98.0, y + 5.0, s, 7.4, "white", True)
    arr((110.6, y + 5.0), (121.4, 36.0 + (y - 31.0) * 0.35))

# decisions (fed by the frozen confirmation run)
box(122.0, 27.0, 22.0, 18.0, NAVY); txt(133.0, 36.0, "Registered\ndecisions", 7.8, "white", True)
arr((139.0, yt - 0.6), (136.0, 45.6), c=BLUE, ls=(0, (2.5, 1.5)))

# post-confirmation checks
box(150.0, 8.0, 22.0, 46.0, "white", ec=LINE, ls=(0, (3, 2)), lw=0.9)
txt(161.0, 49.6, "Post-\nconfirmation", 7.0, GREY, True)
for k, s in enumerate(("Synthetic\ntests", "Seasonal\nreferences", "Cross-year\ncontrols", "Matched\npairs")):
    box(152.0, 36.0 - k * 8.8, 18.0, 7.4, PALE, r=1.0); txt(161.0, 39.7 - k * 8.8, s, 6.6, NAVY)
arr((144.6, 36.0), (149.4, 36.0), ls=(0, (2.5, 1.5)))
for ext in ("pdf", "svg"): fig.savefig(OUT / f"fig03_flowchart.{ext}")
fig.savefig(OUT / "fig03_flowchart.png", dpi=600); print("ok")
