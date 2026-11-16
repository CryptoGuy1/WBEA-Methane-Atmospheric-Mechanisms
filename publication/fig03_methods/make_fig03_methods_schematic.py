"""Figure 3 (methods schematic): (a) study timeline, (b) estimator comparison grid H1-H3, (c) post-confirmation checks.
Pure vector text and shapes; no data plots, icons or generated imagery. Rules and equations match the frozen code
(src/wbea/e08.py, experiments/E08_confirmation/run_e08.py at tag protocol-freeze) and Supplement Eqs. S1-S9."""
import pathlib, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
OUT = pathlib.Path(__file__).resolve().parent
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "dejavusans", "pdf.fonttype": 42, "svg.fonttype": "none"})
NAVY, BLUE, TEAL, ORANGE, GREY, LINE = "#0b3a5b", "#2171b5", "#1b7f8c", "#c8621b", "#5f6b78", "#c9d6e3"
W, H = 174.5, 112.0
fig = plt.figure(figsize=(W / 25.4, H / 25.4)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
def box(x, y, w, h, fc, ec="none", r=1.2, lw=0.6): ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw))
def lab(x, y, s): ax.text(x, y, f"({s})", fontsize=8.5, fontweight="bold", color="black", ha="left", va="top")

# (a) timeline
lab(1.0, H - 1.0, "a")
segs = [(8.0, 46.0, "#e3e8ee", NAVY, "Development, 2021–2025", "exploratory; methods built and tested"),
        (64.0, 44.0, "#d6e6f5", NAVY, "Confirmation, Jan–Sep 2026", "frozen protocol, run once"),
        (118.0, 54.5, "#eef2f5", NAVY, "Post-confirmation diagnostics", "cannot alter registered decisions")]
yt = H - 24.0
for x, w, fc, tc, t1, t2 in segs:
    box(x, yt, w, 10.5, fc); ax.text(x + w / 2, yt + 7.0, t1, fontsize=7.6, fontweight="bold", color=tc, ha="center", va="center")
    ax.text(x + w / 2, yt + 3.1, t2, fontsize=6.6, color=GREY, ha="center", va="center")
for x0, x1 in ((54.0, 64.0), (108.0, 118.0)): ax.annotate("", xy=(x1 - 0.6, yt + 5.25), xytext=(x0 + 0.6, yt + 5.25), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.2))
ax.add_patch(Polygon([[59.0, yt + 13.6], [61.0, yt + 11.6], [59.0, yt + 9.6], [57.0, yt + 11.6]], closed=True, fc=ORANGE, ec="none"))
ax.text(59.0, yt + 15.6, "Protocol and code frozen (11 Nov 2026) before 2026 data were opened", fontsize=6.6, color=ORANGE, ha="center", va="bottom", fontweight="bold")

# (b) estimator comparison grid
lab(1.0, H - 29.0, "b")
cols = [("H1  Stability association", TEAL), ("H2  Wind-conditioned directionality", BLUE), ("H3  Regime composition", ORANGE)]
x0, cw, gap = 24.0, 49.0, 1.5; ytop = H - 33.0; hh = 6.0
rows = [("Input", 14.5), ("Statistic", 13.0), ("Reference", 11.0), ("Registered\ndecision", 15.0)]
for k, (t, c) in enumerate(cols):
    x = x0 + k * (cw + gap); box(x, ytop - hh, cw, hh, c, r=1.0); ax.text(x + cw / 2, ytop - hh / 2, t, fontsize=6.6, fontweight="bold", color="white", ha="center", va="center")
cells = {
 0: ["Network CH$_4$ anomaly $Y$ (median of\n7 core stations); stability $S$ =\nAMS 5 $T_{90}-T_{20}$, standardised",
     "Leave-pair-out residual changes $\\Delta R$;\naligned ($A$) and reversed ($B$) wind hours\nfor 21 pairs within 30 km",
     "Station P95 excursion rates in\n18 regimes (stability × wind ×\nday/night); year-to-year contrasts"],
 1: ["$Y_t=\\alpha_{ymh}+\\beta_S S_t+\\beta_U\\log(U_t+0.5)+\\varepsilon_t$",
     "$D=\\sum_{ij} a_{ij}\\sum_{\\ell=1}^{3} w_{ij\\ell}\\,[q_{ij\\ell}(A)-q_{ij\\ell}(B)]$",
     "$\\theta=\\sum_j C_j\\,\\Delta R_j\\;/\\;\\sum_j \\Delta R_j^{2}$"],
 2: ["14-day block bootstrap\n(2,000 replicates)",
     "All whole-day circular wind shifts\n($K$ = 246); $a_{ij}\\propto 1/\\mathrm{Var}_k(D_{ij}^{(k)})$",
     "14-day block bootstrap;\n$C_j$ from Kitagawa decomposition"],
 3: ["95% CI of $\\beta_S$ above 0; next-day\ncontrol not both significant and\n$|\\beta_{NC}|\\geq 0.5\\,\\beta_S^{\\mathrm{joint}}$",
     "$p=(1+\\#\\{D^{(k)}\\geq D\\})/(K+1)<0.05$;\n$D>0$ with wind timing ±1 h;\nlag-centroid ordering",
     "95% CI of $\\theta$ excludes 0"]}
y = ytop - hh - 1.2
for r, (rname, rh) in enumerate(rows):
    y -= rh
    ax.text(x0 - 1.5, y + rh / 2, rname, fontsize=7.2, fontweight="bold", color=NAVY, ha="right", va="center", linespacing=1.1)
    for k in range(3):
        x = x0 + k * (cw + gap); box(x, y, cw, rh - 0.8, "white" if r != 1 else "#f4f7fa", ec=LINE, r=0.8)
        ax.text(x + cw / 2, y + (rh - 0.8) / 2, cells[r][k], fontsize=7.4 if r == 1 else 6.6, color="#1f2d3a", ha="center", va="center", linespacing=1.25)
ybot = y

# (c) post-confirmation checks
lab(1.0, ybot - 2.0, "c")
checks = [("Synthetic calibration\nand falsification", "Suppl. Section 8"), ("Season-restricted\nshift references", "Suppl. Sections 9.1–9.2"),
          ("Cross-year empirical\nnegative controls", "Suppl. Section 9.3"), ("Matched-pair\ncomparability", "Suppl. Section 10")]
yc = ybot - 15.5; cw4 = (W - x0 - 1.5 - 3 * 1.5) / 4
ax.text(x0 - 1.5, yc + 6.0, "Post-\nconfirmation\nchecks", fontsize=7.2, fontweight="bold", color=NAVY, ha="right", va="center", linespacing=1.1)
for k, (t, s) in enumerate(checks):
    x = x0 + k * (cw4 + 1.5); box(x, yc, cw4, 12.0, "#eef2f5", ec=LINE, r=0.8)
    ax.text(x + cw4 / 2, yc + 7.4, t, fontsize=7.0, fontweight="bold", color=NAVY, ha="center", va="center", linespacing=1.15)
    ax.text(x + cw4 / 2, yc + 2.4, s, fontsize=6.4, color=GREY, ha="center", va="center")
for ext in ("pdf", "svg"): fig.savefig(OUT / f"fig03_methods_schematic.{ext}")
fig.savefig(OUT / "fig03_methods_schematic.png", dpi=600); print("bottom margin (mm):", round(yc, 1))
