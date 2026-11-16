"""Builds figure_manifest.csv, table_manifest.csv and evidence_manifest.csv for the publication assets. source_commit = the last
commit (on the pinned experiment source) touching each input file; output checksums are SHA-256 of the files written here."""
import sys, pathlib, subprocess, hashlib, pandas as pd
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); from pubstyle import ROOT, SUP, SRC, MS
def last(path, ref=SRC): return subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%h", ref, "--", path], capture_output=True, text=True).stdout.strip()
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
E = "experiments/"; R = lambda x, f: f"{E}{x}/results/{f}"
AUD = pd.read_csv(ROOT / "publication/supplement_audit/figure_manifest.csv").set_index("proposed_supplement_figure")
FIG = {  # S: (publication name, script, inputs [(path, ref)], transformation, corrections applied)
 "S1": ("figS01_network_geometry_wind", "make_figs_s01_s09.py", [(R("E01_geometry_instrumentation", "pairwise_geometry.csv"), SRC), ("manuscript/data/section2/stations_study.csv", MS), ("publication/supplementary/data/figS01_windrose_sectors.csv", "local")],
        "redrawn; wind-rose sectors re-extracted (aggregate only) by extract_e01_windrose_sectors.py, identical n to original", "titles removed; (a)-(e) labels; 'R1' note dropped; longitudes in degrees W; colour-blind palette"),
 "S2": ("figS02_coverage_missing_codes", "make_figs_s01_s09.py", [(R("E02_data_quality", "q2_monthly_completeness.csv"), SRC), (R("E02_data_quality", "q3_missing_share_by_hour_pct.csv"), SRC)],
        "redrawn from saved results", "colour scale extended to 0-100% (no saturation); vector colour bar; titles removed; code meanings left as raw codes (OPEN)"),
 "S3": ("figS03_excursion_structure", "make_figs_s01_s09.py", [(R("E03_excursion_patterns", f), SRC) for f in ("q1_p95_rate_month_by_hour.csv", "q1_p95_rate_by_hour.csv", "q1_p95_rate_by_month.csv", "q3_pairwise_cooccurrence.csv")],
        "redrawn from saved results", "titles removed; cividis; 'lift' axis label"),
 "S4": ("figS04_episode_definition_missing_outcomes", "make_figs_s01_s09.py", [(R("E03_excursion_patterns", f), SRC) for f in ("q6_onsets_by_hour_by_rule.csv", "q6_manski_bounds_by_hour.csv")],
        "redrawn from saved results", "'Manski bounds' relabelled 'extreme missing-outcome scenarios' (D-43); titles removed"),
 "S5": ("figS05_correlation_by_stability", "make_figs_s01_s09.py", [(R("E03_excursion_patterns", f"q5_anomaly_correlation_{t}.csv"), SRC) for t in ("unstable", "neutral", "stable")] + [(R("E03_excursion_patterns", "q5_correlation_summary.csv"), SRC)],
        "redrawn from saved results", "vector matrices and colour bar; titles moved to axis labels"),
 "S6": ("figS06_h1_functional_form", "make_figs_s01_s09.py", [(R("E04_stability_elasticity", f), SRC) for f in ("h1_estimates.csv", "h1_functional_form.csv", "baseline_rf_partial_dependence.csv")] + [("manuscript/data/section4/fig04a_quantile_bin_means.csv", MS), ("manuscript/data/section4/fig04a_partial_residuals.csv.gz", "local (uncommitted; authorised extraction)")],
        "redrawn; residual density from the authorised plotting-only extraction (verified n = 40,334, beta 0.04752)", "titles removed; RF panel retained"),
 "S7": ("figS07_h1_robustness", "make_figs_s01_s09.py", [(R("E04_stability_elasticity", "h1_estimates.csv"), SRC)], "redrawn from saved results", "'smoke hours' relabelled potential wildfire-influenced periods (D-31); title removed"),
 "S8": ("figS08_h2_development_pairs", "make_figs_s01_s09.py", [(R("E05_directional_coupling", f), SRC) for f in ("h2_pair_statistics.csv", "h2_null_distribution.csv.gz", "h2_pooled.csv")],
        "redrawn; null band = 2.5/97.5 percentiles of saved replicates (as original)", "pooled D corrected to 0.1285; reference stated (1,000 random shifts); titles removed"),
 "S9": ("figS09_h2_residualisation", "make_figs_s01_s09.py", [(R("E05_directional_coupling", "h2_residualisation_comparison.csv"), SRC)], "redrawn from saved results", "title removed; descriptive legend"),
 "S10": ("figS10_lag_kernel_criterion", "make_figs_s10_s21.py", [(R("E06_detectability_kernel", f), SRC) for f in ("e06_observed_vs_reference_kernel.csv", "e06_reference_kernels.csv")], "redrawn from saved results", "titles removed; reference labelled signal-dominated (A = 3), not a CI"),
 "S11": ("figS11_detectability_models", "make_figs_s10_s21.py", [(R("E06_detectability_kernel", "review_continuous_detectability.csv"), SRC)],
        "REDESIGNED: aggregate detection by amplitude for both models (per-pair continuous-source results were not saved)", "superseded mask-gated model shown only alongside the authoritative continuous-source model (D-39), labelled"),
 "S12": ("figS12_elevated_wind_centroids", "make_figs_s10_s21.py", [(R("E09_elevated_wind", "e09_centroids_reference_sse.csv"), SRC)],
        "redrawn; original CI and reference bands NOT reproduced (not saved); observed and reference means only", "internal codes replaced by descriptive variant names"),
 "S13": ("figS13_elevated_wind_revised", "make_figs_s10_s21.py", [(R("E09_elevated_wind", f), SRC) for f in ("r1_centroids_reference_sse.csv", "r1_decision.csv")],
        "redrawn; original 2.5/97.5% reference bands NOT reproduced (replicates not saved)", "internal codes replaced"),
 "S14": ("figS14_episode_typology", "make_figs_s10_s21.py", [(R("E10_episode_typology", "e10_episodes.csv"), SRC)],
        "redrawn; station shares re-tabulated from the saved episode file (7,951 episodes)", "'isolated' split into no assessable upstream pair (55.5%) vs assessable without lead pattern"),
 "S15": ("figS15_h3_development_decomposition", "make_figs_s10_s21.py", [(R("E07_composition_decomposition", f), SRC) for f in ("h3_sensitivity.csv", "h3_contrasts_primary.csv")],
        "redrawn from saved results", "'Manski' relabelled; deweathering marked not validated out of sample (D-44); internal D-16 code removed"),
 "S16": ("figS16_baseline_comparison", "make_figs_s10_s21.py", [(R("E04_stability_elasticity", f), SRC) for f in ("h1_functional_form.csv", "baseline_rf_partial_dependence.csv")] + [(R("E07_composition_decomposition", "baseline_deweathered_changes.csv"), SRC)],
        "redrawn from saved results", "'E04' code removed from legend"),
 "S17": ("figS17_null_rejection_rates", "make_figs_s10_s21.py", [(R("E12_h2_synthetic_null_calibration", "summary_by_scenario_method.csv"), SRC)], "redrawn from saved results",
        "scenario codes replaced; advected driver labelled falsification; 5% and 7.5% lines labelled"),
 "S18": ("figS18_null_pvalues_and_D", "make_figs_s10_s21.py", [(R("E12_h2_synthetic_null_calibration", f"raw_{s}.csv"), SRC) for s in ("N0", "N1a", "N2a", "N3", "N2b", "N1b")],
        "redrawn from saved replicate files", "2026 comparison line REMOVED; codes replaced"),
 "S19": ("figS19_power", "make_figs_s10_s21.py", [(R("E12_h2_synthetic_null_calibration", "summary_by_scenario_method.csv"), SRC)], "redrawn from saved results", "compact width; codes replaced; no curve"),
 "S20": ("figS20_season_restricted_references", "make_figs_s10_s21.py", [(R("E13_h2_seasonal_shift_sensitivity", f), SRC) for f in ("e13_summary.csv", "e13_surrogates_R0.csv", "e13_surrogates_C1-w.csv", "e13_surrogates_C2-w.csv")],
        "redrawn from saved surrogates", "'cold/warm halves' -> calendar-based blocks; 'E08' removed"),
 "S21": ("figS21_per_quarter_references", "make_figs_s10_s21.py", [(R("E13_h2_seasonal_shift_sensitivity", f), SRC) for f in ("e13_per_season.csv", "e13_surrogates_C4_Jan-Mar.csv", "e13_surrogates_C4_Apr-Jun.csv", "e13_surrogates_C4_Jul-Sep.csv")],
        "redrawn from saved surrogates", "titles removed; integer count axes"),
 "S22": ("figS22_cross_year_negative_control", "(none: copied)", [(f"{E}E14_h2_empirical_yearswap_null/figures/e14_yearswap_null.pdf", SRC)], "copied byte-for-byte (accepted v3)", "none"),
 "S23": ("figS23_matched_pair_comparability", "(none: copied)", [(f"{E}E15_h2_matched_pair_comparability/figures/e15_comparability.pdf", SRC)], "copied byte-for-byte (accepted)", "none"),
}
rows = []
for s, (name, script, inputs, trans, corr) in FIG.items():
    a = AUD.loc[s]; F = SUP / "figures"
    rows.append(dict(supplement_figure=s, publication_file=f"publication/supplementary/figures/{name}.{{pdf,svg,png}}", pdf_sha256=sha(F / f"{name}.pdf"), svg_sha256=sha(F / f"{name}.svg"), png_sha256=sha(F / f"{name}.png"),
                     generating_script=f"publication/supplementary/scripts/{script}" if script.endswith(".py") else script, source_inputs="; ".join(p for p, _ in inputs),
                     source_commits="; ".join((last(p, r) if r not in ("local",) and not r.startswith("local") else r) for p, r in inputs), source_branch="research/e15-h2-matched-pair-comparability (pinned 1788301); manuscript inputs from manuscript/section2-figures-tables (b61ffbf)",
                     original_experiment_figure=a.path, original_figure_commit=subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%H", SRC, "--", a.path + ".svg"], capture_output=True, text=True).stdout.strip(), original_svg_sha256=a.svg_sha256, experiment=a.experiment, experiment_status=a.experiment_status,
                     transformation=trans, corrections_applied=corr, caption_caveats=a.caption_caveats, section=a.section, original_preserved="yes (experiment directory unchanged)"))
fm = pd.DataFrame(rows); fm.to_csv(SUP / "figure_manifest.csv", index=False)
TM = pd.read_csv(ROOT / "publication/supplement_audit/table_manifest.csv")
TIN = {"TS1": ["E02_data_quality/results/q1_variable_completeness_station_year.csv"], "TS2": ["E01_geometry_instrumentation/results/h2_family_eligibility.csv", "E08_confirmation/confirmation_2026/h2_pairs.csv"],
       "TS3": ["E03_excursion_patterns/results/q6_onsets_by_hour_by_rule.csv", "E03_excursion_patterns/results/q6_manski_bounds_by_hour.csv"], "TS4": ["E04_stability_elasticity/results/h1_estimates.csv", "E11_station_contribution/results/x3_h1_station_contribution.csv"],
       "TS5": ["E05_directional_coupling/results/h2_pair_statistics.csv"], "TS6": ["E06_detectability_kernel/results/e06_observed_vs_reference_kernel.csv", "E06_detectability_kernel/results/review_continuous_detectability.csv", "E09_elevated_wind/results/r1_delta_sse.csv", "E10_episode_typology/results/e10_decision.csv"],
       "TS7": ["E07_composition_decomposition/results/h3_sensitivity.csv", "PRE_E08/results/h3_jan_sep_benchmark.csv"], "TS8": ["E08_confirmation/confirmation_2026/e08_results.json", "E08_confirmation/confirmation_2026/descriptive/descriptive_results.json"],
       "TS9": ["E08_confirmation/confirmation_2026/h2_pairs.csv", "E08_confirmation/confirmation_2026/descriptive/h2_pairs_maxT.csv", "E01_geometry_instrumentation/results/h2_family_eligibility.csv"],
       "TS10": ["E08_post_confirmation_exploratory/results/h1_nc_covariance_by_period.csv", "E08_post_confirmation_exploratory/results/h3_2026_denominator_by_station.csv"],
       "TS11": ["E12_h2_synthetic_null_calibration/results/summary_by_scenario_method.csv", "E12_h2_synthetic_null_calibration/results/verdicts.json"], "TS12": ["E13_h2_seasonal_shift_sensitivity/results/e13_summary.csv", "E13_h2_seasonal_shift_sensitivity/results/e13_per_season.csv"],
       "TS13": ["E14_h2_empirical_yearswap_null/results/replicates.csv"], "TS14": ["E15_h2_matched_pair_comparability/results/comparison_table.csv", "E15_h2_matched_pair_comparability/results/shared_pairs_A5_vs_A1.csv"]}
TM["publication_file"] = [f"publication/supplementary/tables/{t}.tex" for t in TM.table_id]; TM["tex_sha256"] = [sha(SUP / "tables" / f"{t}.tex") for t in TM.table_id]
TM["generating_script"] = "publication/supplementary/scripts/make_tables.py"; TM["source_inputs"] = ["; ".join(E + p for p in TIN[t]) for t in TM.table_id]
TM["source_commits"] = ["; ".join(last(E + p) for p in TIN[t]) for t in TM.table_id]; TM["status"] = "prepared (compiles in CAS QA harness: 0 errors, 0 overfull)"
TM.to_csv(SUP / "table_manifest.csv", index=False)
EV = pd.read_csv(ROOT / "publication/supplement_audit/evidence_manifest.csv")
def full(path): return subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%H", SRC, "--", path], capture_output=True, text=True).stdout.strip()
EV["source_commit"] = [full(p) for p in EV.source_file]     # recomputed from the repository root (audit builder left these empty: cwd-relative path bug)
EV["source_ref_pinned"] = SRC
assert (EV.source_commit.str.len() == 40).all() and EV.verified.all()
EV.to_csv(SUP / "evidence_manifest.csv", index=False)
print("figures", len(fm), "| tables", len(TM), "| evidence", len(EV), "verified", int(EV.verified.sum()), "| empty source_commits:", int((fm.source_commits == "").sum() + (TM.source_commits == "").sum()))
