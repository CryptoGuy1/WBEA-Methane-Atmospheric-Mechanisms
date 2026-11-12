"""Fig. 3 (v3): equation-led analysis framework. Panel structure: data inputs | (a) analytical framework, (b) confirmatory
analysis, (c) methodological evaluation | outputs. Input thumbnails use REAL development data (AMS 1 CH4 and AMS 5
T90-T20, 13-19 Jan 2025; AMS 5 wind rose 2021-2025; official station coordinates and the 21 frozen pairs). No results
are shown. The only schematic sketch is the H2 station pair with aligned/reversed wind sectors. Vector, 174.5 mm."""
import sys, pathlib, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "section2"))
import common
from common import plt, MM
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Wedge, Polygon, Circle
from wbea.io import load_dev
from wbea.wind import composite
OUT = common.ROOT / "manuscript/figures/section3"; ROOT = common.ROOT
W, H = 174.5, 104.0
INK, MUTE, ACC = "#1f2d3d", "#5f6b78", "#2171b5"
BLUE = dict(fc="#f3f8fd", ec="#9cc0e3", hd="#d6e7f7"); LAV = dict(fc="#f6f3fb", ec="#b7a6d8", in_="#ebe5f6")
SKY = dict(fc="#f2f7fc", ec="#9fbfe0", in_="#e2edf9"); GRN = dict(fc="#f1f8ef", ec="#9cc59a", in_="#e3f1e0")
fig = plt.figure(figsize=(W * MM, H * MM)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")

def rbox(x, y, w, h, fc, ec, lw=0.8, r=2.0, ls="-", z=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))
def txt(x, y, s, size=6.4, color=INK, ha="center", va="center", weight="normal", z=6):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, fontweight=weight, zorder=z, linespacing=1.2)
def arrow(x0, y0, x1, y1, color="#3d4b5c", lw=0.8, ms=7):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=ms, lw=lw, color=color, shrinkA=0, shrinkB=0, zorder=4))
def big_arrow(x, y, w=3.0, h=5.0, color="#a9b4c0"):
    ax.add_patch(Polygon([(x, y - h * .28), (x + w * .55, y - h * .28), (x + w * .55, y - h / 2), (x + w, y), (x + w * .55, y + h / 2), (x + w * .55, y + h * .28), (x, y + h * .28)],
                         closed=True, fc=color, ec="none", zorder=3))
def thumb(x, y, w, h, polar=False):
    a = fig.add_axes([x / W, y / H, w / W, h / H], projection="polar" if polar else None); a.patch.set_alpha(0)
    if not polar:
        for sp in a.spines.values(): sp.set_visible(False)
    a.set_xticks([]); a.set_yticks([]); return a
def column(x, y, w, h, title):
    rbox(x, y, w, h, BLUE["fc"], BLUE["ec"])
    ax.add_patch(FancyBboxPatch((x + 0.4, y + h - 6.6), w - 0.8, 6.2, boxstyle="round,pad=0,rounding_size=1.8", fc=BLUE["hd"], ec="none", zorder=1.5))
    txt(x + w / 2, y + h - 3.5, title, size=7.6, weight="bold")
def card(x, y, w, h, title, sub=None):
    rbox(x, y, w, h, "#ffffff", "#c9dbef", lw=0.6, r=1.6, z=2); txt(x + w / 2, y + h - 2.8, title, size=6.4, weight="bold")
    if sub: txt(x + w / 2, y + h - 5.6, sub, size=5.6, color=MUTE)
def panel(x, y, w, h, title, st):
    rbox(x, y, w, h, st["fc"], st["ec"]); txt(x + 2.6, y + h - 3.3, title, size=7.4, weight="bold", ha="left")

# ---------------- real data
P = load_dev(["AMS 1", "AMS 5"]); wk = slice("2025-01-13", "2025-01-19")
ch4 = P["AMS 1"]["CH4 (ppm)"].loc[wk]; stab = (P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"]).loc[wk]
cw = composite(P["AMS 5"]); wd = (np.degrees(np.arctan2(-cw.u, -cw.v)) % 360)[cw.ws >= 1.0].dropna()
stn = pd.read_csv(ROOT / "manuscript/data/section2/stations_study.csv").set_index("station_id"); prs = pd.read_csv(ROOT / "manuscript/data/section2/pairs_frozen.csv")

# ---------------- layout
LX, LW_ = 1.5, 30.0; RW_ = 30.0; RX = W - 1.5 - RW_; MX = LX + LW_ + 4.4; MW = RX - 4.4 - MX
TOP, BOT = 102.5, 1.5
column(LX, BOT, LW_, TOP - BOT, "Data inputs"); column(RX, BOT, RW_, TOP - BOT, "Outputs")
ch = (TOP - BOT - 7.6 - 5 * 1.4) / 4; cy = [BOT + 1.4 + k * (ch + 1.4) for k in (3, 2, 1, 0)]
# inputs
card(LX + 1.4, cy[0], LW_ - 2.8, ch, "Hourly CH$_4$", "WBEA, 12 stations")
a = thumb(LX + 3.6, cy[0] + 1.5, LW_ - 7.2, ch - 8.2); a.plot(ch4.index, ch4.values, lw=0.55, c="#2f6fb3"); a.margins(x=0)
card(LX + 1.4, cy[1], LW_ - 2.8, ch, "Wind", "speed and direction")
rr = ch - 8.6; a = thumb(LX + LW_ / 2 - rr / 2, cy[1] + 1.4, rr, rr, polar=True)
cnt, edges = np.histogram(wd, bins=np.arange(0, 361, 22.5)); a.bar(np.deg2rad(edges[:-1] + 11.25), cnt / cnt.max(), width=np.deg2rad(20), color="#7fb0dd", ec="white", lw=0.3)
a.set_theta_zero_location("N"); a.set_theta_direction(-1); a.spines["polar"].set_linewidth(0.4); a.spines["polar"].set_color("#9cc0e3")
card(LX + 1.4, cy[2], LW_ - 2.8, ch, "Stability", "AMS 5 $T_{90}-T_{20}$; ERA5 BLH")
a = thumb(LX + 3.6, cy[2] + 1.5, LW_ - 7.2, ch - 8.2); a.axhline(0, c="#cfcfcf", lw=0.4); a.plot(stab.index, stab.values, lw=0.55, c="#d9822b"); a.margins(x=0)
card(LX + 1.4, cy[3], LW_ - 2.8, ch, "Network geometry", "station pairs (n = 21)")
a = thumb(LX + 3.6, cy[3] + 1.2, LW_ - 7.2, ch - 7.8)
core = [s_ for s_ in stn.index if s_ not in ("AMS 14", "AMS 18")]                  # AMS 14/18 have no eligible pair; full map in Fig. 1
lon, lat = stn.longitude_deg_e[core], stn.latitude_deg_n[core]; kx = np.cos(np.deg2rad(57.0))
for _, r in prs.iterrows(): a.plot([lon[r.i] * kx, lon[r.j] * kx], [lat[r.i], lat[r.j]], c="#b5b5b5", lw=0.35)
a.scatter(lon * kx, lat, s=4.0, c=ACC, lw=0, zorder=3); a.set_aspect("equal", adjustable="datalim")

# ---------------- (a) analytical framework
AY, AH = 52.0, TOP - 52.0
panel(MX, AY, MW, AH, "(a) Analytical framework", LAV)
steps = ["Quality control\nand eligibility", "Temporal\npartitioning", "Background\nadjustment", "Prespecified\nestimators"]
sw = (MW - 5.2 - 3 * 4.0) / 4; sy = AY + AH - 13.0
for k, s in enumerate(steps):
    x = MX + 2.6 + k * (sw + 4.0); rbox(x, sy, sw, 7.0, LAV["in_"], LAV["ec"], lw=0.6, r=1.4, z=2); txt(x + sw / 2, sy + 3.5, s, size=6.1)
    if k < 3: arrow(x + sw + 0.4, sy + 3.5, x + sw + 3.6, sy + 3.5)
txt(MX + 2.6 + 2 * (sw + 4.0) + sw / 2, sy - 2.6, r"$R_i(t)=X_i(t)-\mathrm{median}_{k\neq i,j}\,X_k(t)$", size=5.8, color=MUTE)
ew = (MW - 5.2 - 2 * 2.4) / 3; ey, eh = AY + 2.4, sy - 7.4 - (AY + 2.4)
H_ = [("H1", "Stability association", [r"$y_t=\beta S_t+\gamma\log(U_t+0.5)$", r"$\qquad+\,\alpha_{c(t)}+\varepsilon_t$", "", r"$c(t)$: year $\times$ month $\times$ hour"]),
      ("H2", "Directional coupling", [r"$\rho_\ell=r[\Delta R_i(t-\ell),\Delta R_j(t)]$", r"$\qquad-\,r[\Delta R_j(t-\ell),\Delta R_i(t)]$",
                                     r"$D_{ij}=\Sigma_{\ell=1}^{3}\,w_\ell\,[\rho_\ell(A)-\rho_\ell(R)]$"]),
      ("H3", "Regime composition", [r"$\Delta r=\Sigma_g\,\Delta\pi_g\,\bar{q}_g+\Sigma_g\,\bar{\pi}_g\,\Delta q_g$", "", r"$s=\Sigma_k\,c_k t_k\,/\,\Sigma_k\,t_k^{2}$", "composition share"])]
for k, (hid, name, eqs) in enumerate(H_):
    x = MX + 2.6 + k * (ew + 2.4); rbox(x, ey, ew, eh, "#ffffff", "#d3c8ea", lw=0.6, r=1.6, z=2)
    txt(x + ew / 2, ey + eh - 2.8, hid, size=7.2, weight="bold", color=ACC); txt(x + ew / 2, ey + eh - 6.0, name, size=6.2, weight="bold")
    if k == 1:                                                         # schematic: station pair with aligned / reversed wind sectors
        cxp, cyp, rr = x + ew / 2, ey + eh - 11.6, 3.6
        ax.add_patch(Wedge((cxp, cyp), rr, 140, 220, fc="#cfe3f5", ec="none", zorder=2.5)); ax.add_patch(Wedge((cxp, cyp), rr, -40, 40, fc="#f6dcc4", ec="none", zorder=2.5))
        ax.plot([cxp - 3.4, cxp + 3.4], [cyp, cyp], c="#8c8c8c", lw=0.6, zorder=3)
        for sx, lab in ((cxp - 3.4, "$i$"), (cxp + 3.4, "$j$")): ax.add_patch(Circle((sx, cyp), 0.95, fc=ACC, ec="white", lw=0.4, zorder=4)); txt(sx, cyp - 2.2, lab, size=5.8)
        txt(cxp - 8.6, cyp, "$A$", size=6.2, color="#2f6fb3"); txt(cxp + 8.6, cyp, "$R$", size=6.2, color="#c06a22")
        y0 = cyp - 5.6
    else:
        y0 = ey + eh - 11.2
    for j, e in enumerate(eqs):
        if e: txt(x + ew / 2, y0 - j * 3.7, e, size=5.9 if j < 3 else 5.6, color=INK if j < 3 or k == 1 else MUTE)

# ---------------- (b) confirmatory analysis
BYb, BH = 27.5, 22.4
panel(MX, BYb, MW, BH, "(b) Confirmatory analysis", SKY)
fy, fh = BYb + 2.4, BH - 8.2
boxes = [("Protocol frozen", "after development"), ("Confirmation", "Jan–Sep 2026, single run")]
bw = 27.0
for k, (t, s) in enumerate(boxes):
    x = MX + 2.6 + k * (bw + 4.0); rbox(x, fy, bw, fh, SKY["in_"], SKY["ec"], lw=0.6, r=1.4, z=2); txt(x + bw / 2, fy + fh / 2 + 1.8, t, size=6.3, weight="bold"); txt(x + bw / 2, fy + fh / 2 - 2.0, s, size=5.8, color=MUTE)
    arrow(x + bw + 0.4, fy + fh / 2, x + bw + 3.6, fy + fh / 2)
cx0 = MX + 2.6 + 2 * (bw + 4.0); cwid = MX + MW - 2.6 - cx0
rbox(cx0, fy, cwid, fh, "#ffffff", SKY["ec"], lw=0.6, r=1.4, z=2)
checks = [r"Block-bootstrap CI (H1, H3)", r"$p=\dfrac{1+\#\{D^{(k)}\geq D\}}{K+1},\ K=246$ (H2)", "< 50% valid CH$_4$: station excluded"]
for j, c_ in enumerate(checks):
    yy = fy + fh - 2.6 - j * 4.6 - (0.6 if j == 2 else 0); txt(cx0 + 2.0, yy, "\u2713", size=6.6, color=ACC, ha="left"); txt(cx0 + 5.0, yy, c_, size=5.9, ha="left")

# ---------------- (c) methodological evaluation
CY, CH = BOT + 0.0, 24.0
panel(MX, CY, MW, CH, "(c) Methodological evaluation (post-confirmation)", GRN)
ew2 = (MW - 5.2 - 2.4) / 2
ev = [("Synthetic calibration and falsification", [r"$\hat{\alpha}=\#\{p<0.05\}\,/\,n$ under null scenarios", "power; advected-signal falsification"]),
      ("Season-restricted shift references", [r"$U^{(k)}(t)=U(a_b+(t-a_b-24k)\ \mathrm{mod}\ L_b)$", "shifts within calendar-based seasonal blocks $b$"])]
for k, (t, eqs) in enumerate(ev):
    x = MX + 2.6 + k * (ew2 + 2.4); rbox(x, CY + 2.4, ew2, CH - 8.6, "#ffffff", "#bcdab9", lw=0.6, r=1.4, z=2)
    txt(x + ew2 / 2, CY + CH - 9.2, t, size=6.3, weight="bold")
    txt(x + ew2 / 2, CY + 8.4, eqs[0], size=6.0); txt(x + ew2 / 2, CY + 4.6, eqs[1], size=5.6, color=MUTE)

# ---------------- outputs (quantities, no results)
outs = [("H1", r"$\hat{\beta}$  with 95% CI", "ppm per SD of $S$"), ("H2", r"$D$  and finite-shift $p$", "pooled over eligible pairs"),
        ("H3", r"$\hat{s}$  with 95% CI", "composition share"), (None, "Decision", None)]
for k, (hid, q, sub) in enumerate(outs):
    y = cy[k]; card(RX + 1.4, y, RW_ - 2.8, ch, "")
    if hid:
        txt(RX + RW_ / 2, y + ch - 3.4, hid, size=7.4, weight="bold", color=ACC); txt(RX + RW_ / 2, y + ch / 2 - 0.6, q, size=6.6); txt(RX + RW_ / 2, y + 3.0, sub, size=5.6, color=MUTE)
    else:
        txt(RX + RW_ / 2, y + ch - 3.4, q, size=6.4, weight="bold")
        for j, (s, c_) in enumerate([("Confirmed", ACC), ("Not confirmed", "#7a7a7a"), ("Not evaluable", "#b0b0b0")]):
            yy = y + ch - 9.2 - j * 3.9; rbox(RX + 5.0, yy - 1.3, RW_ - 10.0, 2.8, "#ffffff", c_, lw=0.7, r=1.1, z=3); txt(RX + RW_ / 2, yy + 0.1, s, size=5.8, color=c_)
big_arrow(LX + LW_ + 0.7, 52.0); big_arrow(MX + MW + 0.7, 52.0)
arrow(MX + MW / 2, AY - 0.2, MX + MW / 2, BYb + BH + 0.2)
for ext in ("pdf", "svg"): fig.savefig(OUT / f"fig03_framework.{ext}", metadata={"Date": None} if ext == "svg" else {"CreationDate": None})
fig.savefig(OUT / "fig03_framework_600dpi.png", dpi=600); print("fig03 v3 written", W, "x", H, "mm")
