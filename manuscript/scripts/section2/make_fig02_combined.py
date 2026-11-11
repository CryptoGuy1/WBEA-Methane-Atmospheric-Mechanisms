"""Combined Fig. 2: three stacked CH4-availability heatmaps from the validated daily availability files (no new data):
upper = monthly 2021-2025, middle = daily 2021-2025, lower = daily Jan-Sep 2026. One completeness definition for all:
valid hourly CH4 values / hours in the cell (x 100). Continuous cividis 0-100% with one shared colour bar.
No titles or panel letters. Exact canvas = Elsevier CAS double-column \\textwidth (174.5 mm)."""
import json, numpy as np, pandas as pd
from matplotlib.colors import Normalize
from common import plt, MM, DATA, STUDY, EXCLUDED, save_exact
CMAP, NORM = plt.get_cmap("cividis"), Normalize(0, 100)
dev = pd.read_csv(DATA / "ch4_daily_availability_2021_2025.csv", parse_dates=["day"])
cf = pd.read_csv(DATA / "ch4_daily_availability_2026_jan_sep.csv", parse_dates=["day"])
for d in (dev, cf): d["pct"] = 100 * d.valid_hours / d.hours
dev["month"] = dev.day.dt.to_period("M")
mon = dev.groupby(["station", "month"]).agg(valid=("valid_hours", "sum"), hours=("hours", "sum")).reset_index()
mon = mon[mon.month != pd.Period("2025-12", "M")]; mon["pct"] = 100 * mon.valid / mon.hours        # 1 Dec 2025 alone: partial month omitted

FIG_W, LEFT, RIGHT = 174.5, 16.0, 12.0; PANEL_H = 36.0; GAP = 10.5; CBAR = 14.0; TOP = 1.5
FIG_H = TOP + 3 * PANEL_H + 3 * GAP + CBAR
fig = plt.figure(figsize=(FIG_W * MM, FIG_H * MM)); PW = FIG_W - LEFT - RIGHT
def panel(k):                                                                 # k = 0 upper, 1 middle, 2 lower
    y = FIG_H - TOP - (k + 1) * PANEL_H - k * GAP
    return fig.add_axes([LEFT / FIG_W, y / FIG_H, PW / FIG_W, PANEL_H / FIG_H])

def heat(ax, M, xlabel, ticks, ticklabels, minor=None, cov=None, mark_excl=False, months=False):
    ax.pcolormesh(np.arange(M.shape[1] + 1), np.arange(len(STUDY) + 1), M, cmap=CMAP, norm=NORM, edgecolors="face", linewidth=0.1, rasterized=False)
    ax.set_ylim(len(STUDY), 0); ax.set_yticks(np.arange(len(STUDY)) + 0.5, [f"{s}\u2020" if (mark_excl and s in EXCLUDED) else s for s in STUDY])
    ax.set_xticks(ticks, ticklabels, ha="left"); ax.set_xlim(0, M.shape[1])
    if minor is not None: ax.set_xticks(minor, minor=True)
    ax.set_xlabel(xlabel, labelpad=1.5, fontsize=6.8); ax.tick_params(axis="y", length=0, labelsize=6.3, pad=2); ax.tick_params(axis="x", length=2, labelsize=6.5, pad=1.5)
    ax.tick_params(axis="x", which="minor", length=1.2)
    for sp in ax.spines.values(): sp.set_linewidth(0.4)
    if cov is not None:
        a2 = ax.twinx(); a2.set_ylim(len(STUDY), 0); a2.set_yticks(np.arange(len(STUDY)) + 0.5, [f"{cov[s]:.1f}%" for s in STUDY])
        a2.tick_params(length=0, labelsize=6.0, pad=1.5)
        for sp in a2.spines.values(): sp.set_visible(False)

# upper: monthly 2021-2025
months = sorted(mon.month.unique()); M0 = mon.pivot(index="station", columns="month", values="pct").reindex(STUDY)[months].values
yi = [k for k, p in enumerate(months) if p.month == 1]
heat(panel(0), M0, "Month (January 2021 \u2013 November 2025)", yi, [str(months[k].year) for k in yi], [k for k, p in enumerate(months) if p.month in (4, 7, 10)])
# middle: daily 2021-2025
days = np.sort(dev.day.unique()); dd = pd.to_datetime(days)
M1 = dev.pivot(index="station", columns="day", values="pct").reindex(STUDY)[days].values
cov_dev = 100 * dev.groupby("station").valid_hours.sum() / dev.groupby("station").hours.sum()
yi = [k for k, v in enumerate(dd) if v.month == 1 and v.day == 1]
heat(panel(1), M1, "Day (1 January 2021 \u2013 1 December 2025)", yi, [str(dd[k].year) for k in yi],
     [k for k, v in enumerate(dd) if v.day == 1 and v.month in (4, 7, 10)], cov=cov_dev)
# lower: daily Jan-Sep 2026
d26 = np.sort(cf.day.unique()); dd26 = pd.to_datetime(d26)
M2 = cf.pivot(index="station", columns="day", values="pct").reindex(STUDY)[d26].values
cov_cf = 100 * cf.groupby("station").valid_hours.sum() / cf.groupby("station").hours.sum()
mi = [k for k, v in enumerate(dd26) if v.day == 1]
heat(panel(2), M2, "Day (1 January \u2013 30 September 2026)", mi, [dd26[k].strftime("%b") for k in mi], cov=cov_cf, mark_excl=True)
fig.text((FIG_W - 1.0) / FIG_W, (FIG_H - TOP - PANEL_H - GAP - PANEL_H / 2) / FIG_H, "Valid hours, 2021\u20132025", rotation=90, ha="right", va="center", fontsize=6.2)
fig.text((FIG_W - 1.0) / FIG_W, (FIG_H - TOP - 3 * PANEL_H - 2 * GAP + PANEL_H / 2) / FIG_H, "Valid hours, 2026", rotation=90, ha="right", va="center", fontsize=6.2)
# shared colour bar
cax = fig.add_axes([(LEFT + 0.18 * PW) / FIG_W, 8.2 / FIG_H, 0.64 * PW / FIG_W, 2.4 / FIG_H])
edges = np.linspace(0, 100, 257)                                         # vector colour bar: 256 quadrilaterals (no embedded raster)
cax.pcolormesh(edges, [0, 1], ((edges[:-1] + edges[1:]) / 2)[None, :], cmap=CMAP, norm=NORM, edgecolors="face", linewidth=0.1, rasterized=False)
cax.set_xlim(0, 100); cax.set_yticks([]); cax.set_xticks([0, 25, 50, 75, 100]); cax.tick_params(labelsize=6.3, length=2, pad=1.5)
for sp in cax.spines.values(): sp.set_linewidth(0.4)
cax.set_xlabel("Valid hourly CH$_4$ observations (% of hours in each month or day)", fontsize=6.8, labelpad=2)
cax.axvline(100 * 23 / 24, color="k", lw=0.6); cax.text(100 * 23 / 24, 1.25, "23 of 24 h", transform=cax.get_xaxis_transform(), ha="center", va="bottom", fontsize=5.8)
save_exact(fig, "fig02_ch4_availability")
rec = dict(canvas_mm=[FIG_W, round(FIG_H, 2)], panels=[dict(name="monthly 2021-2025", rows=M0.shape[0], cols=M0.shape[1], nan_cells=int(np.isnan(M0).sum())),
           dict(name="daily 2021-2025", rows=M1.shape[0], cols=M1.shape[1], nan_cells=int(np.isnan(M1).sum())),
           dict(name="daily Jan-Sep 2026", rows=M2.shape[0], cols=M2.shape[1], nan_cells=int(np.isnan(M2).sum()))],
           definition="100 * valid hourly CH4 values / hours in cell (Z, C, '.' and blanks are not valid)", colormap="cividis, 0-100%, shared")
(DATA / "fig02_components.json").write_text(json.dumps(rec, indent=1)); print(json.dumps(rec))
