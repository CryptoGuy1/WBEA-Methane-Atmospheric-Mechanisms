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
for x, w, s, fc in ((14.0, 44.0, "Development  2021–2025", "#e3e8ee"), (78.75, 34.0, "      Frozen protocol", "#fbe3d3"), (121.0, 51.5, "Confirmation  Jan–Sep 2026", "#d6e6f5")):
    box(x, yt, w, 8.0, fc, r=4.0); txt(x + w / 2, yt + 4.0, s, 7.6, NAVY, True)
arr((58.6, yt + 4.0), (78.1, yt + 4.0)); arr((113.4, yt + 4.0), (120.4, yt + 4.0))
lx = 82.35; ax.add_patch(FancyBboxPatch((lx - 1.6, yt + 2.2), 3.2, 2.6, boxstyle="round,pad=0,rounding_size=0.4", fc=ORANGE, ec="none"))
ax.add_patch(matplotlib.patches.Arc((lx, yt + 4.8), 2.2, 2.8, theta1=0, theta2=180, color=ORANGE, lw=1.1))

# data -> preprocessing (both periods enter the same path)
box(4.0, 12.0, 28.0, 44.0, PALE, ec=LINE)
txt(18.0, 51.6, "Hourly data", 8.0, NAVY, True)
for k, s in enumerate(("CH$_4$, 12 stations", "Wind", "Tower stability")):
    box(7.0, 41.0 - k * 6.4, 22.0, 5.0, "white", ec=LINE, r=1.0); txt(18.0, 43.5 - k * 6.4, s, 7.0, NAVY)
box(7.0, 21.0, 22.0, 4.6, "#e3e8ee", r=1.0); txt(18.0, 23.3, "2021–2025", 7.0, NAVY, True)
box(7.0, 15.0, 22.0, 4.6, "#d6e6f5", r=1.0); txt(18.0, 17.3, "Jan–Sep 2026", 7.0, NAVY, True)
arr((32.6, 34.0), (38.4, 34.0))
box(39.0, 23.0, 25.0, 22.0, "#dde8f3", ec=LINE)
txt(51.5, 34.0, "Quality control\n+\n2021–2023\nreference values", 7.4, NAVY, True)

# estimators, procedures fixed by the frozen protocol
box(69.5, 1.0, 52.5, 58.0, "white", ec=ORANGE, ls=(0, (3, 2)), lw=0.9, r=2.0)
txt(95.75, 6.3, "Prespecified estimators\nand decision rules", 7.0, ORANGE, True)
arr((95.75, yt - 0.6), (95.75, 59.6), c=ORANGE, lw=1.2)
est = [("H1", "Stability association", "adjusted regression", TEAL, 45.0), ("H2", "Directional dependence", "shifted-wind reference;\nleave-pair-out residuals", BLUE, 28.5),
       ("H3", "Regime composition", "rate decomposition", ORANGE, 12.0)]
for h, t1, t2, c, y in est:
    arr((64.6, 34.0), (72.4, y + 6.0))
    box(73.0, y, 46.0, 12.0, c); ax.text(75.4, y + 6.0, h, fontsize=9.0, color="white", fontweight="bold", ha="left", va="center")
    ax.text(82.2, y + 8.2, t1, fontsize=7.4, color="white", fontweight="bold", ha="left", va="center")
    ax.text(82.2, y + (3.2 if "\n" in t2 else 4.0), t2, fontsize=7.0, color="white", ha="left", va="center", linespacing=1.15)
    arr((122.6, y + 6.0), (126.9, 34.0 + (y - 28.5) * 0.3))

# registered decisions come from H1-H3 applied to the 2026 data
box(127.5, 24.0, 20.0, 20.0, NAVY); txt(137.5, 34.0, "Registered\ndecisions\n(2026)", 7.8, "white", True)

# post-confirmation checks
box(152.0, 1.0, 21.5, 58.0, "white", ec=LINE, ls=(0, (3, 2)), lw=0.9)
txt(162.75, 52.4, "Post-\nconfirmation\ndiagnostics", 7.0, GREY, True)
for s_, y0, hgt in (("Synthetic\ncalibration &\nfalsification", 35.2, 11.0), ("Seasonal\nreferences", 25.6, 8.0), ("Cross-year\ncontrols", 16.0, 8.0), ("Matched\npairs", 6.4, 8.0)):
    box(153.75, y0, 18.0, hgt, PALE, r=1.0); txt(162.75, y0 + hgt / 2, s_, 7.0, NAVY)
arr((148.1, 34.0), (151.4, 34.0), ls=(0, (2.5, 1.5)))
for ext in ("pdf", "svg"): fig.savefig(OUT / f"fig03_flowchart.{ext}")
fig.savefig(OUT / "fig03_flowchart.png", dpi=600); print("ok")
