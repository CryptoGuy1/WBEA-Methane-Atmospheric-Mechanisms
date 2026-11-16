"""Supplement figures S10-S21 (E06, E09, E10, E07, E12, E13) redrawn from saved results with the FIGURE_QA corrections."""
import sys, pathlib, io, numpy as np, pandas as pd, matplotlib.ticker
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); from pubstyle import *
E = "experiments/"
BINS = ["0–0.5", "0.5–1", "1–1.5", "1.5–2", "2–3"]; MIDS = np.array([0.25, 0.75, 1.25, 1.75, 2.5])

def s10():
    obs = csv(E + "E06_detectability_kernel/results/e06_observed_vs_reference_kernel.csv"); ref = csv(E + "E06_detectability_kernel/results/e06_reference_kernels.csv")
    inside = ((obs.centroid >= obs.ref_centroid_min) & (obs.centroid <= obs.ref_centroid_max)).sum(); assert inside == 1
    fig = plt.figure(figsize=(W * MM, 64 * MM)); a = fig.add_axes([0.075, 0.2, 0.52, 0.72]); b = fig.add_axes([0.70, 0.2, 0.28, 0.72])
    for k in range(5):
        rr = ref[ref.tau_bin == k][["r0", "r1", "r2", "r3"]]; x = np.arange(4) + 5 * k
        a.fill_between(x, rr.min().values, rr.max().values, color="#f3c89f", alpha=0.8, lw=0)
        a.plot(x, obs.loc[k, ["r0", "r1", "r2", "r3"]].values, "o-", c=C_DEV, ms=2.6, lw=0.9)
    a.axhline(0, c=C_GRID, lw=0.6); a.set_xticks(np.arange(5) * 5 + 1.5, [f"{t} h" for t in BINS]); a.set_xlabel("Nominal transit-time class (each group: lags 0, 1, 2, 3 h)")
    a.set_ylabel("Lagged correlation, aligned hours"); h = [plt.Line2D([], [], c=C_DEV, marker="o", ms=2.6, label="Observed, 2021–2025"), plt.Rectangle((0, 0), 1, 1, fc="#f3c89f", label="Signal-dominated simulated range (A = 3)")]
    a.legend(handles=h, frameon=False, loc="upper right")
    b.plot([0, 3], [0, 3], ls=(0, (1.5, 1.5)), c=C_MUTE, lw=0.7)
    for k in range(5): b.add_patch(plt.Rectangle((MIDS[k] - 0.18 * (2 if k == 4 else 1), obs.ref_centroid_min[k]), 0.36 * (2 if k == 4 else 1), obs.ref_centroid_max[k] - obs.ref_centroid_min[k], fc="#f3c89f", alpha=0.8, ec="none"))
    b.vlines(MIDS, obs.centroid_min_by_year, obs.centroid_max_by_year, color=C_DEV, lw=0.7); b.plot(MIDS, obs.centroid, "o", c=C_DEV, ms=3.4)
    b.set_xlim(0, 3); b.set_ylim(0, 2.5); b.set_xticks(MIDS, BINS, fontsize=5.8); b.set_xlabel("Transit-time class (h)"); b.set_ylabel("Positive-part lag centroid (h)")
    label(a, "a"); label(b, "b"); save(fig, "figS10_lag_kernel_criterion")

def s11():
    d = csv(E + "E06_detectability_kernel/results/review_continuous_detectability.csv")
    fig, ax = plt.subplots(1, 2, figsize=(W * MM, 62 * MM), sharey=True); fig.subplots_adjust(left=0.08, right=0.98, bottom=0.17, top=0.91, wspace=0.08)
    for k, mem in enumerate((20, 180)):
        a = ax[k]
        for model, c, m, lab in (("continuous source", C_PRI, "o", "Continuous source (authoritative; D-39)"), ("original (mask-gated)", C_MUTE, "s", "Mask-gated (superseded)")):
            r = d[(d.model == model) & (d.memory_min == mem)].sort_values("A"); a.plot(r.A, 100 * r.detection_rate, m + "-", c=c, mfc=c if m == "o" else "white", ms=4, lw=1.0, label=lab)
        a.set_xticks([0.2, 0.4]); a.set_xlim(0.1, 0.5); a.set_ylim(0, 100); a.set_xlabel("Injected amplitude A (signal SD / residual SD)")
        a.text(0.03, 0.95, f"Signal memory {mem} min", transform=a.transAxes, fontsize=6.4, va="top")
    ax[0].set_ylabel("Pairs detecting the signal (%)"); ax[1].legend(frameon=False, loc="lower right")
    assert abs(d[(d.model == "continuous source") & (d.memory_min == 180) & (d.A == 0.4)].detection_rate.iloc[0] - 0.8333) < 1e-9
    for a, l in zip(ax, "ab"): label(a, l)
    save(fig, "figS11_detectability_models")

VAR = {"W0": "10 m station wind", "W4_full": "ERA5 100 m wind", "W4_speed": "ERA5 100 m speed only", "W4_resel": "ERA5 100 m, reselected hours",
       "W0_dc": "10 m, direction-consistent", "W4_dc": "ERA5 100 m, direction-consistent", "T45": "AMS 5 tower 45 m", "T75": "AMS 5 tower 75 m", "T90": "AMS 5 tower 90 m",
       "W4_fixbin": "ERA5 100 m reference, fixed bins"}
def centroid_panel(a, t, variants, cols):
    a.plot([0, 3], [0, 3], ls=(0, (1.5, 1.5)), c=C_MUTE, lw=0.7)
    for v, c in zip(variants, cols):
        r = t.loc[v]; o = r[[f"obs_bin{k}" for k in range(5)]].values.astype(float); f = r[[f"ref_bin{k}" for k in range(5)]].values.astype(float)
        a.plot(MIDS, o, "o-", c=c, ms=3, lw=1.0, label=VAR[v]); a.plot(MIDS, f, "--", c=c, lw=0.9)
    a.set_xlim(0, 3); a.set_ylim(0, 2.6); a.set_xticks(MIDS, BINS, fontsize=5.8); a.set_xlabel("Transit-time class (h)"); a.set_ylabel("Lag centroid (h)")
    a.legend(frameon=False, fontsize=5.6, loc="upper left")
def style_legend(fig):
    fig.legend(handles=[plt.Line2D([], [], c=C_DEV, marker="o", ms=3, lw=1.0, label="Observed centroid"), plt.Line2D([], [], c=C_DEV, ls="--", lw=0.9, label="Simulated reference mean"),
                        plt.Line2D([], [], c=C_MUTE, ls=(0, (1.5, 1.5)), lw=0.7, label="Centroid = transit time")], loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.0), fontsize=6)
def s12():
    t = csv(E + "E09_elevated_wind/results/e09_centroids_reference_sse.csv").set_index("variant")
    fig, ax = plt.subplots(1, 3, figsize=(W * MM, 68 * MM), sharey=True); fig.subplots_adjust(left=0.065, right=0.99, bottom=0.24, top=0.91, wspace=0.08); style_legend(fig)
    for a, vs in zip(ax, (["W0", "W4_full"], ["W0", "W4_speed", "W4_resel"], ["W0_dc", "W4_dc"])):
        centroid_panel(a, t, vs, [C_DEV, C_PRI, C_ACC][:len(vs)])
    for a, l in zip(ax, "abc"): label(a, l)
    for a in ax[1:]: a.set_ylabel("")
    save(fig, "figS12_elevated_wind_centroids")
def s13():
    t = csv(E + "E09_elevated_wind/results/r1_centroids_reference_sse.csv").set_index("variant")
    dec = csv(E + "E09_elevated_wind/results/r1_decision.csv"); assert "inconclusive" in dec.outcome.iloc[0]
    fig, ax = plt.subplots(1, 2, figsize=(W * MM, 68 * MM), sharey=True); fig.subplots_adjust(left=0.07, right=0.99, bottom=0.24, top=0.91, wspace=0.08); style_legend(fig)
    centroid_panel(ax[0], t, ["W0", "W4_full"], [C_DEV, C_PRI]); centroid_panel(ax[1], t, ["W0", "W4_fixbin"], [C_DEV, C_ACC]); ax[1].set_ylabel("")
    for a, l in zip(ax, "ab"): label(a, l)
    save(fig, "figS13_elevated_wind_revised")

def s14():
    ep = csv(E + "E10_episode_typology/results/e10_episodes.csv"); assert len(ep) == 7951
    ep["cat"] = ep.label.where(ep.label != "isolated", np.where(ep.lead_assessable, "isolated: assessable, no lead pattern", "isolated: no assessable upstream pair"))
    order = ["accumulation-compatible", "mixed", "advection-compatible", "isolated: assessable, no lead pattern", "isolated: no assessable upstream pair", "unclassified"]
    cols = {"accumulation-compatible": "#2171b5", "mixed": "#9e9ac8", "advection-compatible": "#d95f02", "isolated: assessable, no lead pattern": "#969696",
            "isolated: no assessable upstream pair": "#d9d9d9", "unclassified": "#ffffff"}
    sh = pd.crosstab(ep.station, ep.cat, normalize="index").reindex(columns=order, fill_value=0)
    stations = sorted(sh.index, key=lambda s: int(s.split()[1])); sh = sh.reindex(stations)
    assert abs((ep.lead_assessable == False).mean() - 4412 / 7951) < 1e-9
    fig = plt.figure(figsize=(W * MM, 70 * MM)); a = fig.add_axes([0.07, 0.30, 0.50, 0.63]); b = fig.add_axes([0.70, 0.30, 0.28, 0.63])
    bottom = np.zeros(len(sh))
    for c in order: a.bar(range(len(sh)), sh[c], bottom=bottom, color=cols[c], width=0.75, label=c, edgecolor="#9e9e9e" if c == "unclassified" else "white", linewidth=0.3); bottom += sh[c].values
    a.set_xticks(range(len(sh)), [s.replace("AMS ", "") for s in sh.index]); a.set_xlabel("Station (AMS)"); a.set_ylabel("Share of P95 episodes"); a.set_ylim(0, 1)
    fig.legend(handles=[plt.Rectangle((0, 0), 1, 1, fc=cols[c], ec="#bdbdbd", lw=0.3, label=c) for c in order], loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.0), fontsize=6)
    grp = ["accumulation-compatible", "mixed", "advection-compatible", "isolated: assessable, no lead pattern", "isolated: no assessable upstream pair"]
    b.boxplot([ep[ep.cat == g].blh.dropna() for g in grp], showfliers=False, widths=0.6, medianprops=dict(color=C_ACC), boxprops=dict(lw=0.6), whiskerprops=dict(lw=0.6), capprops=dict(lw=0.6))
    b.set_xticks(range(1, 6), ["Accum.", "Mixed", "Advec.", "Isol.\n(assess.)", "Isol.\n(no pair)"], fontsize=5.8); b.set_ylabel("ERA5 boundary-layer height at onset (m)")
    label(a, "a"); label(b, "b"); save(fig, "figS14_episode_typology")

def s15():
    sens = csv(E + "E07_composition_decomposition/results/h3_sensitivity.csv"); con = csv(E + "E07_composition_decomposition/results/h3_contrasts_primary.csv")
    rel = {"Primary (raw P95, Jan-Nov, 2021-2025)": "Primary (P95, Jan–Nov 2021–2025)", "Manski lower (missing CH4 as non-exceedance)": "Missing CH$_4$ as non-exceedance (extreme scenario)",
           "Manski upper (missing CH4 as exceedance)": "Missing CH$_4$ as exceedance (extreme scenario)", "Background-adjusted excess C - B_t (D-16)": "Background-adjusted excess",
           "PWIP hours excluded": "Wildfire-influenced periods excluded", "Full calendar years 2021-2024 only": "Full calendar years 2021–2024 only",
           "Baseline: boosted-tree deweathering, implied meteorology share": "Deweathering baseline (not validated out of sample)"}
    fig = plt.figure(figsize=(W * MM, 112 * MM)); a = fig.add_axes([0.36, 0.62, 0.61, 0.34]); b = fig.add_axes([0.085, 0.09, 0.89, 0.40])
    s = sens.iloc[::-1].reset_index(drop=True)
    for i, r in s.iterrows():
        dw = "deweathering" in r.analysis.lower(); c = C_ACC if dw else (C_PRI if i == len(s) - 1 else C_DEV)
        if np.isfinite(r.ci_lo): a.plot([r.ci_lo, r.ci_hi], [i, i], c=c, lw=1.0)
        a.plot(r.share, i, "D" if dw else "o", c=c, mfc="white" if dw else c, ms=3.4)
    labs = [rel.get(x, x) for x in s.analysis]; assert all(x in rel for x in s.analysis), list(s.analysis)
    a.set_yticks(range(len(s)), labs, fontsize=6); a.tick_params(axis="y", length=0); a.axvline(0, c=C_MUTE, lw=0.6); a.set_xlabel("Composition share of between-year change (95% block-bootstrap CI)")
    assert abs(sens.share.iloc[0] - 0.0269) < 1e-9
    cy = con[con.year_b == con.year_a + 1].copy(); cy["x"] = range(len(cy))
    stations = list(dict.fromkeys(cy.station)); xpos = []; k = 0
    for st in stations:
        for _ in range(4): xpos.append(k); k += 1
        k += 1
    cy["x"] = xpos[:len(cy)]
    b.bar(cy.x, 100 * cy.composition, color=C_PRI, width=0.8, label="Composition (regime frequencies)")
    b.bar(cy.x, 100 * cy.within, bottom=np.where((cy.composition >= 0) == (cy.within >= 0), 100 * cy.composition, 0), color="#fdae6b", width=0.8, label="Within regimes")
    b.plot(cy.x, 100 * cy.total, "_", c="#000000", ms=6, mew=1.0, label="Total change")
    b.axhline(0, c=C_MUTE, lw=0.5); b.set_xticks([np.mean([x for x, s_ in zip(cy.x, cy.station) if s_ == st]) for st in stations], [s_.replace("AMS ", "") for s_ in stations])
    b.set_xlabel("Station (AMS; bars: 2021–22, 22–23, 23–24, 24–25)"); b.set_ylabel("Change in excursion rate (pp)"); b.legend(frameon=False, ncol=3, loc="upper left")
    label(a, "a", dx=-0.50); label(b, "b", dx=-0.035); save(fig, "figS15_h3_development_decomposition")

def s16():
    ff = csv(E + "E04_stability_elasticity/results/h1_functional_form.csv"); rf = csv(E + "E04_stability_elasticity/results/baseline_rf_partial_dependence.csv")
    dw = csv(E + "E07_composition_decomposition/results/baseline_deweathered_changes.csv"); r = np.corrcoef(dw.within, dw.deweathered_change)[0, 1]; assert len(dw) == 120 and round(r, 2) == 0.94
    fig, ax = plt.subplots(1, 2, figsize=(W * MM, 66 * MM)); fig.subplots_adjust(left=0.09, right=0.98, bottom=0.17, top=0.91, wspace=0.28)
    ax[0].axhline(0, c=C_GRID, lw=0.5); ax[0].plot(ff.S_sd, ff.linear_effect_ppm, c="#252525", ls=(0, (4, 2)), lw=1.0, label="Fixed-effects linear")
    ax[0].plot(ff.S_sd, ff.spline_effect_ppm, c=C_ACC, lw=1.1, label="Spline"); ax[0].plot(rf.S_sd, rf.rf_partial_dependence_ppm, c=C_PRI, lw=1.1, label="Random-forest normalisation")
    ax[0].set_xlabel("Stability, $Z_S$ (reference SD)"); ax[0].set_ylabel("Effect on network CH$_4$ (ppm)"); ax[0].legend(frameon=False, loc="upper left")
    lim = 10; ax[1].plot([-lim, lim], [-lim, lim], ls=(0, (2, 2)), c=C_MUTE, lw=0.6); ax[1].scatter(100 * dw.within, 100 * dw.deweathered_change, s=8, c=C_DEV, lw=0, alpha=0.7)
    ax[1].set_xlim(-lim, lim); ax[1].set_ylim(-lim, lim); ax[1].set_aspect("equal"); ax[1].set_xlabel("Within-regime change, decomposition (pp)"); ax[1].set_ylabel("Deweathered change (pp)")
    ax[1].text(0.03, 0.95, f"120 contrasts; r = {r:.2f}", transform=ax[1].transAxes, va="top", fontsize=6.3)
    for a, l in zip(ax, "ab"): label(a, l)
    save(fig, "figS16_baseline_comparison")

NAME = {"N0": "Baseline null", "N1a": "Wind-independent delayed common driver", "N2a": "Seasonal drift", "N3": "Autocorrelation, diurnal structure, missingness",
        "N2b": "Seasonal confounding (constructed)", "N1b": "Wind-advected shared driver (falsification)"}
METH = {"primary": "Whole-period shifts (frozen)", "within-season shift": "Within-season shifts (exploratory)", "truncated shift": "Truncated shifts (exploratory)"}
def s17():
    S = csv(E + "E12_h2_synthetic_null_calibration/results/summary_by_scenario_method.csv")
    fig = plt.figure(figsize=(W * MM, 74 * MM)); a = fig.add_axes([0.075, 0.33, 0.55, 0.60]); b = fig.add_axes([0.72, 0.33, 0.26, 0.60])
    cols = {"primary": C_DEV, "within-season shift": C_PRI, "truncated shift": C_ACC}
    for i, sc in enumerate(["N0", "N1a", "N2a", "N3"]):
        for j, m in enumerate(METH):
            r = S[(S.scenario == sc) & (S.method == m)].iloc[0]; x = i + (j - 1) * 0.22
            a.plot([x, x], [100 * r.wilson_lo, 100 * r.wilson_hi], c=cols[m], lw=1.0); a.plot(x, 100 * r.rate, "o", c=cols[m], ms=3.4, mfc=cols[m] if m == "primary" else "white")
    a.axhline(5, c=C_DEV, lw=0.7); a.axhline(7.5, c=C_MUTE, lw=0.6, ls=(0, (2, 2))); a.set_xticks(range(4), ["Baseline\nnull", "Delayed common\ndriver", "Seasonal\ndrift", "Autocorrelation,\ndiurnal, gaps"], fontsize=6)
    a.set_ylabel("Rejection rate (%; Wilson 95% CI)"); a.set_ylim(0, 12)
    for j, (sc, m) in enumerate([("N2b", "primary"), ("N2b", "within-season shift"), ("N2b", "truncated shift"), ("N1b", "primary")]):
        r = S[(S.scenario == sc) & (S.method == m)].iloc[0]; c = C_ACC if sc == "N1b" else cols[m]
        b.plot([j, j], [100 * r.wilson_lo, 100 * r.wilson_hi], c=c, lw=1.0); b.plot(j, 100 * r.rate, "o", c=c, ms=3.4, mfc=c if m == "primary" else "white")
    b.axhline(5, c=C_DEV, lw=0.7); b.axvline(2.5, c=C_GRID, lw=0.6); b.set_xticks(range(4), ["Whole-\nperiod", "Within-\nseason", "Trun-\ncated", "Whole-\nperiod"], fontsize=5.8); b.set_ylim(0, 105)
    b.text(1, 92, "Seasonal confounding\n(constructed)", ha="center", fontsize=5.8); b.text(2.8, 86, "Advected driver\n(falsification)", ha="right", va="center", fontsize=5.8, color=C_ACC)
    h = [plt.Line2D([], [], marker="o", c=cols[m], mfc=cols[m] if m == "primary" else "white", lw=1.0, ms=3.4, label=METH[m]) for m in METH]
    h += [plt.Line2D([], [], c=C_DEV, lw=0.7, label="Nominal 5%"), plt.Line2D([], [], c=C_MUTE, lw=0.6, ls=(0, (2, 2)), label="Calibration margin 7.5%")]
    fig.legend(handles=h, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.0), fontsize=5.9)
    label(a, "a"); label(b, "b"); save(fig, "figS17_null_rejection_rates")

def raw(sc): return csv(E + f"E12_h2_synthetic_null_calibration/results/raw_{sc}.csv")
def s18():
    fig, ax = plt.subplots(1, 2, figsize=(W * MM, 66 * MM)); fig.subplots_adjust(left=0.09, right=0.98, bottom=0.17, top=0.91, wspace=0.28)
    cols = {"N0": "#000000", "N1a": C_PRI, "N2a": "#6baed6", "N3": C_MUTE, "N2b": C_ACC, "N1b": "#7b3294"}
    ax[0].plot([0, 1], [0, 1], c=C_GRID, lw=0.6)
    for sc in ["N0", "N1a", "N2a", "N3", "N2b"]:
        p = np.sort(raw(sc).p_primary.values); ax[0].step(np.r_[0, p, 1], np.r_[0, np.arange(1, len(p) + 1) / len(p), 1], where="post", c=cols[sc], lw=1.0, label=NAME[sc])
    ax[0].set_xlabel("Finite shifted-wind p (whole-period reference)"); ax[0].set_ylabel("Empirical CDF"); ax[0].legend(frameon=False, loc="lower right", fontsize=5.6)
    for sc in ["N0", "N1a", "N2a", "N3", "N2b", "N1b"]:
        ax[1].hist(raw(sc).D_primary, bins=np.arange(-0.06, 0.2, 0.005), histtype="step", color=cols[sc], lw=1.0, label=NAME[sc])
    ax[1].set_xlabel("Pooled $D$ (dimensionless)"); ax[1].set_ylabel("Replicates"); ax[1].set_ylim(0, 205); ax[1].legend(frameon=False, loc="upper right", fontsize=5.6)
    for a, l in zip(ax, "ab"): label(a, l)
    save(fig, "figS18_null_pvalues_and_D")

def s19():
    S = csv(E + "E12_h2_synthetic_null_calibration/results/summary_by_scenario_method.csv")
    spec = [("P1_t007", "o", True, C_PRI), ("P1_t013", "o", True, C_PRI), ("P1_ceiling", "o", True, C_PRI), ("P1_L2", "s", True, C_PRI), ("P1_L3", "v", True, C_ACC), ("P1T_t013", "D", False, C_PRI), ("P1T_ceiling", "D", False, C_PRI)]
    fig, a = plt.subplots(figsize=(W * MM * 0.6, 62 * MM)); fig.subplots_adjust(left=0.13, right=0.97, bottom=0.18, top=0.91)
    a.axhline(0, c=C_GRID, lw=0.5); a.axvline(0, c=C_GRID, lw=0.5); done = set()
    lab = {"o": "Fixed 1-h lag", "s": "Fixed 2-h lag", "v": "Fixed 3-h lag", "D": "Transit-dependent lag"}
    for sc, m, f, c in spec:
        r = S[(S.scenario == sc) & (S.method == "primary")].iloc[0]
        a.plot([r.D_q50] * 2, [100 * r.wilson_lo, 100 * r.wilson_hi], c=c, lw=1.0); a.plot(r.D_q50, 100 * r.rate, m, c=c, mfc=c if f else "none", ms=4.6 if f else 5.6, label=None if m in done else lab[m]); done.add(m)
    a.set_xlim(-0.08, 0.24); a.set_ylim(-6, 106); a.set_xlabel("Median pooled $D$ of the configuration"); a.set_ylabel("Detection power (%; Wilson 95% CI)"); a.legend(frameon=False, loc="center left")
    save(fig, "figS19_power")

def s20():
    T = csv(E + "E13_h2_seasonal_shift_sensitivity/results/e13_summary.csv").set_index("configuration")
    spec = [("R0", "R0 frozen whole-period (reproduction)", "Whole-period shifts\n(registered)"), ("C1-w", "C1-w (season null, own weights)", "Within calendar quarters"),
            ("C2-w", "C2-w (season null, own weights)", "Within calendar-based blocks\nJan–Apr / May–Sep")]
    fig, ax = plt.subplots(1, 3, figsize=(W * MM, 60 * MM), sharex=True); fig.subplots_adjust(left=0.07, right=0.99, bottom=0.2, top=0.90, wspace=0.25)
    for a, (f, key, txt) in zip(ax, spec):
        s = csv(E + f"E13_h2_seasonal_shift_sensitivity/results/e13_surrogates_{f}.csv").iloc[:, 0]; obs = T.loc[key, "pooled_D"]; assert len(s) == T.loc[key, "K"]
        cnt, _, _ = a.hist(s, bins=np.arange(-0.15, 0.16, 0.01), color="#bdbdbd", ec="white", lw=0.3); a.set_ylim(0, cnt.max() * 1.5); a.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True)); a.axvline(obs, c=C_PRI, lw=1.4); a.axvline(0, c=C_GRID, lw=0.5)
        a.text(0.03, 0.97, f"{txt}\nK = {len(s)}", transform=a.transAxes, va="top", fontsize=5.8)
    ax[0].set_ylabel("Number of surrogates"); ax[1].set_xlabel("Pooled directional statistic $D$ (dimensionless)")
    for a, l in zip(ax, "abc"): label(a, l)
    save(fig, "figS20_season_restricted_references")

def s21():
    T = csv(E + "E13_h2_seasonal_shift_sensitivity/results/e13_per_season.csv").set_index("season")
    fig, ax = plt.subplots(1, 3, figsize=(W * MM, 60 * MM), sharex=True); fig.subplots_adjust(left=0.07, right=0.99, bottom=0.2, top=0.90, wspace=0.25)
    for a, q in zip(ax, ["Jan-Mar", "Apr-Jun", "Jul-Sep"]):
        s = csv(E + f"E13_h2_seasonal_shift_sensitivity/results/e13_surrogates_C4_{q}.csv").iloc[:, 0]; assert len(s) == T.loc[q, "K"]
        cnt, _, _ = a.hist(s, bins=np.arange(-0.16, 0.4, 0.015), color="#bdbdbd", ec="white", lw=0.3); a.set_ylim(0, cnt.max() * 1.45); a.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True)); a.axvline(T.loc[q, "pooled_D"], c=C_PRI, lw=1.4); a.axvline(0, c=C_GRID, lw=0.5)
        a.text(0.03, 0.97, f"{q.replace('-', '–')} 2026 ({int(T.loc[q, 'pairs'])} pairs)\nK = {len(s)}", transform=a.transAxes, va="top", fontsize=5.8)
    ax[0].set_ylabel("Number of surrogates"); ax[1].set_xlabel("Pooled directional statistic $D$ (dimensionless)")
    for a, l in zip(ax, "abc"): label(a, l)
    save(fig, "figS21_per_quarter_references")

if __name__ == "__main__":
    for f in (s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20, s21): f(); print("done", f.__name__)
