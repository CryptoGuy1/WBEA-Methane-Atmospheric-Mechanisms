"""E14 analysis (reads saved results only): summary table and one three-panel figure."""
import json, pathlib, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import kstest, wilcoxon, binom
HERE = pathlib.Path(__file__).resolve().parent; RES = HERE / "results"; FIG = HERE / "figures"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.linewidth": 0.6, "pdf.fonttype": 42, "svg.fonttype": "none"})
MM = 1 / 25.4; Z2026 = 6.989191                     # registered 2026 statistic under the frozen reference (E13 R0 reproduction; cited only)
R = pd.read_csv(RES / "replicates.csv"); REC = json.loads((RES / "seasonal_recurrence.json").read_text())
def wilson(k, n, z=1.959963984540054):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return c - h, c + h
rows = []
for ss in ("coverage_rule", "confirmation_network"):
    d = R[R.station_set == ss]; sw, an = d[d.kind == "swap"], d[d.kind != "swap"]
    for ref, col in (("Whole-period shifts (frozen reference)", "p"), ("Within calendar quarters (exploratory)", "C1_p"), ("Within Jan-Apr / May-Sep (exploratory)", "C2_p")):
        k = int((sw[col] <= 0.05).sum()); lo, hi = wilson(k, len(sw))
        rows.append(dict(station_set=ss, reference=ref, replicates=len(sw), rejections=k, rate_pct=100 * k / len(sw), wilson_lo_pct=100 * lo, wilson_hi_pct=100 * hi,
                         mean_p=sw[col].mean(), pairs=int(sw.pairs.iloc[0]), swap_D_min=sw.D.min(), swap_D_max=sw.D.max(),
                         anchor_D_min=an.D.min(), anchor_D_max=an.D.max(),
                         anchors_at_floor=int((an[col] <= 1.0 / (an[{"p": "K", "C1_p": "C1_K", "C2_p": "C2_K"}[col]] + 1) + 1e-12).sum())))
S = pd.DataFrame(rows); S.to_csv(RES / "summary.csv", index=False)
prim = R[(R.station_set == "coverage_rule") & (R.kind == "swap")]
stats = dict(ks_D=float(kstest(prim.p, "uniform").statistic), ks_p=float(kstest(prim.p, "uniform").pvalue), z_mean=float(prim.z.mean()), z_sd=float(prim.z.std()),
             wilcoxon_z_gt0_p=float(wilcoxon(prim.z, alternative="greater").pvalue),
             P_le1_given_rate={str(r): float(binom.cdf(1, 20, r)) for r in (0.10, 0.15, 0.20, 0.238)},
             decision="0-3/20 rejected: no evidence of inflation at the resolution of this design (does not establish calibration)")
(RES / "secondary_stats.json").write_text(json.dumps(stats, indent=1))

fig = plt.figure(figsize=(174.5 * MM, 62 * MM))
axs = [fig.add_axes([0.06, 0.2, 0.25, 0.72]), fig.add_axes([0.40, 0.2, 0.25, 0.72]), fig.add_axes([0.735, 0.2, 0.245, 0.72])]
for a, l in zip(axs, "abc"):
    a.text(-0.02, 1.03, f"({l})", transform=a.transAxes, fontweight="bold", fontsize=8, ha="right", va="bottom")
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
    a.tick_params(length=2.5, width=0.5)
# (a) standardised statistic: year-swapped negative controls vs same-year (observed alignment); deterministic display offsets by wind year
ax = axs[0]; an = R[(R.station_set == "coverage_rule") & (R.kind != "swap")]
off = {y: (i - 2) * 0.06 for i, y in enumerate(sorted(R.wind_year.unique()))}
ax.scatter(0 + prim.wind_year.map(off), prim.z, s=12, c="#7f7f7f", lw=0, alpha=0.85, label="Cross-year (20)")
rej = prim[prim.p <= 0.05]; ax.scatter(0 + rej.wind_year.map(off), rej.z, s=22, facecolors="none", edgecolors="#d95f02", lw=0.9, label="Rejected at 5%")
ax.scatter(1 + an.ch4_year.map(off), an.z, s=14, c="#2171b5", lw=0, label="Same-year (5)")
ax.axhline(0, c="#d9d9d9", lw=0.6, zorder=0); ax.axhline(Z2026, c="#2171b5", lw=0.8, ls=(0, (3, 2)))
ax.text(1.53, Z2026 + 0.12, "2026", color="#2171b5", fontsize=6, ha="right", va="bottom")
ax.set_xticks([0, 1], ["Cross-year", "Same-year"]); ax.set_xlim(-0.45, 1.55); ax.set_ylabel("Standardised pooled statistic, $z$")
ax.legend(frameon=False, fontsize=5.8, loc="center left", bbox_to_anchor=(0.0, 0.58), handletextpad=0.3, borderaxespad=0.1)
# (b) p-value ECDF of the 20 year-swapped replicates under the frozen whole-period reference
ax = axs[1]; ax.plot([0, 1], [0, 1], c="#bdbdbd", lw=0.7, ls=(0, (2, 2)))
for ss, c, ls, lab in (("coverage_rule", "#4d4d4d", "-", "All eligible stations"), ("confirmation_network", "#2171b5", (0, (4, 1.5)), "2026 station set")):
    p = np.sort(R[(R.station_set == ss) & (R.kind == "swap")].p.values); ax.step(np.r_[0, p, 1], np.r_[0, np.arange(1, len(p) + 1) / len(p), 1], where="post", c=c, lw=1.0, ls=ls, label=lab)
ax.axvline(0.05, c="#d95f02", lw=0.6); ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); ax.set_xlabel("Finite shifted-wind $p$"); ax.set_ylabel("Empirical CDF (cross-year)")
ax.legend(frameon=False, fontsize=5.8, loc="lower right")
# (c) realism: recurring seasonal cycle of methane residual variability (development years)
ax = axs[2]; mon = np.arange(1, 10)
for y, v in REC["resid_diff_sd_by_month"].items(): ax.plot(mon, v, c="#7f7f7f", lw=0.8, alpha=0.8)
ax.plot(mon, np.mean(list(REC["resid_diff_sd_by_month"].values()), axis=0), c="#252525", lw=1.4)
ax.set_xticks(mon, ["J", "F", "M", "A", "M", "J", "J", "A", "S"]); ax.set_ylabel("SD of hourly residual change (ppm)"); ax.set_xlabel("Month (lines: development years)")
for ext in ("pdf", "svg"): fig.savefig(FIG / f"e14_yearswap_null.{ext}")
fig.savefig(FIG / "e14_yearswap_null.png", dpi=600); print(S[["station_set", "reference", "rejections", "rate_pct", "wilson_lo_pct", "wilson_hi_pct", "mean_p"]].round(2).to_string(index=False)); print(json.dumps(stats, indent=0))
