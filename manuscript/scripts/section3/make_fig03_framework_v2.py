"""Fig. 3 (v2): analysis framework in a panelled workflow style. Data thumbnails use REAL data only (plus neutral schematic glyphs for the station pair, interval and decision labels): AMS 1 hourly CH4 and
AMS 5 T90-T20 for 13-19 Jan 2025 (development period), AMS 5 wind rose 2021-2025 (development), and the saved E08
shifted-wind reference distribution (246 pooled null values; observed value deliberately not shown). Vector; 174.5 mm."""
import sys, pathlib, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "section2"))
import common
from common import plt, MM
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Wedge, Polygon, Circle
from wbea.io import load_dev
from wbea.wind import composite
from wbea import e08
OUT = common.ROOT / "manuscript/figures/section3/archive_v2"; ROOT = common.ROOT
W, H = 174.5, 104.0
INK, MUTE = "#1f2d3d", "#5f6b78"
BLUE = dict(fc="#f3f8fd", ec="#9cc0e3", hd="#d6e7f7")        # inputs / outputs
LAV = dict(fc="#f6f3fb", ec="#b7a6d8")                        # (a) temporal design
PEACH = dict(fc="#fdf6ee", ec="#e2b88a")                      # (b) estimands
GREEN = dict(fc="#f1f8ef", ec="#9cc59a")                      # (c) inference
C_DEV, C_REF, C_CONF, C_FRZ = "#9ecae1", "#deebf7", "#2171b5", "#d94801"
fig = plt.figure(figsize=(W * MM, H * MM)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")

def rbox(x, y, w, h, fc, ec, lw=0.8, r=2.2, ls="-", z=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))
def txt(x, y, s, size=6.6, color=INK, ha="center", va="center", weight="normal", style="normal", z=6):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, fontweight=weight, style=style, zorder=z, linespacing=1.15)
def arrow(x0, y0, x1, y1, color="#3d4b5c", lw=0.8, ms=7, z=4):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=ms, lw=lw, color=color, shrinkA=0, shrinkB=0, zorder=z))
def big_arrow(x, y, w=3.4, h=5.0, color="#a9b4c0"):
    ax.add_patch(Polygon([(x, y - h * 0.28), (x + w * 0.55, y - h * 0.28), (x + w * 0.55, y - h / 2), (x + w, y), (x + w * 0.55, y + h / 2),
                          (x + w * 0.55, y + h * 0.28), (x, y + h * 0.28)], closed=True, fc=color, ec="none", zorder=3))
def thumb(x, y, w, h):                                         # inset axes in mm
    a = fig.add_axes([x / W, y / H, w / W, h / H]); a.patch.set_alpha(0)
    for sp in a.spines.values(): sp.set_visible(False)
    a.set_xticks([]); a.set_yticks([]); return a
def header_panel(x, y, w, h, title, style):
    rbox(x, y, w, h, style["fc"], style["ec"])
    ax.add_patch(FancyBboxPatch((x + 0.4, y + h - 7.0), w - 0.8, 6.6, boxstyle="round,pad=0,rounding_size=2.0", fc=style["hd"], ec="none", zorder=1.5))
    txt(x + w / 2, y + h - 3.7, title, size=7.6, weight="bold")
def card(x, y, w, h, title):
    rbox(x, y, w, h, "#ffffff", "#c9dbef", lw=0.6, r=1.8, z=2)
    txt(x + w / 2, y + h - 3.0, title, size=6.4, weight="bold")

# ------------------------------------------------ real data for thumbnails
P = load_dev(["AMS 1", "AMS 5"]); wk = slice("2025-01-13", "2025-01-19")
ch4 = P["AMS 1"]["CH4 (ppm)"].loc[wk]; stab = (P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"]).loc[wk]
cw = composite(P["AMS 5"]); wd = (np.degrees(np.arctan2(-cw.u, -cw.v)) % 360)[cw.ws >= 1.0].dropna()
S_ALL = P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"]; CUTS = S_ALL.loc["2021":"2023"].quantile([1 / 3, 2 / 3]).values   # frozen tercile cuts
null = np.load(ROOT / "experiments/E08_confirmation/confirmation_2026/h2_null_matrix.npy"); _, pooled_null, _ = e08.pooled_inverse_null_variance(np.zeros(null.shape[1]), null)

# ------------------------------------------------ left: data inputs
LX, LW_, TOPY, BOTY = 2.0, 33.0, 101.5, 14.2
header_panel(LX, BOTY, LW_, TOPY - BOTY, "Data inputs", BLUE)
ch = (TOPY - BOTY - 8.0 - 3 * 1.6) / 3
cards = [BOTY + 1.6 + k * (ch + 1.6) for k in (2, 1, 0)]
card(LX + 1.6, cards[0], LW_ - 3.2, ch, "Methane (hourly)")
a = thumb(LX + 4.0, cards[0] + 1.6, LW_ - 8.0, ch - 6.2); a.plot(ch4.index, ch4.values, lw=0.55, c="#2f6fb3"); a.margins(x=0)
card(LX + 1.6, cards[1], LW_ - 3.2, ch, "Wind")
a = fig.add_axes([(LX + LW_ / 2 - (ch - 6.0) / 2) / W, (cards[1] + 1.0) / H, (ch - 6.0) / W, (ch - 6.0) / H], projection="polar")
cnt, edges = np.histogram(wd, bins=np.arange(0, 361, 22.5)); th = np.deg2rad(edges[:-1] + 11.25)
a.bar(th, cnt / cnt.max(), width=np.deg2rad(20), color="#7fb0dd", edgecolor="white", lw=0.3); a.set_theta_zero_location("N"); a.set_theta_direction(-1)
a.set_xticks([]); a.set_yticks([]); a.spines["polar"].set_linewidth(0.4); a.spines["polar"].set_color("#9cc0e3"); a.patch.set_alpha(0)
card(LX + 1.6, cards[2], LW_ - 3.2, ch, "Stability ($T_{90}-T_{20}$)")
a = thumb(LX + 4.0, cards[2] + 1.6, LW_ - 8.0, ch - 6.2); a.axhline(0, c="#c9c9c9", lw=0.4); a.plot(stab.index, stab.values, lw=0.55, c="#d9822b"); a.margins(x=0)

# ------------------------------------------------ middle panels
MX, MW = 40.0, 95.0
big_arrow(LX + LW_ + 0.6, 57.0); big_arrow(MX + MW + 0.6, 57.0)
# (a) temporal design
AY, AH = 80.5, 21.0
rbox(MX, AY, MW, AH, LAV["fc"], LAV["ec"]); txt(MX + 3.0, AY + AH - 3.4, "(a) Temporal design", size=7.6, weight="bold", ha="left")
t0, t1 = pd.Timestamp("2021-01-01"), pd.Timestamp("2026-10-01"); X0, X1 = MX + 4.0, MX + MW - 4.0
tx = lambda d: X0 + (X1 - X0) * (pd.Timestamp(d) - t0).days / (t1 - t0).days
by = AY + 9.6
rbox(tx("2021-01-01"), by, tx("2025-12-02") - tx("2021-01-01"), 3.6, C_DEV, "none", r=0.8, z=2); txt((tx("2021-01-01") + tx("2025-12-02")) / 2, by + 1.8, "Development", size=6.4)
rbox(tx("2021-01-01"), by - 4.3, tx("2024-01-01") - tx("2021-01-01"), 3.0, C_REF, C_DEV, lw=0.5, r=0.8, z=2); txt((tx("2021-01-01") + tx("2024-01-01")) / 2, by - 2.8, "Reference baselines", size=6.0)
rbox(tx("2026-01-01"), by, tx("2026-10-01") - tx("2026-01-01"), 3.6, C_CONF, "none", r=0.8, z=2); txt((tx("2026-01-01") + tx("2026-10-01")) / 2, by - 2.6, "Confirmation", size=6.2, color=C_CONF, weight="bold")
xf = tx("2025-12-17"); ax.plot([xf, xf], [by - 0.6, by + 7.2], c=C_FRZ, lw=1.0, zorder=3); txt(xf - 1.0, by + 5.6, "Protocol frozen", size=6.2, color=C_FRZ, ha="right", va="center", weight="bold")
for yr in range(2021, 2027):
    txt(tx(f"{yr}-01-01"), AY + 2.4, str(yr), size=5.8, color=MUTE)
# (b) prespecified estimands
BY_, BH = 37.5, 40.5
rbox(MX, BY_, MW, BH, PEACH["fc"], PEACH["ec"]); txt(MX + 3.0, BY_ + BH - 3.4, "(b) Prespecified estimands", size=7.6, weight="bold", ha="left")
cw_, gap = 29.0, 2.0; cx0 = MX + (MW - 3 * cw_ - 2 * gap) / 2
specs = [("H1|Stability association", r"$y_t=\beta\,S_t+\gamma\,\log U_t+\alpha_{c(t)}$"),
         ("H2|Directional coupling", r"$D=\sum_{\ell=1}^{3}w_\ell\,(\rho_\ell^{\,A}-\rho_\ell^{\,R})$"),
         ("H3|Regime composition", r"$\Delta r=\Delta_{\mathrm{comp}}+\Delta_{\mathrm{within}}$")]
for k, (title, eq) in enumerate(specs):
    x = cx0 + k * (cw_ + gap); y = BY_ + 3.0; h = BH - 9.5
    rbox(x, y, cw_, h, "#ffffff", "#e8cfb2", lw=0.6, r=1.8, z=2)
    hid, hname = title.split("|"); txt(x + cw_ / 2, y + h - 2.8, hid, size=7.2, weight="bold", color=C_CONF); txt(x + cw_ / 2, y + h - 6.0, hname, size=6.3, weight="bold")
    txt(x + cw_ / 2, y + 4.2, eq, size=6.6)
    gx, gy, gw, gh = x + 3.0, y + 9.6, cw_ - 6.0, h - 18.6          # glyph area
    if k == 0:                                                       # association: REAL hourly AMS 1 CH4 vs AMS 5 stability, 13-19 Jan 2025
        g = thumb(gx, gy, gw, gh); jj = pd.concat([stab, ch4], axis=1).dropna(); xs_, ys_ = jj.iloc[:, 0].values, jj.iloc[:, 1].values
        g.scatter(xs_, ys_, s=1.3, c="#9cb8d6", lw=0); b1, b0 = np.polyfit(xs_, ys_, 1); xl = np.array([xs_.min(), xs_.max()]); g.plot(xl, b0 + b1 * xl, c="#2171b5", lw=0.9)
        txt(gx + gw / 2, gy - 1.3, "CH$_4$ vs stability (hourly)", size=5.6, color=MUTE)
    if k == 1:                                                       # station pair + aligned / reversed wind sectors (no transport arrows)
        cxp, cyp = gx + gw / 2, gy + gh / 2; dx = gw * 0.26
        ax.add_patch(Wedge((cxp, cyp), gh * 0.55, 140, 220, fc="#cfe3f5", ec="none", zorder=2.5))
        ax.add_patch(Wedge((cxp, cyp), gh * 0.55, -40, 40, fc="#f6dcc4", ec="none", zorder=2.5))
        ax.plot([cxp - dx, cxp + dx], [cyp, cyp], c="#8c8c8c", lw=0.6, zorder=3)
        for sx, lab in ((cxp - dx, "$i$"), (cxp + dx, "$j$")):
            ax.add_patch(Circle((sx, cyp), 1.1, fc=C_CONF, ec="white", lw=0.4, zorder=4)); txt(sx, cyp - 2.6, lab, size=6.2)
        txt(cxp - gh * 0.45, cyp + gh * 0.42, "aligned", size=5.6, color="#2f6fb3"); txt(cxp + gh * 0.45, cyp + gh * 0.42, "reversed", size=5.6, color="#c06a22")
    if k == 2:                                                       # composition: REAL AMS 5 stability-tercile shares, Jan-Sep 2021 vs 2025
        g = thumb(gx + 3.0, gy, gw - 6.0, gh); cols = ["#9ecae1", "#c6dbef", "#fdd0a2"]
        for b, yr in enumerate((2021, 2025)):
            sv = S_ALL.loc[f"{yr}-01-01":f"{yr}-09-30"].dropna(); fr = np.bincount(np.digitize(sv, CUTS), minlength=3) / len(sv); bottom = 0
            for c_ in range(3): g.bar(b, fr[c_], bottom=bottom, color=cols[c_], width=0.55, ec="white", lw=0.4); bottom += fr[c_]
        g.set_xlim(-0.6, 1.6); g.set_ylim(0, 1.02); txt(gx + gw / 2, gy - 1.3, "stability regimes, 2021 vs 2025", size=5.6, color=MUTE)
# (c) inference and decision
CY, CH = 14.2, 21.6
rbox(MX, CY, MW, CH, GREEN["fc"], GREEN["ec"]); txt(MX + 3.0, CY + CH - 3.4, "(c) Inference and decision", size=7.6, weight="bold", ha="left")
cells = [("Block bootstrap", "14-day blocks"), ("Wind-shift reference", r"$p=\dfrac{1+\#\{D_k\geq D\}}{K+1}$"), ("Frozen decision rules", "applied once to 2026")]
cw2 = (MW - 8.0 - 2 * 3.0) / 3
for k, (t, s) in enumerate(cells):
    x = MX + 4.0 + k * (cw2 + 3.0); rbox(x, CY + 2.6, cw2, CH - 9.0, "#ffffff", "#bcdab9", lw=0.6, r=1.8, z=2)
    txt(x + cw2 / 2, CY + CH - 8.6, t, size=6.4, weight="bold"); txt(x + cw2 / 2, CY + (8.0 if k == 1 else 7.0), s, size=5.9 if k == 1 else 6.1, color=INK)
    if k == 1: txt(x + cw2 / 2, CY + 4.0, "$K = 246$ whole-day shifts", size=5.6, color=MUTE)
    if k < 2: arrow(x + cw2 + 0.3, CY + 2.6 + (CH - 9.0) / 2, x + cw2 + 2.7, CY + 2.6 + (CH - 9.0) / 2)
arrow(MX + MW / 2, BY_ - 0.2, MX + MW / 2, CY + CH + 0.3); arrow(MX + MW / 2, AY - 0.2, MX + MW / 2, BY_ + BH + 0.3)

# ------------------------------------------------ right: outputs
RX = MX + MW + 4.6; RW = W - RX - 2.0
header_panel(RX, BOTY, RW, TOPY - BOTY, "Outputs", BLUE)
card(RX + 1.6, cards[0], RW - 3.2, ch, "Estimates")
g = thumb(RX + 6.0, cards[0] + 2.4, RW - 12.0, ch - 7.4)                # neutral glyph (no hypothesis result implied)
g.plot([0.25, 0.85], [0, 0], c="#2171b5", lw=1.0); g.scatter([0.55], [0], s=7, c="#2171b5", zorder=3); g.axvline(0, c="#8c8c8c", lw=0.5, ls=(0, (2, 1.5)))
g.set_xlim(-0.25, 1.1); g.set_ylim(-1, 1); txt(RX + RW / 2, cards[0] + 1.4, "estimate, 95% CI vs 0", size=5.6, color=MUTE)
card(RX + 1.6, cards[1], RW - 3.2, ch, "Null reference")
g = thumb(RX + 4.5, cards[1] + 2.4, RW - 9.0, ch - 7.2); g.hist(pooled_null, bins=24, color="#9ecae1", ec="white", lw=0.3)
g.axvline(0, c="#8c8c8c", lw=0.4); txt(RX + RW / 2, cards[1] + 1.4, "pooled $D$ under 246 shifts", size=5.6, color=MUTE)
card(RX + 1.6, cards[2], RW - 3.2, ch, "Decisions")
for k, (s, c_) in enumerate([("Confirmed", "#2171b5"), ("Not confirmed", "#8c8c8c"), ("Not evaluable", "#bdbdbd")]):
    yy = cards[2] + ch - 9.0 - k * 4.4; rbox(RX + 5.0, yy - 1.4, RW - 10.0, 3.0, "#ffffff", c_, lw=0.7, r=1.2, z=3); txt(RX + RW / 2, yy + 0.1, s, size=5.9, color=c_)

# ------------------------------------------------ bottom: post-confirmation analyses
rbox(2.0, 1.0, W - 4.0, 10.6, "#fbfbfb", "#c7ced6", lw=0.7, r=2.0, ls=(0, (3, 2)))
txt(5.0, 6.3, "Post-confirmation analyses", size=6.8, weight="bold", ha="left"); txt(5.0, 3.6, "exploratory; decisions unchanged", size=5.8, color=MUTE, ha="left")
items = ["Synthetic null\ncalibration and power", "Falsification:\nadvected shared signal", "Season-restricted\nshift references", "Transport diagnostics\n(development)"]
xs = np.linspace(44.0, W - 3.0, len(items) + 1)
for k, s in enumerate(items):
    rbox(xs[k] + 1.0, 2.4, xs[k + 1] - xs[k] - 2.0, 8.2, "#ffffff", "#d4dae0", lw=0.5, r=1.4, z=2); txt((xs[k] + xs[k + 1]) / 2, 6.5, s, size=5.9)
for ext in ("pdf", "svg"): fig.savefig(OUT / f"fig03_framework.{ext}", metadata={"Date": None} if ext == "svg" else {"CreationDate": None})
fig.savefig(OUT / "fig03_framework_600dpi.png", dpi=600); print("fig03 v2 written", W, "x", H, "mm")
