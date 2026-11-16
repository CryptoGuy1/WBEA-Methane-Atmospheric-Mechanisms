"""E15 tables and figure (reads saved results only)."""
import pathlib, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = pathlib.Path(__file__).resolve().parent; R = HERE / "results"; F = HERE / "figures"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.linewidth": 0.6, "pdf.fonttype": 42, "svg.fonttype": "none"})
MM = 1 / 25.4; T = pd.read_csv(R / "comparison_table.csv").set_index("id"); S = pd.read_csv(R / "shared_pairs_A5_vs_A1.csv", index_col=0)
P = pd.read_csv(R / "pair_level_all.csv"); S["km"] = P[P.analysis == "A5"].set_index("pair").km
# summary table (markdown + csv)
order = ["A0", "A2", "A2b", "A3", "A4", "A5"] + [f"A5y_{y}" for y in range(2021, 2026)] + [f"A3y_{y}" for y in range(2021, 2026)] + ["A1", "A1r", "A7", "A6"]
status = {"A0": "original (published)", "A1": "original (frozen confirmation)"}
tab = T.reindex(order).reset_index()
tab["status"] = [status.get(i, "post-confirmation exploratory") for i in tab.id]
tab.to_csv(R / "summary_table.csv", index=False)
md = ["| ID | Status | Window | Universe | Pairs | Reference | Pooled D | Pooled null SD | z | p | Effective pairs |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for r in tab.itertuples():
    f = lambda v, d=4: "n/a" if pd.isna(v) else f"{v:.{d}f}"
    md.append(f"| {r.id} | {r.status} | {r.window} | {r.universe} | {r.pairs} | {r.reference} | {f(r.pooled_D)} | {f(r.pooled_null_sd)} | {f(r.z, 2)} | {f(r.p)} | {f(r.eff_pairs, 1)} |")
(R / "summary_table.md").write_text("\n".join(md) + "\n\nA6 not evaluable: undefined shifted-wind surrogates for the six AMS 2 pairs (DEVIATIONS D2).\n")

fig = plt.figure(figsize=(174.5 * MM, 80 * MM)); axa = fig.add_axes([0.18, 0.15, 0.36, 0.80]); axb = fig.add_axes([0.645, 0.15, 0.255, 0.80])
for a, l in ((axa, "(a)"), (axb, "(b)")):
    a.text(-0.02, 1.0, l, transform=a.transAxes, fontweight="bold", fontsize=8, ha="right", va="bottom")
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
    a.tick_params(length=2.5, width=0.5)
rows = [("A0", "Published development", "#4d4d4d", "o"), ("A2", "+ all admissible shifts", "#7f7f7f", "o"),
        ("A3", "+ Jan–Sep pooled window", "#7f7f7f", "o"), ("A4", "+ 21 shared pairs", "#7f7f7f", "o"), ("A5", "+ 11-station universe", "#7f7f7f", "o")] + \
       [(f"A5y_{y}", f"Jan–Sep {y}", "#9e9e9e", "s") for y in range(2021, 2026)] + [("A1", "2026 confirmation", "#2171b5", "D")]
ys = np.arange(len(rows))[::-1].astype(float); ys[:5] += 0.6; ys[-1] -= 0.4
for y, (aid, lab, c, m) in zip(ys, rows):
    axa.plot(T.pooled_D[aid], y, m, c=c, ms=4.4 if m != "D" else 5.2, mfc=c if m != "s" else "white", mec=c, mew=1.0)
axa.set_yticks(ys, [r[1] for r in rows], fontsize=6.4); axa.tick_params(axis="y", length=0)
axa.axhline((ys[4] + ys[5]) / 2, c="#d9d9d9", lw=0.6); axa.axhline((ys[-2] + ys[-1]) / 2, c="#d9d9d9", lw=0.6)
axa.set_xlim(0.05, 0.32); axa.set_xlabel("Pooled directional statistic $D$ (dimensionless)")
axa.get_yticklabels()[-1].set_color("#2171b5"); axa.get_yticklabels()[-1].set_fontweight("bold")
sc = axb.scatter(S.D_dev, S.D_2026, c=S.km, cmap="viridis", s=18 + 260 * S.w_2026, edgecolors="white", linewidths=0.4, zorder=3)
axb.plot([0, 0.8], [0, 0.8], c="#9e9e9e", lw=0.7, ls=(0, (2, 2)), zorder=1); axb.set_xlim(0, 0.78); axb.set_ylim(0, 0.78)
axb.set_xlabel("$D_{ij}$, development (Jan–Sep pooled)"); axb.set_ylabel("$D_{ij}$, 2026 confirmation")
cax = fig.add_axes([0.915, 0.15, 0.012, 0.80]); cb = fig.colorbar(sc, cax=cax); cb.set_label("Station separation (km)", fontsize=6.5); cb.ax.tick_params(labelsize=6, length=2); cb.outline.set_linewidth(0.4); cb.solids.set_rasterized(False); cb.solids.set_edgecolor("face")
for ext in ("pdf", "svg"): fig.savefig(F / f"e15_comparability.{ext}")
fig.savefig(F / "e15_comparability.png", dpi=600); print("\n".join(md[:3]))
