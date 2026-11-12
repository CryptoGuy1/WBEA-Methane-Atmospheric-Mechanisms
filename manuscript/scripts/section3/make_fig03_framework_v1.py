"""Fig. 3: falsification-tested analysis framework (schematic; no data). Vector, 174.5 mm (CAS textwidth), style as Figs 1-2."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "section2"))
import common
from common import plt, MM
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import matplotlib.dates as mdates, datetime as dt
OUT = common.ROOT / "manuscript/figures/section3/archive_v1"
W, H = 174.5, 98.0
C_DEV, C_REF, C_CONF, C_FRZ, C_INK, C_MUTE, C_BOX = "#9ecae1", "#deebf7", "#2171b5", "#d94801", "#252525", "#6b6b6b", "#ffffff"
fig = plt.figure(figsize=(W * MM, H * MM)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
def box(x, y, w, h, fc=C_BOX, ec="#bdbdbd", lw=0.6, r=1.2, ls="-", z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))
def text(x, y, s, size=6.8, color=C_INK, ha="center", va="center", weight="normal", style="normal", z=5):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, fontweight=weight, style=style, zorder=z, linespacing=1.15)
def arrow(x0, y0, x1, y1, color="#8c8c8c", lw=0.7):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=6, lw=lw, color=color, shrinkA=0, shrinkB=0, zorder=3))

# ---------------- timeline (top)
X0, X1 = 30.0, W - 4.0; t0, t1 = dt.date(2021, 1, 1), dt.date(2026, 10, 1)
tx = lambda d: X0 + (X1 - X0) * (d - t0).days / (t1 - t0).days
TY = 84.0
for yr in range(2021, 2027):
    ax.plot([tx(dt.date(yr, 1, 1))] * 2, [TY - 7.4, TY - 6.4], c=C_MUTE, lw=0.5); text(tx(dt.date(yr, 1, 1)), TY - 9.2, str(yr), size=6.3, color=C_MUTE)
ax.plot([X0, X1], [TY - 6.4, TY - 6.4], c=C_MUTE, lw=0.5)
box(tx(t0), TY, tx(dt.date(2025, 12, 2)) - tx(t0), 4.6, fc=C_DEV, ec="none", r=0.8)
text((tx(t0) + tx(dt.date(2025, 12, 2))) / 2, TY + 2.3, "Development  (exploratory)", size=6.8)
box(tx(t0), TY - 5.2, tx(dt.date(2024, 1, 1)) - tx(t0), 3.6, fc=C_REF, ec=C_DEV, lw=0.5, r=0.8)
text((tx(t0) + tx(dt.date(2024, 1, 1))) / 2, TY - 3.4, "Reference  (fixed baselines)", size=6.3)
xf = tx(dt.date(2025, 12, 20))
ax.plot([xf, xf], [TY - 6.4, TY + 8.0], c=C_FRZ, lw=1.1, zorder=4); text(xf, TY + 9.6, "Protocol frozen", size=6.5, color=C_FRZ, weight="bold")
box(tx(dt.date(2026, 1, 1)), TY, tx(t1) - tx(dt.date(2026, 1, 1)), 4.6, fc=C_CONF, ec="none", r=0.8)
text((tx(dt.date(2026, 1, 1)) + tx(t1)) / 2, TY - 3.4, "Confirmation", size=6.5, color=C_CONF, weight="bold")
text(4.0, TY + 2.3, "Data periods", size=7, ha="left", weight="bold")

# ---------------- hypothesis lanes
cols = [("Inputs", 30.0), ("Estimator", 66.5), ("Inference", 103.0), ("Decision rule", 139.5)]; CW = 31.0
LY, LH, GAP = 54.0, 9.4, 3.2                                                # top lane y, lane height, gap
lanes = [("H1", "Stability\nassociation", ["Network CH$_4$ median;\nAMS 5 $T_{90}-T_{20}$", "Cell-adjusted\nregression", "14-day block\nbootstrap", "CI $>$ 0;\nnext-day control"]),
         ("H2", "Directional\ncoupling", ["Leave-pair-out\nresiduals; 21 pairs", "Aligned $-$ reversed\nlead–lag contrast $D$", "All 246 whole-day\nwind shifts", "$p<0.05$; $\\pm$1 h;\nordered lags"]),
         ("H3", "Regime\ncomposition", ["Station excursions;\n18 meteorological regimes", "Rate decomposition\n(composition share)", "Joint block\nbootstrap", "CI excludes 0"])]
top = LY + LH + 8.0; bot = LY - 2 * (LH + GAP) - 2.0
for k, (name, x) in enumerate(cols):                                       # column tints tie to the timeline colours
    fc, ec = (C_CONF, C_CONF) if k == 3 else (C_REF, C_REF)
    ax.add_patch(Rectangle((x - 1.6, bot), CW + 3.2, top - bot, fc=fc, ec="none", alpha=0.16 if k == 3 else 0.55, zorder=0))
    text(x + CW / 2, top - 2.6, name, size=7, weight="bold", color=C_CONF if k == 3 else C_INK)
text((cols[0][1] + cols[2][1] + CW) / 2, bot - 3.0, "Specified on development data", size=6.3, color=C_MUTE, style="italic")
text(cols[3][1] + CW / 2, bot - 3.0, "Applied once to 2026 data", size=6.3, color=C_CONF, style="italic")
for i, (hid, label, cells) in enumerate(lanes):
    y = LY - i * (LH + GAP)
    box(4.0, y, 23.0, LH, fc="#f2f2f2", ec="none")
    text(7.6, y + LH / 2, hid, size=8.5, weight="bold", color=C_CONF); text(17.2, y + LH / 2, label, size=6.5)
    for j, (cname, x) in enumerate(cols):
        box(x, y, CW, LH, ec="#9e9e9e" if j < 3 else C_CONF, lw=0.6 if j < 3 else 0.8)
        text(x + CW / 2, y + LH / 2, cells[j], size=6.3)
        if j < 3: arrow(x + CW + 0.2, y + LH / 2, cols[j + 1][1] - 0.2, y + LH / 2)

# ---------------- diagnostics and post-confirmation analyses (bottom)
BY, BH = 2.0, 16.0
box(4.0, BY, 51.0, BH, fc="#ffffff", ec="#9e9e9e", lw=0.6, ls=(0, (3, 2)))  # diagnostics
text(6.5, BY + BH - 3.0, "Transport diagnostics", size=6.8, ha="left", weight="bold"); text(37.0, BY + BH - 3.0, "(development)", size=6.3, ha="left", color=C_MUTE)
for j, s in enumerate(["Lag-kernel\nmatch", "Elevated-wind\ntransit"]):
    box(7.0 + j * 23.0, BY + 2.2, 21.0, 8.0, fc="#f7f7f7", ec="none"); text(17.5 + j * 23.0, BY + 6.2, s, size=6.3)
box(58.0, BY, W - 62.0, BH, fc="#ffffff", ec=C_FRZ, lw=0.7, ls=(0, (3, 2)))
text(60.5, BY + BH - 3.0, "Post-confirmation analyses", size=6.8, ha="left", weight="bold"); text(98.8, BY + BH - 3.0, "(exploratory; registered decisions unchanged)", size=6.3, ha="left", color=C_MUTE)
pw = (W - 62.0 - 4.0 * 2 - 2 * 3.0) / 3
for j, s in enumerate(["Synthetic null\ncalibration and power", "Falsification:\nadvected shared signal", "Season-restricted\nshift references"]):
    x = 62.0 + j * (pw + 3.0); box(x, BY + 2.2, pw, 8.0, fc="#fdf0e6", ec="none"); text(x + pw / 2, BY + 6.2, s, size=6.3)
for ext in ("pdf", "svg"): fig.savefig(OUT / f"fig03_framework.{ext}", metadata={"Date": None} if ext == "svg" else {"CreationDate": None})
fig.savefig(OUT / "fig03_framework_600dpi.png", dpi=600); print("fig03 written", W, "x", H, "mm")
