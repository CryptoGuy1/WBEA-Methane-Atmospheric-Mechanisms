"""Builds figure_manifest.csv, table_manifest.csv and evidence_manifest.csv for the Supplement evidence audit.
Non-mutating: reads committed files via `git show <branch>:<path>`. Every evidence value is re-read from its authoritative file
and checked against the stated value (tolerance = stated precision); failures are written as verified=False, never hidden."""
import subprocess, io, json, hashlib, re, pathlib, numpy as np, pandas as pd
from PIL import Image
HERE = pathlib.Path(__file__).resolve().parent
EXP = "research/e15-h2-matched-pair-comparability"; MS = "manuscript/section2-figures-tables"; AUD = "audit/final-experimental-audit"
def gshow(ref, p, binary=False):
    r = subprocess.run(["git", "show", f"{ref}:{p}"], capture_output=True); assert r.returncode == 0, (ref, p); return r.stdout if binary else r.stdout.decode()
def csv(ref, p, **k): return pd.read_csv(io.BytesIO(gshow(ref, p, True)), compression="gzip" if p.endswith(".gz") else None, **k)
def js(ref, p): return json.loads(gshow(ref, p))
def head(ref): return subprocess.run(["git", "rev-parse", ref], capture_output=True, text=True).stdout.strip()
def last(ref, p): return subprocess.run(["git", "log", "-1", "--format=%H", ref, "--", p], capture_output=True, text=True).stdout.strip()

# ---------------------------------------------------------------- FIGURES (23 distinct experiment figures)
MSF = "manuscript/figures/section4/"
F = [  # id, experiment, S-number, section, status, related manuscript-branch figure, conclusion, caveats, placement, caption outline, corrections, supersession
 ("figure01_network_geometry", "E01", "S1", "S1 Network and data", "development", "Fig. 1 (fig01_wbea_network) covers geometry",
  "27 H2 pairs <=30 km; station layout; composite wind-rose climatology at AMS 1, 5, 7", "wind roses are development-period composites (10 m, 20 m fill)",
  "Supplement (wind roses are unique; geometry duplicates Fig. 1)", "Panel (a) pairs; (b) all stations; (c)-(e) wind-from roses with n hours; development 2021-01-01 to 2025-12-02",
  "remove in-panel titles; (a)-(e) labels; drop internal 'R1' note; widen panel (b); CAS width", "none"),
 ("figure02_coverage_and_gap_timing", "E02", "S2", "S1 Network and data", "development", "Fig. 2 (fig02_ch4_availability) covers monthly/daily completeness",
  "missing-code timing: zero/span ('Z') hours concentrated at hours ending 01-06 (~16%)", "colour scale starts at 50% (lower months saturate); meanings of codes Z and '.' unconfirmed by WBEA (OPEN)",
  "Supplement (panel b unique; panel a partly duplicates Fig. 2)", "(a) monthly valid share; (b) share of station-hours by missing code and hour",
  "extend scale to 0% or state truncation; remove titles; confirm code meanings", "none"),
 ("figure03_excursion_phenotype", "E03", "S3", "S2 Excursions and observational structure", "development", "none (regime heatmap is a different summary)",
  "excursion rate peaks at night and in winter; joint-excursion lift falls with distance (Spearman -0.821)", "descriptive; development data; P95 by construction 5% in 2021-2023",
  "Supplement", "(a) hour x month rate; (b) diurnal; (c) seasonal (95% joint block-bootstrap CI); (d) co-occurrence lift vs separation, 66 pairs",
  "remove titles; (a)-(d) labels; define 'lift'", "none"),
 ("figureS4_episode_definition_sensitivity", "E03", "S4", "S2 Excursions and observational structure", "development", "none",
  "episode-onset timing depends on definition; missing-outcome bounds wide at hours 01-06", "label 'Manski bounds' superseded by 'extreme missing-outcome scenarios' (D-43)",
  "Supplement", "(a) onsets by definition R1-R5; (b) missing-outcome bounds vs complete case", "relabel 'Manski bounds'; remove titles", "terminology corrected (D-43)"),
 ("figureS1_network_correlation_by_stability", "E03", "S5", "S2 Excursions and observational structure", "development", "none",
  "network anomaly correlation decreases from unstable (0.41) to stable (0.25) terciles", "descriptive; tercile cuts -0.60, 0.00 degC",
  "Supplement", "three correlation matrices by stability tercile", "remove titles; (a)-(c) labels", "none"),
 ("figure04_stability_elasticity", "E04", "S6", "S3 Atmospheric stability (H1)", "development", "Fig. 4a redraws this with extracted residuals",
  "near-linear adjusted association, 0.048 ppm/SD; spline and RF partial dependence agree", "development only; RF baseline exploratory",
  "Supplement as archival (panel b RF curve not in Fig. 4)", "(a) partial residuals with bin means and linear fit; (b) spline, linear, RF partial dependence",
  "remove titles; keep RF panel; CAS width", "Fig. 4a supersedes panel (a) for the main text"),
 ("figure05_h1_robustness", "E04", "S7", "S3 Atmospheric stability (H1)", "development", "Fig. 4b/c show a subset",
  "H1 positive across years, seasons, response sets and proxies; next-day control 0.000", "label 'smoke hours' superseded by PWIP (D-31); 25 rows",
  "Supplement (full forest)", "estimates with 95% block-bootstrap CIs by replication, response, proxy and negative control",
  "relabel 'smoke hours'; remove title", "none"),
 ("figure06_directional_coupling", "E05", "S8", "S4 Directional analysis (H2)", "development", "Fig. 5a redraws panel (a); Fig. 5c replaces panel (b) with 2026",
  "development pooled D = 0.1285; 27/27 pairs positive; 21 family-wise significant", "panel (b) label shows 0.129 (saved 0.1285); development reference = 1,000 random shifts",
  "Supplement as archival", "(a) D vs separation with null 95% band; (b) development pooled null histogram",
  "correct '0.129' to 0.1285; state reference construction; remove titles", "Fig. 5 supersedes for main text"),
 ("figure08_residualisation_sensitivity", "E05", "S9", "S4 Directional analysis (H2)", "development", "none",
  "pair D robust to four regional-component definitions", "descriptive",
  "Supplement", "D by pair under no removal, leave-one-out, leave-pair-out (primary), leave-pair-out excluding AMS 14/18",
  "remove title", "none"),
 ("figure07_kernel_shape", "E06", "S10", "S5 Transport diagnostics", "development", "Fig. 5d redraws panel (b) with 2026 centroids",
  "pre-registered kernel criterion FAILED: 1/5 bins within signal-dominated reference (4 required)", "reference = simulated A = 3 injections (mask-gated); not a confidence interval",
  "Supplement (panel a lag profiles unique)", "(a) lag profiles observed vs simulated by transit bin; (b) centroid vs transit with reference band and year range",
  "remove titles; label failed criterion in caption", "none"),
 ("figureS2_detectability", "E06", "S11", "S5 Transport diagnostics", "development", "none",
  "per-pair detection under injected signals", "SHOWS SUPERSEDED mask-gated model; primary statement is continuous-source (D-39: 45%/83% at A = 0.2/0.4, memory 180 min)",
  "Supplement after regeneration", "detection rate vs pair transit, by amplitude and memory",
  "REGENERATE from review_continuous_detectability.csv (or show both models labelled)", "superseded by D-39 continuous-source analysis"),
 ("e09_centroids_by_wind", "E09", "S12", "S5 Transport diagnostics", "development", "none",
  "elevated-wind transit: INCONCLUSIVE (Delta SSE 0.314, CI -0.081 to 0.772)", "internal codes W0/W4/X4a in legends",
  "Supplement", "lag centroid vs transit under 10 m and ERA5 100 m winds with reference ranges",
  "replace codes with descriptive labels; remove titles", "E09-r1 refines"),
 ("e09_r1_centroids", "E09", "S13", "S5 Transport diagnostics", "development", "none",
  "revised elevated-wind analysis remains INCONCLUSIVE (Delta SSE 0.294, CI -0.122 to 0.741)", "internal codes",
  "Supplement (combine with S12 if space)", "(a) fixed W0 hours; (b) fixed bins, reference only changes",
  "replace codes; remove titles", "authoritative over e09_centroids_by_wind for the decision"),
 ("e10_typology", "E10", "S14", "S5 Transport diagnostics", "development", "none",
  "episode typology NOT SUPPORTED (wind-shift placebo not met: 0.122 vs 0.148)", "'isolated' (70.3% of episodes) mixes episodes with no assessable upstream pair (55.5% of all episodes) and assessable episodes without a lead pattern",
  "Supplement", "(a) episode-type shares by station; (b) ERA5 BLH at onset by type",
  "split or relabel 'isolated' (no assessable pair vs no lead pattern); state 'not supported' in caption", "none"),
 ("figure09_composition_decomposition", "E07", "S15", "S6 Regime decomposition (H3)", "development", "Fig. 6a redraws panel (b) as c vs w scatter",
  "development H3 share 0.027 (CI -0.040 to 0.126): NOT SUPPORTED; within-regime change dominates", "panel (a) includes deweathering share 0.213 NOT validated out of sample (D-44) and 'Manski' labels (D-43)",
  "Supplement", "(a) pooled share and sensitivities; (b) consecutive-year decomposition by station",
  "relabel Manski rows; mark deweathering as unvalidated; remove titles", "terminology corrected (D-43, D-44)"),
 ("figureS3_baseline_comparison", "E07", "S16", "S6 Regime decomposition (H3)", "development", "none",
  "fixed-effects vs RF normalisation agree for H1; Kitagawa within-regime vs deweathered change r = 0.94", "legend contains 'E04'",
  "Supplement", "(a) H1 effect curves; (b) H3 within-regime vs deweathered change, 120 contrasts",
  "remove experiment code; remove titles", "none"),
 ("e12_null_rejection_rates", "E12", "S17", "S8 Synthetic calibration and falsification", "post-confirmation exploratory", "Fig. 7a-c redraw these values",
  "null rejections 4.6/5.4/4.8/4.6% (overall inconclusive); seasonal confounding 23.8%; advected driver 100%", "scenario codes N0-N3, N1b, N2b; N1b is a falsification scenario, not a null",
  "Supplement as archival", "(a) calibration nulls by reference; (b) seasonal confounding and falsification",
  "replace codes; remove titles", "Fig. 7 supersedes for main text"),
 ("e12_null_pvalue_cdf_and_D", "E12", "S18", "S8 Synthetic calibration and falsification", "post-confirmation exploratory", "none",
  "p-value CDFs near uniform except seasonal confounding; D distributions", "panel (b) compares simulated D with the 2026 value: invites over-interpretation",
  "Supplement", "(a) p-value ECDF per scenario; (b) pooled D under nulls",
  "replace codes; caveat or remove 2026 line", "none"),
 ("e12_power", "E12", "S19", "S8 Synthetic calibration and falsification", "post-confirmation exploratory", "Fig. 7d redraws",
  "power 100% for D 0.07-0.20; 0% at 3 h lag", "power above D 0.21 untested",
  "Supplement as archival", "power vs median D, seven configurations",
  "replace codes; remove title; compact", "Fig. 7d supersedes"),
 ("e13_fig1_reference_distributions", "E13", "S20", "S9 Post-confirmation H2 analyses", "post-confirmation exploratory", "none",
  "2026 statistic exceeds all season-restricted surrogates (0/246, 0/63, 0/93)", "titles say 'Frozen E08' and 'cold/warm halves (C2)' (now calendar-based blocks)",
  "Supplement", "whole-period, quarterly and Jan-Apr/May-Sep reference distributions with observed D",
  "relabel C2; remove experiment codes; remove titles", "E13 closure terminology (a0f4e9f)"),
 ("e13_fig2_per_season", "E13", "S21", "S9 Post-confirmation H2 analyses", "post-confirmation exploratory", "none",
  "each 2026 quarter analysed separately: D 0.347/0.216/0.201, all at p floor", "p floors 1/64-1/66",
  "Supplement", "per-quarter reference distributions with observed D",
  "remove titles", "none"),
 ("e14_yearswap_null", "E14", "S22", "S9 Post-confirmation H2 analyses", "post-confirmation exploratory", "none",
  "cross-year negative control: 1/20 whole-period rejections (2/20 quarters, 0/20 Jan-Apr/May-Sep)", "dependent combinations; not a Type-I error estimate; same-year = observed alignment",
  "Supplement", "(a) z cross-year vs same-year with 2026 reference; (b) p-value ECDF; (c) seasonal recurrence",
  "none (v3 final; 174.5 mm)", "v3 supersedes v1/v2"),
 ("e15_comparability", "E15", "S23", "S9 Post-confirmation H2 analyses", "post-confirmation exploratory", "none",
  "development-2026 gap +0.159: +0.009 composition/window/reference/residualisation; +0.150 period among same 21 pairs", "descriptive; weight-sensitive (0.086-0.150); heterogeneous by separation; A6 not evaluable",
  "Supplement", "(a) pooled D through controlled steps, development years and 2026; (b) pair D development vs 2026 by separation",
  "none (174.5 mm, vector)", "none"),
]
FC = ["id", "experiment", "proposed_supplement_figure", "section", "experiment_status", "related_manuscript_branch_figure", "conclusion_supported",
      "caption_caveats", "recommended_placement", "caption_outline", "required_corrections", "supersession"]
fm = pd.DataFrame(F, columns=FC); files = subprocess.run(["git", "ls-tree", "-r", "--full-tree", "--name-only", EXP], capture_output=True, text=True).stdout.split()
rows = []
for r in fm.itertuples():
    g = next(f[:-4] for f in files if f.endswith(f"/figures/{r.id}.svg"))
    png = Image.open(io.BytesIO(gshow(EXP, g + ".png", True))); dpi = png.info.get("dpi", (None,))[0]
    svg = gshow(EXP, g + ".svg", True); fmts = [e for e in ("svg", "png", "pdf") if f"{g}.{e}" in files]
    rows.append(dict(path=g, branch=EXP, source_commit=last(EXP, g + ".svg"), formats=";".join(fmts), png_px=f"{png.size[0]}x{png.size[1]}", png_dpi=round(dpi) if dpi else "",
                     publication_source=g + ".svg", svg_sha256=hashlib.sha256(svg).hexdigest(), manuscript_duplication_overleaf="UNVERIFIED"))
fm = pd.concat([fm, pd.DataFrame(rows)], axis=1); assert len(fm) == 23 and fm.proposed_supplement_figure.is_unique
fm.to_csv(HERE / "figure_manifest.csv", index=False)

# ---------------------------------------------------------------- EVIDENCE (values re-read from authoritative files)
E = []
def ev(eid, exp, status, finding, stated, tol, src_ref, src, getter, interp, caveat):
    try: got = getter(); ok = abs(float(got) - float(stated)) <= tol
    except Exception as ex: got, ok = repr(ex), False
    E.append(dict(id=eid, experiment=exp, status=status, finding=finding, stated_value=stated, source_value=got, verified=ok, source_branch=src_ref,
                  source_file=src, source_commit=last(src_ref, src), interpretation=interp, caveat=caveat))
X = EXP; C = "experiments/E08_confirmation/confirmation_2026/"
e04 = lambda lab, col="estimate": csv(X, "experiments/E04_stability_elasticity/results/h1_estimates.csv").set_index("label").loc[lab, col]
e08 = lambda *k: (lambda d: [d := d[x] for x in k][-1])(js(X, C + "e08_results.json"))
ev("E03-1", "E03", "development", "joint-excursion lift vs distance, Spearman (66 pairs)", -0.821, 5e-4, X, "experiments/E03_excursion_patterns/results/addendum_distance_dependence_uncertainty.csv",
   lambda: csv(X, "experiments/E03_excursion_patterns/results/addendum_distance_dependence_uncertainty.csv").estimate.iloc[0], "spatial coherence decays with distance", "descriptive")
ev("F5-1", "PRE_E08/F5", "development", "stable low-wind enrichment at excursion onset", 2.728, 5e-4, X, "experiments/PRE_E08/results/f5_dev_regime_distribution_pooled.csv",
   lambda: csv(X, "experiments/PRE_E08/results/f5_dev_regime_distribution_pooled.csv").set_index("regime").loc["stable-low-wind", "enrichment"], "excursion onsets favour stable low-wind hours", "descriptive")
ev("E04-1", "E04", "development", "H1 development estimate (ppm/SD)", 0.04752, 5e-6, X, "experiments/E04_stability_elasticity/results/h1_estimates.csv", lambda: e04("Direct (with log wind)"), "development gate passed", "development data")
ev("E04-2", "E04", "development", "H1 development next-day control", -0.00004, 5e-6, X, "experiments/E04_stability_elasticity/results/h1_estimates.csv", lambda: e04("Negative control: coefficient on S(t+24), given S(t)"), "no next-day association in development", "")
ev("E05-1", "E05", "development", "H2 development pooled D", 0.1285, 5e-5, X, "experiments/E05_directional_coupling/results/h2_pooled.csv",
   lambda: csv(X, "experiments/E05_directional_coupling/results/h2_pooled.csv").pooled_D.iloc[0], "development gate passed", "reported elsewhere as 0.128 or 0.129 (rounding)")
ev("E05-2", "E05", "development", "family-wise significant development pairs (of 27)", 21, 0, X, "experiments/E05_directional_coupling/results/h2_pooled.csv",
   lambda: csv(X, "experiments/E05_directional_coupling/results/h2_pooled.csv").pairs_familywise_lt_05.iloc[0], "", "")
ev("E06-1", "E06", "development", "kernel criterion: bins inside reference (of 5; 4 required)", 1, 0, X, "experiments/E06_detectability_kernel/results/e06_observed_vs_reference_kernel.csv",
   lambda: (lambda k: int(((k.centroid >= k.ref_centroid_min) & (k.centroid <= k.ref_centroid_max)).sum()))(csv(X, "experiments/E06_detectability_kernel/results/e06_observed_vs_reference_kernel.csv")),
   "pre-registered quantitative kernel criterion FAILED", "ordering rule later frozen for confirmation; not agreement")
ev("E06-2", "E06", "development", "continuous-source detection, memory 180 min, A = 0.4", 0.8333, 5e-5, X, "experiments/E06_detectability_kernel/results/review_continuous_detectability.csv",
   lambda: (lambda d: d[(d.model == "continuous source") & (d.memory_min == 180) & (d.A == 0.4)].detection_rate.iloc[0])(csv(X, "experiments/E06_detectability_kernel/results/review_continuous_detectability.csv")), "detectability limits", "primary model per D-39")
ev("E07-1", "E07", "development", "H3 development share (Jan-Nov)", 0.0269, 5e-5, X, "experiments/E07_composition_decomposition/results/h3_sensitivity.csv",
   lambda: csv(X, "experiments/E07_composition_decomposition/results/h3_sensitivity.csv").share.iloc[0], "H3 NOT SUPPORTED in development", "")
ev("E09-1", "E09", "development", "elevated-wind Delta SSE (E09-r1)", 0.294, 5e-4, X, "experiments/E09_elevated_wind/results/r1_decision.csv",
   lambda: float(str(csv(X, "experiments/E09_elevated_wind/results/r1_decision.csv").value.iloc[0]).split()[0]), "INCONCLUSIVE", "CI -0.122 to 0.741")
ev("E10-1", "E10", "development", "typology wind-shift placebo met (1 = yes)", 0, 0, X, "experiments/E10_episode_typology/results/e10_decision.csv",
   lambda: int(bool(csv(X, "experiments/E10_episode_typology/results/e10_decision.csv").met.iloc[0])), "typology NOT SUPPORTED", "real 0.122 vs placebo 95th 0.148")
ev("E11-1", "E11", "development", "H2 leave-one-station-out pooled D minimum", 0.1206, 5e-5, X, "experiments/E11_station_contribution/results/x3_h2_station_contribution.csv",
   lambda: csv(X, "experiments/E11_station_contribution/results/x3_h2_station_contribution.csv").pooled_D.min(), "no single station drives H2", "range 0.1206-0.1432")
ev("E11-2", "E11", "development", "H1 leave-one-core-station-out minimum", 0.0432, 5e-5, X, "experiments/E11_station_contribution/results/x3_h1_station_contribution.csv",
   lambda: (lambda d: d[d.label.str.contains("response without")].estimate.min())(csv(X, "experiments/E11_station_contribution/results/x3_h1_station_contribution.csv")), "no single core station drives H1", "range 0.0432-0.0572 (7 rows); expanded 11-station variant 0.0343")
ev("E08-H1", "E08", "registered confirmation", "H1 2026 estimate (ppm/SD); CONFIRMED", 0.05204, 5e-6, X, C + "e08_results.json", lambda: e08("H1", "b1_primary"), "confirmed", "")
ev("E08-H1nc", "E08", "registered confirmation", "H1 2026 next-day coefficient", -0.01872, 5e-6, X, C + "e08_results.json", lambda: e08("H1", "b_nc"), "rule not triggered (ratio -0.34)", "UNEXPLAINED discrepancy with development; must be reported")
ev("E08-H2", "E08", "registered confirmation", "H2 2026 pooled D; CONFIRMED", 0.2879317085, 1e-10, X, C + "e08_results.json", lambda: e08("H2", "pooled_D"), "confirmed under frozen shifted-wind test", "no transport or emission inference")
ev("E08-H2p", "E08", "registered confirmation", "H2 finite p (1/247)", 1 / 247, 1e-12, X, C + "e08_results.json", lambda: e08("H2", "p"), "p at floor", "finite-shift resolution")
ev("E08-H3", "E08", "registered confirmation", "H3 2026 share; NOT CONFIRMED", 0.0110, 5e-5, X, C + "e08_results.json", lambda: e08("H3", "share"), "not confirmed", "estimator dominated by AMS 18")
ev("PC-H3", "E08 post-confirmation", "post-confirmation exploratory", "AMS 18 share of 2026 H3 denominator", 0.9293, 5e-5, X, "experiments/E08_post_confirmation_exploratory/results/h3_weight_concentration.json",
   lambda: js(X, "experiments/E08_post_confirmation_exploratory/results/h3_weight_concentration.json")["AMS18_denominator_share_2026"], "registered H3 estimate effectively one-station", "development 39.05%")
ev("PC-H1", "E08 post-confirmation", "post-confirmation exploratory", "2026 within-cell corr(S, S+24)", 0.146, 5e-4, X, "experiments/E08_post_confirmation_exploratory/results/h1_nc_covariance_summary.json",
   lambda: js(X, "experiments/E08_post_confirmation_exploratory/results/h1_nc_covariance_summary.json")["conf_corr_within"], "covariance explanation not supported", "")
s12 = lambda sc, m="primary", c="rate": csv(X, "experiments/E12_h2_synthetic_null_calibration/results/summary_by_scenario_method.csv").pipe(lambda d: d[(d.scenario == sc) & (d.method == m)][c].iloc[0])
for eid, sc, m, v, f, i in (("E12-1", "N1a", "primary", 0.054, "delayed common driver null rejection", "overall null calibration INCONCLUSIVE (upper 7.74% > 7.5%)"),
                            ("E12-2", "N2b", "primary", 0.238, "seasonal-confounding rejection (constructed)", "whole-period reference sensitive"),
                            ("E12-3", "N1b", "primary", 1.0, "advected shared driver rejection (falsification)", "test cannot identify transport; NOT a Type-I error"),
                            ("E12-4", "P1_L3", "primary", 0.0, "power at 3-h lag", "long-lag blind spot")):
    ev(eid, "E12", "post-confirmation exploratory", f, v, 5e-4, X, "experiments/E12_h2_synthetic_null_calibration/results/summary_by_scenario_method.csv", lambda sc=sc, m=m: s12(sc, m), i, "synthetic")
e13 = csv(X, "experiments/E13_h2_seasonal_shift_sensitivity/results/e13_summary.csv").set_index("configuration")
ev("E13-1", "E13", "post-confirmation exploratory", "quarterly-reference surrogates >= observed (of 63)", 0, 0, X, "experiments/E13_h2_seasonal_shift_sensitivity/results/e13_summary.csv",
   lambda: e13.loc["C1-w (season null, own weights)", "n_surrogates_ge_obs"], "robust to season-restricted references", "sensitivity, not a replacement test")
e14 = csv(X, "experiments/E14_h2_empirical_yearswap_null/results/summary.csv")
for eid, ref, v in (("E14-1", "Whole-period shifts (frozen reference)", 1), ("E14-2", "Within calendar quarters (exploratory)", 2), ("E14-3", "Within Jan-Apr / May-Sep (exploratory)", 0)):
    ev(eid, "E14", "post-confirmation exploratory", f"cross-year rejections /20: {ref} (frozen station rule)", v, 0, X, "experiments/E14_h2_empirical_yearswap_null/results/summary.csv",
       lambda ref=ref: e14[(e14.station_set == "coverage_rule") & (e14.reference == ref)].rejections.iloc[0], "rare rejections in cross-year negative controls", "dependent combinations; not a Type-I error estimate")
e15 = csv(X, "experiments/E15_h2_matched_pair_comparability/results/comparison_table.csv").set_index("id")
ev("E15-1", "E15", "post-confirmation exploratory", "matched pooled development Jan-Sep (21 pairs, 11 stations)", 0.1375, 5e-5, X, "experiments/E15_h2_matched_pair_comparability/results/comparison_table.csv",
   lambda: e15.loc["A5", "pooled_D"], "period difference +0.150 among same pairs", "descriptive; not causal")
ev("E15-2", "E15", "post-confirmation exploratory", "equal-weight development-2026 gap", 0.0864, 5e-4, X, "experiments/E15_h2_matched_pair_comparability/results/weight_sensitivity.csv",
   lambda: csv(X, "experiments/E15_h2_matched_pair_comparability/results/weight_sensitivity.csv").set_index("scheme").loc["equal", "difference"], "gap weight-sensitive", "")
em = pd.DataFrame(E); em.to_csv(HERE / "evidence_manifest.csv", index=False)

# ---------------------------------------------------------------- TABLES (candidates)
TB = [
 ("TS1", "S1", "Station-year data completeness (CH4, wind, temperature)", "experiments/E02_data_quality/results/q1_variable_completeness_station_year.csv", "station, year, variable, valid share", "include", "complements main Tables 1-2"),
 ("TS2", "S1", "Station pairs: separation, bearing, H2 eligibility (27 development / 21 confirmation)", "experiments/E01_geometry_instrumentation/results/pairwise_geometry.csv", "pair, km, bearing, development-eligible, confirmation-eligible", "include", "not in main text"),
 ("TS3", "S2", "Excursion-episode definition sensitivity and missing-outcome scenarios", "experiments/E03_excursion_patterns/results/q6_manski_bounds_by_hour.csv", "definition, onsets, hour; scenario bounds", "combine with figure S4 or archive", "file name uses superseded 'manski' term"),
 ("TS4", "S3", "H1 development estimates: replication, response sets, proxies, negative control, station contributions", "experiments/E04_stability_elasticity/results/h1_estimates.csv", "label, n hours, estimate, 95% CI", "include (with E11 H1 rows)", "Fig. S7 shows graphically"),
 ("TS5", "S4", "H2 development pair statistics", "experiments/E05_directional_coupling/results/h2_pair_statistics.csv", "pair, km, n aligned/reversed, weights, D, null SD, p, max-T p, CI", "include", "pair-level CIs are block bootstrap"),
 ("TS6", "S5", "Transport diagnostics: kernel criterion, continuous-source detectability, elevated wind, typology validation", "experiments/E06_detectability_kernel/results/e06_observed_vs_reference_kernel.csv", "bin, centroid, reference range, inside; detection by A/memory; Delta SSE; V1-V4", "include (combined negative/inconclusive table)", "sources also review_continuous_detectability.csv, r1_decision.csv, e10_decision.csv"),
 ("TS7", "S6", "H3 development share and sensitivities (Jan-Nov, Jan-Sep)", "experiments/E07_composition_decomposition/results/h3_sensitivity.csv", "analysis, share, 95% CI", "include", "relabel Manski rows; mark deweathering unvalidated"),
 ("TS8", "S7", "Frozen 2026 confirmation: full H1-H3 statistics and descriptive outputs", "experiments/E08_confirmation/confirmation_2026/e08_results.json", "quantity, value, CI, decision", "include", "partly in main results table; full detail here"),
 ("TS9", "S7", "2026 H2 pair statistics with max-T family-wise p", "experiments/E08_confirmation/confirmation_2026/descriptive/h2_pairs_maxT.csv", "pair, D, null SD, weight, p unadjusted, p max-T", "include", "no 2026 pair bootstrap CIs exist"),
 ("TS10", "S7", "Post-confirmation H1 and H3 diagnostics (NC covariance by period; H3 denominator by station)", "experiments/E08_post_confirmation_exploratory/results/h1_nc_covariance_by_period.csv", "period, correlations, coefficients; station, sum t^2, share", "include", "post-confirmation exploratory"),
 ("TS11", "S8", "Synthetic calibration, power and falsification: all scenarios and references", "experiments/E12_h2_synthetic_null_calibration/results/summary_by_scenario_method.csv", "scenario (descriptive), role, method, n, rejections, rate, Wilson CI, classification, median D", "include", "N2a Wilson lower bound erratum (0.0325 not 0.033)"),
 ("TS12", "S9", "Season-restricted reference configurations (2026)", "experiments/E13_h2_seasonal_shift_sensitivity/results/e13_summary.csv", "configuration, K, D, p, null max, z", "include", "sensitivity only"),
 ("TS13", "S9", "Cross-year negative-control outcomes (25 combinations x 2 station sets)", "experiments/E14_h2_empirical_yearswap_null/results/replicates.csv", "methane year, wind year, pairs, D, p, z, quarter/block p", "include", "dependent combinations; nominal intervals"),
 ("TS14", "S9", "Matched-pair comparability: controlled comparisons and shared-pair weights", "experiments/E15_h2_matched_pair_comparability/results/summary_table.csv", "analysis, window, universe, pairs, reference, D, null SD, z, p, effective pairs; shared-pair D/weights/contributions", "include (two parts)", "A6 not evaluable"),
]
tm = pd.DataFrame(TB, columns=["table_id", "section", "purpose", "authoritative_source", "proposed_columns", "recommendation", "notes"])
tm["source_branch"] = EXP; tm["source_exists"] = [subprocess.run(["git", "cat-file", "-e", f"{EXP}:{p}"]).returncode == 0 for p in tm.authoritative_source]
tm["source_commit"] = [last(EXP, p) for p in tm.authoritative_source]; tm.to_csv(HERE / "table_manifest.csv", index=False)
print("figures", len(fm), "| evidence", len(em), "verified", int(em.verified.sum()), "| tables", len(tm), "sources exist", int(tm.source_exists.sum()))
print(em[~em.verified][["id", "stated_value", "source_value"]].to_string(index=False) if (~em.verified).any() else "ALL EVIDENCE VALUES VERIFIED")
