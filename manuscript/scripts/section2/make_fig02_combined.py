"""Combined Fig. 2: three stacked CH4-availability heatmaps from the validated daily availability files (no new data):
upper = monthly 2021-2025, middle = daily 2021-2025, lower = daily Jan-Sep 2026. One completeness definition for all:
valid hourly CH4 values / hours in the cell (x 100). Previous four-class colour scheme, classes in % of hours, one shared legend.
No titles or panel letters. Exact canvas = Elsevier CAS double-column \\textwidth (174.5 mm)."""
import json, numpy as np, pandas as pd
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from common import plt, MM, DATA, STUDY, EXCLUDED, save_exact
# Previous colour scheme restored exactly as in the earlier individual figures (same four colours):
#  daily cells (middle, lower): 0 h | 1-11 h | 12-22 h | 23-24 h valid  (= 0 | 4-46 | 50-92 | 96-100 % of hours)
#  monthly cells (upper):       <50 | 50-75 | 75-90 | >=90 % of hours valid
# Completeness definition is identical (valid hours / hours in cell); class limits match the aggregation level.
COLS = ["#d94801", "#fdae6b", "#9ecae1", "#2171b5"]
D_LAB = ["0 h", "1-11 h", "12-22 h", "23-24 h (normal operation: one daily zero/span hour)"]
M_LAB = ["< 50%", "50-75%", "75-90%", ">= 90% (normal operation about 95.8%)"]
CMAP = ListedColormap(COLS)
NORM_D = BoundaryNorm([-1.0, 100 * 0.5 / 24, 100 * 11.5 / 24, 100 * 22.5 / 24, 101.0], 4)       # boundaries at half-hours: exact hour classes
NORM_M = BoundaryNorm([0.0, 50.0, 75.0, 90.0, 100.01], 4)
dev = pd.read_csv(DATA / "ch4_daily_availability_2021_2025.csv", parse_dates=["day"])
cf = pd.read_csv(DATA / "ch4_daily_availability_2026_jan_sep.csv", parse_dates=["day"])
for d in (dev, cf): d["pct"] = 100 * d.valid_hours / d.hours
dev["month"] = dev.day.dt.to_period("M")
mon = dev.groupby(["station", "month"]).agg(valid=("valid_hours", "sum"), hours=("hours", "sum")).reset_index()
mon = mon[mon.month != pd.Period("2025-12", "M")]; mon["pct"] = 100 * mon.valid / mon.hours        # 1 Dec 2025 alone: partial month omitted

FIG_W, LEFT, RIGHT = 174.5, 16.0, 12.0; PANEL_H = 36.0; GAP = 10.5; CBAR = 21.0; TOP = 1.5
FIG_H = TOP + 3 * PANEL_H + 3 * GAP + CBAR
fig = plt.figure(figsize=(FIG_W * MM, FIG_H * MM)); PW = FIG_W - LEFT - RIGHT
def panel(k):                                                                 # k = 0 upper, 1 middle, 2 lower
    y = FIG_H - TOP - (k + 1) * PANEL_H - k * GAP
    return fig.add_axes([LEFT / FIG_W, y / FIG_H, PW / FIG_W, PANEL_H / FIG_H])

def heat(ax, M, xlabel, ticks, ticklabels, minor=None, cov=None, mark_excl=False, months=False, norm=None):
    ax.pcolormesh(np.arange(M.shape[1] + 1), np.arange(len(STUDY) + 1), M, cmap=CMAP, norm=norm, edgecolors="face", linewidth=0.1, rasterized=False)
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
cov_mon = 100 * mon.groupby("station").valid.sum() / mon.groupby("station").hours.sum()     # secondary axis restored: share of valid hours over the plotted months
heat(panel(0), M0, "Month (January 2021 \u2013 November 2025)", yi, [str(months[k].year) for k in yi], [k for k, p in enumerate(months) if p.month in (4, 7, 10)], cov=cov_mon, norm=NORM_M)
# middle: daily 2021-2025
days = np.sort(dev.day.unique()); dd = pd.to_datetime(days)
M1 = dev.pivot(index="station", columns="day", values="pct").reindex(STUDY)[days].values
cov_dev = 100 * dev.groupby("station").valid_hours.sum() / dev.groupby("station").hours.sum()
yi = [k for k, v in enumerate(dd) if v.month == 1 and v.day == 1]
heat(panel(1), M1, "Day (1 January 2021 \u2013 1 December 2025)", yi, [str(dd[k].year) for k in yi],
     [k for k, v in enumerate(dd) if v.day == 1 and v.month in (4, 7, 10)], cov=cov_dev, norm=NORM_D)
# lower: daily Jan-Sep 2026
d26 = np.sort(cf.day.unique()); dd26 = pd.to_datetime(d26)
M2 = cf.pivot(index="station", columns="day", values="pct").reindex(STUDY)[d26].values
cov_cf = 100 * cf.groupby("station").valid_hours.sum() / cf.groupby("station").hours.sum()
mi = [k for k, v in enumerate(dd26) if v.day == 1]
heat(panel(2), M2, "Day (1 January \u2013 30 September 2026)", mi, [dd26[k].strftime("%b") for k in mi], cov=cov_cf, mark_excl=True, norm=NORM_D)
fig.text((FIG_W - 1.0) / FIG_W, (FIG_H - TOP - PANEL_H / 2) / FIG_H, "Valid hours, Jan 2021\u2013Nov 2025", rotation=90, ha="right", va="center", fontsize=6.2)
fig.text((FIG_W - 1.0) / FIG_W, (FIG_H - TOP - PANEL_H - GAP - PANEL_H / 2) / FIG_H, "Valid hours, 2021\u20132025", rotation=90, ha="right", va="center", fontsize=6.2)
fig.text((FIG_W - 1.0) / FIG_W, (FIG_H - TOP - 3 * PANEL_H - 2 * GAP + PANEL_H / 2) / FIG_H, "Valid hours, 2026", rotation=90, ha="right", va="center", fontsize=6.2)
# legends (same colours): monthly classes for the upper plot, daily classes for the middle and lower plots
kw = dict(frameon=False, fontsize=6.5, handlelength=1.3, columnspacing=1.4, handletextpad=0.5, title_fontsize=6.8, ncol=4, loc="lower left")
fig.legend(handles=[Patch(fc=c, ec="none", label=l) for c, l in zip(COLS, M_LAB)], bbox_to_anchor=(LEFT / FIG_W, 11.0 / FIG_H),
           title="Upper plot: valid hourly CH$_4$ observations per month (% of hours)", alignment="left", **kw)
fig.legend(handles=[Patch(fc=c, ec="none", label=l) for c, l in zip(COLS, D_LAB)], bbox_to_anchor=(LEFT / FIG_W, 0.5 / FIG_H),
           title="Middle and lower plots: valid hourly CH$_4$ observations per day (of 24 h)", alignment="left", **kw)
save_exact(fig, "fig02_ch4_availability")
rec = dict(canvas_mm=[FIG_W, round(FIG_H, 2)], panels=[dict(name="monthly 2021-2025", rows=M0.shape[0], cols=M0.shape[1], nan_cells=int(np.isnan(M0).sum())),
           dict(name="daily 2021-2025", rows=M1.shape[0], cols=M1.shape[1], nan_cells=int(np.isnan(M1).sum())),
           dict(name="daily Jan-Sep 2026", rows=M2.shape[0], cols=M2.shape[1], nan_cells=int(np.isnan(M2).sum()))],
           definition="100 * valid hourly CH4 values / hours in cell (Z, C, '.' and blanks are not valid)", colormap="four classes, previous colours #d94801 #fdae6b #9ecae1 #2171b5; daily: 0|1-11|12-22|23-24 h; monthly: <50|50-75|75-90|>=90%")
(DATA / "fig02_components.json").write_text(json.dumps(rec, indent=1)); print(json.dumps(rec))
