"""Fig. 2 (revision 3: width = CAS textwidth 174.5 mm; data, classes and layout otherwise unchanged) and Fig. S1: daily CH4 availability (unchanged data and classes); exact canvas sizes; no titles or
panel labels. Adds Fig. S1b: monthly completeness for 2021-2025 (supplementary option), from the same hourly indicators."""
import numpy as np, pandas as pd
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from common import plt, MM, DATA, STUDY, EXCLUDED, save_exact
BINS = [-0.5, 0.5, 11.5, 22.5, 24.5]
COLS = ["#d94801", "#fdae6b", "#9ecae1", "#2171b5"]
LABELS = ["0 h (0%)", "1-11 h (4-46%)", "12-22 h (50-92%)", "23-24 h (96-100%; normal operation with one daily zero/span hour)"]
CMAP, NORM = ListedColormap(COLS), BoundaryNorm(BINS, len(COLS))

def layout(width_mm, height_mm, left_mm, right_mm, bottom_mm, top_mm):
    fig = plt.figure(figsize=(width_mm * MM, height_mm * MM))
    ax = fig.add_axes([left_mm / width_mm, bottom_mm / height_mm, (width_mm - left_mm - right_mm) / width_mm, (height_mm - bottom_mm - top_mm) / height_mm])
    return fig, ax

def right_axis(ax, cov, label):
    ax2 = ax.twinx(); ax2.set_ylim(ax.get_ylim()); ax2.set_yticks(np.arange(len(STUDY)) + 0.5, [f"{100 * cov[s]:.1f}%" for s in STUDY])
    ax2.tick_params(length=0, labelsize=6.5, pad=2); ax2.set_ylabel(label, fontsize=6.5, labelpad=4)
    for sp in ax2.spines.values(): sp.set_visible(False)

def daily(csv, stem, width_mm, height_mm, xlabel, year_ticks, mark_excluded, legend_ncol, bottom_mm):
    d = pd.read_csv(csv, parse_dates=["day"]); days = np.sort(d.day.unique()); dd = pd.to_datetime(days)
    M = d.pivot(index="station", columns="day", values="valid_hours").reindex(STUDY)
    cov = d.groupby("station").valid_hours.sum() / d.groupby("station").hours.sum()
    fig, ax = layout(width_mm, height_mm, (26.0 if width_mm > 100 else 25.0) if mark_excluded else 12.0, 15.0, bottom_mm, 1.5)
    ax.pcolormesh(np.r_[np.arange(len(days)), len(days)], np.arange(len(STUDY) + 1), M.values, cmap=CMAP, norm=NORM, edgecolors="face", linewidth=0.15, rasterized=False)   # face-coloured edges remove PDF anti-aliasing seams
    ax.set_ylim(len(STUDY), 0); ax.set_yticks(np.arange(len(STUDY)) + 0.5, [f"{s} (excluded)" if (s in EXCLUDED and mark_excluded) else s for s in STUDY])
    for t in ax.get_yticklabels():
        if "excluded" in t.get_text(): t.set_color("#737373")
    if year_ticks:
        yi = [k for k, v in enumerate(dd) if v.month == 1 and v.day == 1]; ax.set_xticks(yi, [str(dd[k].year) for k in yi], ha="left")
        ax.set_xticks([k for k, v in enumerate(dd) if v.day == 1 and v.month in (4, 7, 10)], minor=True)
    else:
        mi = [k for k, v in enumerate(dd) if v.day == 1]; ax.set_xticks(mi, [dd[k].strftime("%b") for k in mi], ha="left")
    ax.set_xlabel(xlabel, labelpad=2); ax.tick_params(axis="y", length=0, labelsize=6.5); ax.tick_params(axis="x", length=2, labelsize=6.5)
    for sp in ax.spines.values(): sp.set_linewidth(0.4)
    right_axis(ax, cov, "Valid hours, whole period")
    fig.legend(handles=[Patch(fc=c, ec="none", label=l) for c, l in zip(COLS, LABELS)], loc="lower center", ncol=legend_ncol, frameon=False,
               bbox_to_anchor=(0.5, 0.005), fontsize=6.5, handlelength=1.3, columnspacing=1.2, handletextpad=0.5,
               title="Valid hourly CH$_4$ observations per day (proportion of 24 h)", title_fontsize=6.5)
    save_exact(fig, stem); return cov

c26 = daily(DATA / "ch4_daily_availability_2026_jan_sep.csv", "fig02_ch4_availability_2026", 174.5, 70, "2026 (hour-ending MST; one column = one day)",
            False, True, 2, 21.0)
daily(DATA / "ch4_daily_availability_2026_jan_sep.csv", "fig02_ch4_availability_2026_single_column", 90, 92, "2026 (one column = one day)",
      False, True, 1, 33.0)
daily(DATA / "ch4_daily_availability_2021_2025.csv", "figS1_ch4_availability_2021_2025", 174.5, 70,
      "1 Jan 2021 - 1 Dec 2025 (hour-ending MST; one column = one day; minor ticks at quarters)", True, False, 2, 21.0)

# ---- Fig. S1b (option): monthly completeness, 2021-2025, from the same daily file
d = pd.read_csv(DATA / "ch4_daily_availability_2021_2025.csv", parse_dates=["day"]); d["month"] = d.day.dt.to_period("M")
m = d.groupby(["station", "month"]).agg(valid=("valid_hours", "sum"), hours=("hours", "sum")).reset_index(); m["pct"] = 100 * m.valid / m.hours
m = m[m.month != pd.Period("2025-12", "M")]                        # 1 Dec 2025 only: partial month excluded
m.to_csv(DATA / "ch4_monthly_availability_2021_2025.csv", index=False)
months = sorted(m.month.unique()); M = m.pivot(index="station", columns="month", values="pct").reindex(STUDY)
MB = [0, 50, 75, 90, 100.01]; MC = ["#d94801", "#fdae6b", "#9ecae1", "#2171b5"]
fig, ax = layout(174.5, 66, 12.0, 15.0, 17.0, 1.5)
ax.pcolormesh(np.arange(len(months) + 1), np.arange(len(STUDY) + 1), M.values, cmap=ListedColormap(MC), norm=BoundaryNorm(MB, 4), edgecolors="white", linewidth=0.3)
ax.set_ylim(len(STUDY), 0); ax.set_yticks(np.arange(len(STUDY)) + 0.5, STUDY)
yi = [k for k, p in enumerate(months) if p.month == 1]; ax.set_xticks(yi, [str(months[k].year) for k in yi], ha="left")
ax.set_xticks([k for k, p in enumerate(months) if p.month in (4, 7, 10)], minor=True)
ax.set_xlabel("Month, January 2021 - November 2025 (December 2025 partial month excluded: development data end 1 Dec 2025)", labelpad=2)
ax.tick_params(axis="y", length=0, labelsize=6.5); ax.tick_params(axis="x", length=2, labelsize=6.5)
cov = d.groupby("station").valid_hours.sum() / d.groupby("station").hours.sum(); right_axis(ax, cov, "Valid hours, whole period")
fig.legend(handles=[Patch(fc=c, ec="none", label=l) for c, l in zip(MC, ["< 50%", "50-75%", "75-90%", ">= 90% (normal operation about 95.8%)"])],
           loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.005), fontsize=6.5, handlelength=1.3, columnspacing=1.2,
           title="Valid hourly CH$_4$ observations per month", title_fontsize=6.5)
save_exact(fig, "figS1_ALTERNATIVE_monthly_ch4_availability_2021_2025")
print("fig02, single-column, S1 daily and S1b monthly written"); print({s: round(100 * c26[s], 1) for s in STUDY})
