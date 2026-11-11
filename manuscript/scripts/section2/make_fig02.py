"""Fig. 2 (Jan-Sep 2026) and Fig. S1 (2021-2025): DAILY CH4 availability from hourly validity indicators
(manuscript/data/section2/ch4_daily_availability_*.csv). Cells are vector quadrilaterals (pcolormesh, not rasterised)."""
import numpy as np, pandas as pd
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from common import plt, MM, DATA, STUDY, EXCLUDED, save
BINS = [-0.5, 0.5, 11.5, 22.5, 24.5]                # valid hours per day: 0 | 1-11 | 12-22 | 23-24
COLS = ["#d94801", "#fdae6b", "#9ecae1", "#2171b5"]
LABELS = ["0 h", "1-11 h", "12-22 h", "23-24 h (normal operation: one daily zero/span hour)"]
CMAP, NORM = ListedColormap(COLS), BoundaryNorm(BINS, len(COLS))

def heat(csv, width_mm, height_mm, stem, year_ticks=False, legend_ncol=3, mark_excluded=True):
    d = pd.read_csv(csv, parse_dates=["day"]); days = np.sort(d.day.unique())
    M = d.pivot(index="station", columns="day", values="valid_hours").reindex(STUDY)
    cov = d.groupby("station").valid_hours.sum() / d.groupby("station").hours.sum()
    fig, ax = plt.subplots(figsize=(width_mm * MM, height_mm * MM))
    x = np.r_[np.arange(len(days)), len(days)]; y = np.arange(len(STUDY) + 1)
    ax.pcolormesh(x, y, M.values, cmap=CMAP, norm=NORM, edgecolors="none", rasterized=False)
    ax.set_ylim(len(STUDY), 0); ax.set_yticks(np.arange(len(STUDY)) + 0.5)
    ax.set_yticklabels([f"{s} (excluded)" if (s in EXCLUDED and mark_excluded) else s for s in STUDY])
    for t in ax.get_yticklabels():
        if "excluded" in t.get_text(): t.set_color("#737373")
    dd = pd.to_datetime(days)
    if year_ticks:
        yi = [k for k, v in enumerate(dd) if v.month == 1 and v.day == 1]; ax.set_xticks(yi, [str(dd[k].year) for k in yi])
        mi = [k for k, v in enumerate(dd) if v.day == 1 and v.month in (4, 7, 10)]; ax.set_xticks(mi, minor=True)
        ax.set_xlabel("1 Jan 2021 - 1 Dec 2025 (hour-ending MST; one column = one day; minor ticks at quarters)")
    else:
        mi = [k for k, v in enumerate(dd) if v.day == 1]; ax.set_xticks(mi, [dd[k].strftime("%b") for k in mi], ha="left")
        ax.set_xlabel(f"{dd[0].year} (hour-ending MST; one column = one day)")
    ax.tick_params(axis="both", length=2, pad=1.5); ax.tick_params(axis="y", length=0)
    ax2 = ax.twinx(); ax2.set_ylim(len(STUDY), 0); ax2.set_yticks(np.arange(len(STUDY)) + 0.5, [f"{100 * cov[s]:.1f}%" for s in STUDY])
    ax2.tick_params(length=0, labelsize=6); ax2.set_ylabel("Valid hourly CH$_4$, whole period", fontsize=6.2)
    for sp in ("top", "right", "left", "bottom"): ax.spines[sp].set_linewidth(0.4); ax2.spines[sp].set_visible(False)
    leg = fig.legend(handles=[Patch(fc=c, ec="none", label=l) for c, l in zip(COLS, LABELS)], loc="lower center", ncol=legend_ncol,
                     frameon=False, bbox_to_anchor=(0.5, 0.0), fontsize=6, handlelength=1.2, columnspacing=1.0,
                     title="Valid hourly CH$_4$ observations per day", title_fontsize=6.2)
    fig.subplots_adjust(bottom=0.27 if legend_ncol > 1 else 0.36); save(fig, stem); return cov

c26 = heat(DATA / "ch4_daily_availability_2026_jan_sep.csv", 180, 68, "fig02_ch4_availability_2026", legend_ncol=4)
heat(DATA / "ch4_daily_availability_2026_jan_sep.csv", 90, 88, "fig02_ch4_availability_2026_single_column", legend_ncol=1)
heat(DATA / "ch4_daily_availability_2021_2025.csv", 180, 68, "figS1_ch4_availability_2021_2025", year_ticks=True, legend_ncol=4, mark_excluded=False)
print("fig02 and figS1 written"); print((100 * c26).round(1).to_dict())
