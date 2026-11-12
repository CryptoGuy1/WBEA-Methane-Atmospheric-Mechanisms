"""Final integrated audit: cross-check numbers reported in E06/E08/E12/E13 reports and decision logs against the saved
result files on each branch (read with `git show`, no branch modified or merged). Writes audit/crosscheck_results.csv."""
import io, json, subprocess, sys, numpy as np, pandas as pd
R = {"main": "main", "e12": "research/e12-h2-null-calibration", "e13": "research/e13-h2-seasonal-shift-sensitivity"}
def show(ref, path): return subprocess.run(["git", "show", f"{R[ref]}:{path}"], capture_output=True, text=True, check=True).stdout
def js(ref, path): return json.loads(show(ref, path))
def csv(ref, path): return pd.read_csv(io.StringIO(show(ref, path)))
rows = []
def chk(area, item, reported, saved, tol):
    ok = (reported == saved) if isinstance(reported, str) else bool(abs(float(reported) - float(saved)) <= tol)
    rows.append(dict(area=area, item=item, reported=reported, saved=saved, tolerance=tol, match=ok))
C = "experiments/E08_confirmation/confirmation_2026/"
e8 = js("main", C + "e08_results.json"); h1, h2, h3 = e8["H1"], e8["H2"], e8["H3"]
for item, rep, sav, t in [("H1 b1", 0.052, h1["b1_primary"], 5e-4), ("H1 CI lo", 0.039, h1["b1_primary_ci"][0], 5e-4), ("H1 CI hi", 0.069, h1["b1_primary_ci"][1], 5e-4),
    ("H1 n", 4472, h1["n_primary"], 0), ("H1 b1_joint", 0.055, h1["b1_joint"], 5e-4), ("H1 b_nc", -0.0187, h1["b_nc"], 5e-5), ("H1 b_nc CI lo", -0.0268, h1["b_nc_ci"][0], 5e-5),
    ("H1 b_nc CI hi", -0.0051, h1["b_nc_ci"][1], 5e-5), ("H1 ratio", -0.34, h1["ratio_nc"], 5e-3), ("H1 ratio CI lo", -0.51, h1["ratio_nc_ci"][0], 5e-3), ("H1 ratio CI hi", -0.09, h1["ratio_nc_ci"][1], 5e-3),
    ("H2 pooled D", 0.287931708, h2["pooled_D"], 5e-10), ("H2 p", 1 / 247, h2["p"], 1e-12), ("H2 K", 246, h2["K"], 0), ("H2 pairs", 21, h2["pairs_used"], 0),
    ("H2 +1h", 0.294, h2["pooled_D_wind_plus1h"], 5e-4), ("H2 -1h", 0.257, h2["pooled_D_wind_minus1h"], 5e-4), ("H2 rho", 1.0, h2["centroid_rule"]["rho"], 1e-9),
    ("H2 centroid diff CI lo", 0.74, h2["centroid_diff_ci"][0], 5e-3), ("H2 wind-eligible h", 54886, h2["wind_eligible_hours_total"], 0), ("H2 methane-complete h", 42133, h2["methane_complete_hours_total"], 0),
    ("H3 share", 0.011, h3["share"], 5e-4), ("H3 CI lo", -0.020, h3["ci_lo"], 5e-4), ("H3 CI hi", 0.043, h3["ci_hi"], 5e-4), ("H3 contrasts", 55, h3["contrasts_estimable"], 0),
    ("AMS 2 coverage", 0.4118, e8["log"]["station_coverage"]["AMS 2"], 5e-5)] + [(f"H2 centroid bin{k}", v, h2["centroids"][k], 5e-3) for k, v in enumerate([0.13, 0.35, 0.56, 0.98, 1.12])]:
    chk("E08 primary", item, rep, sav, t)
chk("E08 primary", "H1 decision", "True", str(h1["decision"]["confirmed"]), 0); chk("E08 primary", "H2 decision", "True", str(h2["confirmed"]), 0); chk("E08 primary", "H3 decision", "False", str(h3["confirmed"]), 0)
ds = js("main", C + "descriptive/descriptive_results.json"); f5 = csv("main", C + "descriptive/f5_regime_distribution.csv").set_index("regime")
kr = csv("main", C + "descriptive/kernel_reference_comparison.csv"); mt = csv("main", C + "descriptive/h2_pairs_maxT.csv")
for item, rep, sav, t in [("ERA5 proxy", 0.058, ds["h1_descriptive"]["era5_proxy_b"], 5e-4), ("CR1 SE", 0.0078, ds["h1_descriptive"]["cr1_se"], 5e-5),
    ("max-T pairs < 0.05", 14, int((mt.p_maxT_familywise < 0.05).sum()), 0), ("F5 stable-low-wind enrichment", 2.46, f5.loc["stable-low-wind", "enrichment"], 5e-3),
    ("F5 advective enrichment", 0.29, f5.loc["advective", "enrichment"], 5e-3), ("six-regime share", 0.012, ds["h3_descriptive"]["share_6_regimes"], 5e-4),
    ("kernel SSE mask-gated", 0.19, kr.SSE.iloc[0], 5e-3), ("kernel SSE continuous", 1.12, kr.SSE.iloc[1], 5e-3)]:
    chk("E08 descriptive", item, rep, sav, t)
P = "experiments/E08_post_confirmation_exploratory/results/"
w = js("main", P + "h3_weight_concentration.json"); n = js("main", P + "h1_nc_covariance_summary.json"); nb = csv("main", P + "h1_nc_covariance_by_period.csv").set_index("period")
for item, rep, sav, t in [("AMS 18 denominator share 2026", 0.929, w["AMS18_denominator_share_2026"], 5e-4), ("AMS 18 share development", 0.390, w["AMS18_denominator_share_development_JanSep"], 5e-4),
    ("share excl. AMS 18", -0.085, w["share_excluding_AMS18_point"], 5e-4), ("2026 corr(S,S+24) within", 0.146, n["conf_corr_within"], 5e-4),
    ("2026 corr(CH4,S+24) within", -0.043, nb.loc["2026 Jan-Sep", "corr_Y_Snext_within_cell"], 5e-4), ("Spearman b_nc vs corr", 0.14, n["spearman_bnc_vs_corrwithin_6_periods"], 5e-3)]:
    chk("Post-confirmation exploratory", item, rep, sav, t)
k6 = csv("main", "experiments/E06_detectability_kernel/results/e06_observed_vs_reference_kernel.csv")
rows.append(dict(area="E06 kernel", item="saved columns", reported="(see E06 REPORT)", saved=";".join(k6.columns), tolerance="", match=True))
S = csv("e12", "experiments/E12_h2_synthetic_null_calibration/results/summary_by_scenario_method.csv")
g = lambda sc, m, col: S[(S.scenario == sc) & (S.method == m)][col].iloc[0]
for sc, r, lo, hi in [("N0", .046, .031, .068), ("N1a", .054, .037, .077), ("N2a", .048, .033, .070), ("N3", .046, .031, .068), ("N2b", .238, .203, .277)]:
    chk("E12", f"{sc} primary rate", r, g(sc, "primary", "rate"), 5e-4); chk("E12", f"{sc} Wilson lo", lo, g(sc, "primary", "wilson_lo"), 5e-4); chk("E12", f"{sc} Wilson hi", hi, g(sc, "primary", "wilson_hi"), 5e-4)
for sc, m, r in [("N2b", "within-season shift", .052), ("N2b", "truncated shift", .068), ("N0", "within-season shift", .062), ("N1a", "within-season shift", .066),
                 ("N2a", "within-season shift", .042), ("N3", "within-season shift", .046), ("N1b", "primary", 1.0), ("P1_L3", "primary", 0.0)]:
    chk("E12", f"{sc} {m} rate", r, g(sc, m, "rate"), 5e-4)
for sc, d in [("P1_t007", .069), ("P1_t013", .131), ("P1_ceiling", .195), ("P1_L2", .108), ("P1_L3", -.040), ("P1T_t013", .131), ("P1T_ceiling", .177), ("N1b", .132), ("N2b", .012)]:
    chk("E12", f"{sc} median D", d, g(sc, "primary", "D_q50"), 5e-4)
for sc in ["P1_t007", "P1_t013", "P1_ceiling", "P1_L2", "P1T_t013", "P1T_ceiling"]: chk("E12", f"{sc} power", 1.0, g(sc, "primary", "rate"), 0)
v = js("e12", "experiments/E12_h2_synthetic_null_calibration/results/verdicts.json")
chk("E12", "Q1 verdict", "inconclusive", v["Q1_null_calibration"], 0); chk("E12", "Q2 verdict", "sensitive", v["Q2_seasonal_confounding"], 0)
chk("E12", "total replicates", 4100, v["total_replicates"], 0); chk("E12", "not evaluable", 0, v["total_not_evaluable"], 0)
E = csv("e13", "experiments/E13_h2_seasonal_shift_sensitivity/results/e13_summary.csv").set_index("configuration"); PS = csv("e13", "experiments/E13_h2_seasonal_shift_sensitivity/results/e13_per_season.csv").set_index("season")
r0 = E.loc["R0 frozen whole-period (reproduction)"]
chk("E13 vs E08", "R0 pooled D == E08 pooled D", h2["pooled_D"], r0.pooled_D, 1e-12); chk("E13 vs E08", "R0 p == E08 p", h2["p"], r0.p, 1e-12); chk("E13 vs E08", "R0 K", 246, r0.K, 0)
for cfg, K, p, Dv, mx, z in [("C1-w (season null, own weights)", 63, 1 / 64, .2871, .067, 7.55), ("C1-f (season null, frozen weights)", 63, 1 / 64, .2879, .066, 7.19),
                             ("C2-w (season null, own weights)", 93, 1 / 94, .2877, .099, 7.68), ("C2-f (season null, frozen weights)", 93, 1 / 94, .2879, .101, 7.56)]:
    chk("E13", f"{cfg[:4]} K", K, E.loc[cfg, "K"], 0); chk("E13", f"{cfg[:4]} p", p, E.loc[cfg, "p"], 1e-9); chk("E13", f"{cfg[:4]} pooled D", Dv, E.loc[cfg, "pooled_D"], 5e-5)
    chk("E13", f"{cfg[:4]} null max", mx, E.loc[cfg, "null_max"], 5e-4); chk("E13", f"{cfg[:4]} z", z, E.loc[cfg, "z"], 5e-3)
for q, d, K, npair in [("Jan-Mar", .347, 63, 21), ("Apr-Jun", .216, 64, 21), ("Jul-Sep", .201, 65, 20)]:
    chk("E13", f"{q} D", d, PS.loc[q, "pooled_D"], 5e-4); chk("E13", f"{q} K", K, PS.loc[q, "K"], 0); chk("E13", f"{q} pairs", npair, PS.loc[q, "pairs"], 0); chk("E13", f"{q} surrogates>=obs", 0, PS.loc[q, "n_surrogates_ge_obs"], 0)
src = show("e13", "experiments/E13_h2_seasonal_shift_sensitivity/e13.py"); plan = show("e13", "experiments/E13_h2_seasonal_shift_sensitivity/EXPERIMENT_PLAN.md")
chk("E13 definitions", "C1 blocks in code", "True", str("C1 = [(0, 2160), (2160, 4344), (4344, 6552)]" in src), 0)
chk("E13 definitions", "C2 blocks in code", "True", str("C2 = [(0, 2880), (2880, 6552)]" in src), 0)
chk("E13 definitions", "C1 shifts 14-76 in code", "True", str("C1_K = np.arange(14, 77)" in src), 0); chk("E13 definitions", "C2 shifts 14-106 in code", "True", str("C2_K = np.arange(14, 107)" in src), 0)
chk("E13 definitions", "plan states C1 K=63, C2 K=93", "True", str("| 14-76 | 63 |" in plan and "| 14-106 | 93 |" in plan), 0)
chk("E13", "overall outcome", "strengthens", json.loads(show("e13", "experiments/E13_h2_seasonal_shift_sensitivity/results/e13_results.json"))["overall_rule_outcome"], 0)
out = pd.DataFrame(rows); out.to_csv("audit/crosscheck_results.csv", index=False)
print(out.groupby("area").match.agg(["sum", "count"]).to_string()); print("MISMATCHES:"); print(out[~out.match].to_string(index=False) if (~out.match).any() else "none")
sys.exit(0 if out.match.all() else 1)
