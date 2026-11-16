"""Supplement figures S1-S9 (E01-E05) redrawn from saved results; no statistic recomputed except transparent re-expression
(percent scaling, percentiles of saved null replicates, as in the originals). Each function asserts key values against sources."""
import sys, pathlib, numpy as np, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); from pubstyle import *
E = "experiments/"
CORE = ["AMS 1", "AMS 2", "AMS 6", "AMS 7", "AMS 11", "AMS 13", "AMS 23"]

def s01():
    st = csv("manuscript/data/section2/stations_study.csv", MS).set_index("station_id"); geo = csv(E + "E01_geometry_instrumentation/results/pairwise_geometry.csv")
    fam = geo[geo.in_h2_family]; assert len(geo) == 66 and len(fam) == 27
    wr = pd.read_csv(DATA / "figS01_windrose_sectors.csv")
    la0, lo0 = st.loc["AMS 5", "latitude_deg_n"], st.loc["AMS 5", "longitude_deg_e"]
    km = lambda s: ((st.loc[s, "longitude_deg_e"] - lo0) * 111.32 * np.cos(np.deg2rad(57.0)), (st.loc[s, "latitude_deg_n"] - la0) * 110.57)
    col = lambda s: C_ACC if s == "AMS 5" else (C_DEV if s in CORE else C_PRI)
    fig = plt.figure(figsize=(W * MM, 92 * MM))
    a = fig.add_axes([0.075, 0.11, 0.25, 0.82]); b = fig.add_axes([0.40, 0.56, 0.15, 0.37])
    for _, r in fam.iterrows():
        (x1, y1), (x2, y2) = km(r.i), km(r.j); a.plot([x1, x2], [y1, y2], c="#bdbdbd", lw=0.5, zorder=1)
    off = {"AMS 1": (-13, 2), "AMS 9": (4, 3), "AMS 13": (-13, -7), "AMS 30": (-13, 2), "AMS 2": (-11, 1), "AMS 11": (4, 1)}
    for s in st.index:
        if s in ("AMS 14", "AMS 18"): continue
        x, y = km(s); a.scatter(x, y, s=18, c=col(s), zorder=3, edgecolors="white", linewidths=0.4)
        a.annotate(s.replace("AMS ", ""), (x, y), xytext=off.get(s, (4, 2)), textcoords="offset points", fontsize=6.3)
    a.set_aspect("equal"); a.set_xlabel("Distance east of AMS 5 (km)"); a.set_ylabel("Distance north of AMS 5 (km)"); label(a, "a")
    for s in st.index: b.scatter(st.loc[s, "longitude_deg_e"], st.loc[s, "latitude_deg_n"], s=8, c=col(s), edgecolors="none")
    for s in ("AMS 14", "AMS 18"): b.annotate(s, (st.loc[s, "longitude_deg_e"], st.loc[s, "latitude_deg_n"]), xytext=(3, 0), textcoords="offset points", fontsize=5.8)
    b.set_aspect(1 / np.cos(np.deg2rad(57.0)), adjustable="datalim"); b.set_xlabel("Longitude", fontsize=6.3); b.set_ylabel("Latitude (°N)", fontsize=6.3); label(b, "b")
    import matplotlib.ticker as mt; b.xaxis.set_major_locator(mt.MultipleLocator(1.0)); b.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{abs(v):.0f}°W"))
    h = [plt.Line2D([], [], marker="o", ls="", c=c, ms=4, label=l) for c, l in ((C_DEV, "H1 core response station"), (C_ACC, "AMS 5 (stability tower)"), (C_PRI, "Other station"))]
    h.append(plt.Line2D([], [], c="#bdbdbd", lw=0.8, label="H2 pair (≤ 30 km; n = 27)"))
    fig.legend(handles=h, loc="lower left", bbox_to_anchor=(0.385, 0.08), frameon=False, fontsize=6.2)
    for k, s in enumerate(["AMS 1", "AMS 5", "AMS 7"]):
        p = fig.add_axes([[0.575, 0.57, 0.14, 0.31], [0.815, 0.57, 0.14, 0.31], [0.695, 0.10, 0.14, 0.31]][k], projection="polar")
        f = wr[wr.station == s].sort_values("sector"); p.set_theta_zero_location("N"); p.set_theta_direction(-1)
        p.bar(np.deg2rad(f.centre_deg), 100 * f.frequency, width=np.deg2rad(20), color="#6a7f99", edgecolor="white", linewidth=0.3)
        p.set_yticklabels([]); p.set_xticks(np.deg2rad([0, 90, 180, 270])); p.set_xticklabels(["N", "E", "S", "W"], fontsize=6); p.tick_params(axis="x", pad=-1)
        p.spines["polar"].set_linewidth(0.4); p.grid(lw=0.3, c=C_GRID)
        p.text(0.5, -0.30, f"{s} (n = {int(f.n_hours.iloc[0]):,} h)", transform=p.transAxes, ha="center", fontsize=6.2)
        label(p, "cde"[k], dx=0.05, dy=1.04)
    save(fig, "figS01_network_geometry_wind")

def s02():
    q2 = csv(E + "E02_data_quality/results/q2_monthly_completeness.csv"); q3 = csv(E + "E02_data_quality/results/q3_missing_share_by_hour_pct.csv")
    M = q2.pivot(index="station", columns="month", values="pct_valid_all_hours"); order = ["AMS 1", "AMS 2", "AMS 5", "AMS 6", "AMS 7", "AMS 9", "AMS 11", "AMS 13", "AMS 14", "AMS 18", "AMS 23", "AMS 30"]
    M = M.reindex(order); months = pd.PeriodIndex(M.columns, freq="M")
    fig = plt.figure(figsize=(W * MM, 66 * MM)); a = fig.add_axes([0.075, 0.36, 0.55, 0.56]); cb = fig.add_axes([0.075, 0.19, 0.55, 0.035]); b = fig.add_axes([0.73, 0.24, 0.25, 0.68])
    import matplotlib as mpl
    norm = mpl.colors.Normalize(0, 100); cmap = mpl.colormaps["cividis"]
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M.values[i, j]
            if np.isfinite(v): a.add_patch(plt.Rectangle((j, i), 1, 1, fc=cmap(norm(v)), ec="none"))
    a.set_xlim(0, M.shape[1]); a.set_ylim(M.shape[0], 0); a.set_yticks(np.arange(len(order)) + 0.5, order, fontsize=6.2)
    xt = [k for k, p in enumerate(months) if p.month == 1]; a.set_xticks([x + 0.5 for x in xt], [str(months[k].year) for k in xt]); a.tick_params(axis="y", length=0)
    for sp in a.spines.values(): sp.set_visible(False)
    a.set_xlabel("Month (development period)"); label(a, "a")
    lev = np.linspace(0, 100, 257)
    for k in range(256): cb.add_patch(plt.Rectangle((lev[k], 0), lev[k + 1] - lev[k], 1, fc=cmap(norm(lev[k] + 0.2)), ec=cmap(norm(lev[k] + 0.2)), lw=0.2))
    cb.set_xlim(0, 100); cb.set_yticks([]); cb.set_xlabel("Valid CH$_4$ hours per station-month (%)", fontsize=6.5)
    for sp in cb.spines.values(): sp.set_visible(False)
    for code, c, ls, lab in (("Z", C_ACC, "-", "code Z"), (".", C_PRI, "-", "code '.'"), ("C", C_DEV, (0, (3, 1.5)), "code C")):
        b.plot(q3.time_mst_hour_ending, q3[code], c=c, ls=ls, lw=1.0, marker="o", ms=2, label=lab)
    b.set_xticks(range(0, 24, 6)); b.set_xlabel("Hour ending (MST)"); b.set_ylabel("Share of station-hours (%)"); b.legend(frameon=False, loc="upper right"); label(b, "b")
    assert abs(q3.Z.max() - 16.4) < 1.0
    save(fig, "figS02_coverage_missing_codes")

def s03():
    hm = csv(E + "E03_excursion_patterns/results/q1_p95_rate_month_by_hour.csv").set_index("time_mst_hour_ending")
    hr = csv(E + "E03_excursion_patterns/results/q1_p95_rate_by_hour.csv"); mo = csv(E + "E03_excursion_patterns/results/q1_p95_rate_by_month.csv")
    lift = csv(E + "E03_excursion_patterns/results/q3_pairwise_cooccurrence.csv"); assert len(lift) == 66
    fig = plt.figure(figsize=(W * MM, 112 * MM)); ax = [fig.add_axes(p) for p in ([0.075, 0.58, 0.36, 0.37], [0.585, 0.58, 0.39, 0.37], [0.075, 0.09, 0.36, 0.37], [0.585, 0.09, 0.39, 0.37])]
    import matplotlib as mpl
    im = ax[0].pcolormesh(np.arange(25) - 0.5, np.arange(13) + 0.5, hm.values, cmap="cividis", shading="flat", rasterized=False)
    ax[0].set_xlabel("Hour ending (MST)"); ax[0].set_ylabel("Month"); ax[0].set_yticks([1, 4, 7, 10]); ax[0].set_xticks(range(0, 24, 6))
    c = fig.colorbar(im, ax=ax[0], fraction=0.05, pad=0.02); c.set_label("Excursion rate (%)", fontsize=6.3); c.ax.tick_params(labelsize=6); c.solids.set_rasterized(False); c.outline.set_linewidth(0.4)
    ax[1].fill_between(hr.hour_ending, hr.ci_lo, hr.ci_hi, color="#c6dbef", lw=0); ax[1].plot(hr.hour_ending, hr.rate_pct, c=C_PRI, lw=1.0)
    ax[1].axhline(5, c=C_MUTE, lw=0.6, ls=(0, (2, 2))); ax[1].set_xticks(range(0, 24, 6)); ax[1].set_xlabel("Hour ending (MST)"); ax[1].set_ylabel("Excursion rate (%; 95% CI)")
    ax[2].fill_between(mo.month, mo.ci_lo, mo.ci_hi, color="#c6dbef", lw=0); ax[2].plot(mo.month, mo.rate_pct, "o-", c=C_PRI, ms=2.5, lw=1.0)
    ax[2].axhline(5, c=C_MUTE, lw=0.6, ls=(0, (2, 2))); ax[2].set_xticks(range(1, 13)); ax[2].set_xlabel("Month"); ax[2].set_ylabel("Excursion rate (%; 95% CI)")
    ax[3].scatter(lift.km, lift.lift, s=8, c="#bdbdbd", lw=0, label="Unconditional")
    ax[3].scatter(lift.km, lift.lift_given_month_hour, s=8, c=C_DEV, lw=0, label="Given month × hour")
    ax[3].axhline(1, c=C_MUTE, lw=0.6, ls=(0, (2, 2))); ax[3].set_xscale("log"); ax[3].set_xlabel("Station separation (km)"); ax[3].set_ylabel("Joint-excursion lift")
    ax[3].legend(frameon=False, loc="upper right")
    for a, l in zip(ax, "abcd"): label(a, l)
    save(fig, "figS03_excursion_structure")

def s04():
    on = csv(E + "E03_excursion_patterns/results/q6_onsets_by_hour_by_rule.csv"); mb = csv(E + "E03_excursion_patterns/results/q6_manski_bounds_by_hour.csv")
    fig, ax = plt.subplots(1, 2, figsize=(W * MM, 62 * MM)); fig.subplots_adjust(left=0.07, right=0.98, bottom=0.18, top=0.91, wspace=0.3)
    cols = ["#08519c", "#6baed6", "#d95f02", "#fdae6b", "#4d4d4d"]
    for c, (r, ls) in zip(cols, zip(on.columns[1:], ["-", "-", "-", (0, (3, 1.5)), (0, (3, 1.5))])):
        ax[0].plot(on.hour_ending, on[r], c=c, ls=ls, lw=1.0, marker="o", ms=1.8, label=r)
    ax[0].set_xticks(range(0, 24, 6)); ax[0].set_xlabel("Hour ending (MST)"); ax[0].set_ylabel("P95 episode onsets (12 stations, 2021–2025)"); ax[0].set_ylim(0, 830); ax[0].legend(frameon=False, fontsize=5.6, loc="upper left", bbox_to_anchor=(0.40, 1.0))
    ax[1].fill_between(mb.time_mst_hour_ending, mb.lower_pct, mb.upper_pct, color="#c6dbef", lw=0, label="Extreme missing-outcome scenarios")
    ax[1].plot(mb.time_mst_hour_ending, mb.complete_case_pct, c=C_PRI, lw=1.0, label="Complete case")
    ax[1].set_xticks(range(0, 24, 6)); ax[1].set_xlabel("Hour ending (MST)"); ax[1].set_ylabel("Excursion-hour rate (%)"); ax[1].legend(frameon=False, loc="upper right")
    for a, l in zip(ax, "ab"): label(a, l)
    save(fig, "figS04_episode_definition_missing_outcomes")

def s05():
    import matplotlib as mpl
    fig = plt.figure(figsize=(W * MM, 64 * MM)); summ = csv(E + "E03_excursion_patterns/results/q5_correlation_summary.csv").set_index("tercile")
    norm = mpl.colors.Normalize(-0.2, 1); cmap = mpl.colormaps["viridis"]
    for k, t in enumerate(["unstable", "neutral", "stable"]):
        a = fig.add_axes([0.06 + k * 0.295, 0.14, 0.25, 0.25 * W / 64])
        m = csv(E + f"E03_excursion_patterns/results/q5_anomaly_correlation_{t}.csv", index_col=0); n = m.shape[0]
        for i in range(n):
            for j in range(n): a.add_patch(plt.Rectangle((j, i), 1, 1, fc=cmap(norm(m.values[i, j])), ec="none"))
        a.set_xlim(0, n); a.set_ylim(n, 0); lab = [s.replace("AMS ", "") for s in m.index]
        a.set_xticks(np.arange(n) + 0.5, lab, fontsize=5.6); a.set_yticks(np.arange(n) + 0.5, lab, fontsize=5.6); a.tick_params(length=0)
        for sp in a.spines.values(): sp.set_visible(False)
        a.set_xlabel(f"{t.capitalize()} tercile (mean r = {summ.loc[t, 'mean_offdiag_r']:.2f})", fontsize=6.5); label(a, "abc"[k])
    cax = fig.add_axes([0.945, 0.14, 0.012, 0.25 * W / 64]); lev = np.linspace(-0.2, 1, 257)
    for k in range(256): cax.add_patch(plt.Rectangle((0, lev[k]), 1, lev[k + 1] - lev[k], fc=cmap(norm(lev[k] + 0.002)), ec=cmap(norm(lev[k] + 0.002)), lw=0.2))
    cax.set_ylim(-0.2, 1); cax.set_xticks([]); cax.yaxis.tick_right(); cax.yaxis.set_label_position("right"); cax.set_ylabel("Pearson r of CH$_4$ anomaly", fontsize=6.3); cax.tick_params(labelsize=6)
    for sp in cax.spines.values(): sp.set_visible(False)
    save(fig, "figS05_correlation_by_stability")

def s06():
    est = csv(E + "E04_stability_elasticity/results/h1_estimates.csv").set_index("label"); ff = csv(E + "E04_stability_elasticity/results/h1_functional_form.csv")
    rf = csv(E + "E04_stability_elasticity/results/baseline_rf_partial_dependence.csv"); qb = csv("manuscript/data/section4/fig04a_quantile_bin_means.csv", MS)
    pr = pd.read_csv(ROOT / "manuscript/data/section4/fig04a_partial_residuals.csv.gz")       # authorised extraction (local; not redistributed)
    assert len(pr) == int(est.loc["Direct (with log wind)", "n_hours"]) == 40334
    fig, ax = plt.subplots(1, 2, figsize=(W * MM, 66 * MM)); fig.subplots_adjust(left=0.09, right=0.98, bottom=0.17, top=0.91, wspace=0.28)
    ax[0].hexbin(pr.S_partial_residual_sd, pr.CH4_partial_residual_ppm, gridsize=(58, 32), extent=(-2.5, 4, -0.3, 0.6), bins="log", mincnt=1, cmap="Greys", alpha=0.55, linewidths=0, rasterized=True)
    ax[0].plot(qb.S_bin_mean, qb.y_bin_mean, "o", ms=2.4, mfc="white", mec="#3a3a3a", mew=0.6, label="Quantile-bin means (25)")
    ax[0].plot(ff.S_sd, ff.linear_effect_ppm, c="#252525", ls=(0, (4, 2)), lw=1.0, label="Linear fit (0.0475 ppm per SD)")
    ax[0].set_xlim(-2.5, 4); ax[0].set_ylim(-0.3, 0.6); ax[0].set_xlabel("Stability, $Z_S$ (reference SD; adjusted)"); ax[0].set_ylabel("CH$_4$ anomaly (ppm; adjusted)"); ax[0].legend(frameon=False, loc="upper left")
    ax[1].axhline(0, c=C_GRID, lw=0.5); ax[1].plot(ff.S_sd, ff.linear_effect_ppm, c="#252525", ls=(0, (4, 2)), lw=1.0, label="Linear")
    ax[1].plot(ff.S_sd, ff.spline_effect_ppm, c=C_ACC, lw=1.2, label="Piecewise-linear spline"); ax[1].plot(rf.S_sd, rf.rf_partial_dependence_ppm, c=C_PRI, lw=1.2, label="Random-forest partial dependence")
    ax[1].set_xlabel("Stability, $Z_S$ (reference SD)"); ax[1].set_ylabel("Effect relative to $Z_S$ = 0 (ppm)"); ax[1].legend(frameon=False, loc="upper left")
    for a, l in zip(ax, "ab"): label(a, l)
    save(fig, "figS06_h1_functional_form")

def s07():
    est = csv(E + "E04_stability_elasticity/results/h1_estimates.csv"); est = est.iloc[::-1].reset_index(drop=True)
    relabel = {"Direct, smoke hours excluded": "Direct, potential wildfire-influenced periods excluded", "Proxy ERA5 -log(BLH), AMS 5 cell": "Proxy: ERA5 −log(boundary-layer height), AMS 5 cell"}
    def grp(l):
        if l.startswith("Negative") or "negative-control" in l: return C_ACC
        if l.startswith("Proxy"): return C_PRI
        if l in ("Total (no wind term)", "Direct (with log wind)"): return "#000000"
        return C_DEV
    fig, a = plt.subplots(figsize=(W * MM, 112 * MM)); fig.subplots_adjust(left=0.40, right=0.97, bottom=0.08, top=0.98)
    for i, r in est.iterrows():
        c = grp(r.label); a.plot([r.ci_lo, r.ci_hi], [i, i], c=c, lw=1.0); a.plot(r.estimate, i, "o", c=c, ms=3)
    prim = est.set_index("label").loc["Direct (with log wind)", "estimate"]; assert abs(prim - 0.04752) < 1e-9
    a.axvline(0, c=C_MUTE, lw=0.6); a.axvline(prim, c=C_GRID, lw=0.6, ls=(0, (2, 2)))
    a.set_yticks(range(len(est)), [relabel.get(l, l) for l in est.label], fontsize=6.2); a.tick_params(axis="y", length=0)
    a.set_xlabel("ppm per SD of stability proxy (95% block-bootstrap CI)")
    save(fig, "figS07_h1_robustness")

def s08():
    ps = csv(E + "E05_directional_coupling/results/h2_pair_statistics.csv"); nl = csv(E + "E05_directional_coupling/results/h2_null_distribution.csv.gz").values
    pool = csv(E + "E05_directional_coupling/results/h2_pooled.csv").iloc[0]; prec = 1 / nl.std(0) ** 2; pooled_null = nl @ prec / prec.sum()
    assert pool.pooled_D == 0.1285 and abs(float(prec @ ps.D / prec.sum()) - 0.1285) < 5e-5
    fig = plt.figure(figsize=(W * MM, 68 * MM)); a = fig.add_axes([0.075, 0.17, 0.55, 0.76]); b = fig.add_axes([0.72, 0.17, 0.26, 0.76])
    o = ps.sort_values("km").reset_index(); lo, hi = np.percentile(nl, 2.5, 0)[o["index"]], np.percentile(nl, 97.5, 0)[o["index"]]
    a.fill_between(o.km, lo, hi, step="mid", color="#e5e5e5", lw=0, label="Shifted-wind null, central 95%")
    fw = o.p_maxT_familywise < 0.05
    a.vlines(o.km, o.ci_lo, o.ci_hi, color=C_DEV, lw=0.6)
    a.plot(o.km[fw], o.D[fw], "o", c=C_DEV, ms=3.4, label="Family-wise p < 0.05 (max-T)"); a.plot(o.km[~fw], o.D[~fw], "o", ms=3.4, mfc="white", mec=C_DEV, mew=0.8, label="Not family-wise significant")
    a.axhline(0, c=C_GRID, lw=0.6); a.set_xlabel("Station separation (km)"); a.set_ylabel("Pair statistic $D_{ij}$ (dimensionless; 95% CI)"); a.legend(frameon=False, loc="upper right")
    b.hist(pooled_null, bins=40, color="#bdbdbd", ec="white", lw=0.3); b.axvline(pool.pooled_D, c=C_DEV, lw=1.6)
    b.text(pool.pooled_D - 0.003, b.get_ylim()[1] * 0.92, "Observed\n$D$ = 0.1285", ha="right", va="top", fontsize=6.3)
    b.set_xlabel("Pooled $D$ (dimensionless)"); b.set_ylabel("Random whole-day wind shifts (of 1,000)")
    label(a, "a"); label(b, "b"); save(fig, "figS08_h2_development_pairs")

def s09():
    rc = csv(E + "E05_directional_coupling/results/h2_residualisation_comparison.csv").sort_values("km").reset_index(drop=True)
    fig, a = plt.subplots(figsize=(W * MM, 68 * MM)); fig.subplots_adjust(left=0.075, right=0.98, bottom=0.22, top=0.95)
    spec = [("no common-mode removal", "#bdbdbd", "o"), ("leave-one-out common mode", C_ACC, "s"), ("leave-pair-out (primary)", "#000000", "D"), ("leave-pair-out, AMS 14/18 excluded", C_PRI, "^")]
    x = np.arange(len(rc))
    for k, (col, c, m) in enumerate(spec):
        a.plot(x + (k - 1.5) * 0.17, rc[col], m, c=c, ms=3.2, ls="", label={"no common-mode removal": "No common-mode removal", "leave-one-out common mode": "Leave-one-out common mode",
               "leave-pair-out (primary)": "Leave-pair-out (primary)", "leave-pair-out, AMS 14/18 excluded": "Leave-pair-out, AMS 14 and 18 excluded"}[col])
    a.axhline(0, c=C_GRID, lw=0.6); a.set_xticks(x, [p.replace("AMS ", "").replace("->", "–") for p in rc.pair], rotation=90, fontsize=6)
    a.set_xlabel("Station pair (ordered by separation, 2.7–27.3 km)"); a.set_ylabel("Pair statistic $D_{ij}$ (dimensionless)"); a.legend(frameon=False, ncol=2, loc="upper right")
    save(fig, "figS09_h2_residualisation")

if __name__ == "__main__":
    for f in (s01, s02, s03, s04, s05, s06, s07, s08, s09): f(); print("done", f.__name__)
