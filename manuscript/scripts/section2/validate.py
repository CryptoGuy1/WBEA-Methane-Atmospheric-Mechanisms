"""Automated validation of Section 2 outputs. Writes manuscript/data/section2/validation_report.json; exits non-zero on failure."""
import json, re, subprocess, sys, numpy as np, pandas as pd
from common import ROOT, DATA, FIG, TAB, STUDY, EXCLUDED, PAIRS_CSV, E08_RESULTS
from wbea.geometry import stations, pair_table
R = {}; ok = True
def check(name, cond, detail=""):
    global ok; R[name] = dict(passed=bool(cond), detail=detail); ok &= bool(cond)
meta = pd.read_csv(ROOT / "metadata/stations_official_2024.csv").set_index("station_id"); st = pd.read_csv(DATA / "stations_study.csv").set_index("station_id")
check("coordinates_match_metadata", np.allclose(st.loc[STUDY, ["latitude_deg_n", "longitude_deg_e"]].values, meta.loc[STUDY, ["latitude_deg_n", "longitude_deg_e"]].values, atol=0, rtol=0), "12 stations, exact")
fz = pd.read_csv(PAIRS_CSV); used = [s for s in STUDY if s not in EXCLUDED]; pt = pair_table(used, 30.0)
rec = sorted(f"{a}->{b}" for a, b in zip(pt.i, pt.j)); pl = pd.read_csv(DATA / "pairs_frozen.csv")
check("pairs_equal_frozen_and_recomputed", sorted(fz.pair) == rec == sorted(pl.pair) and len(rec) == 21, f"{len(rec)} pairs; identical to frozen h2_pairs.csv and to the <=30 km rule on 11 stations")
cov = pd.read_csv(DATA / "ch4_station_coverage_2026_check.csv"); froz = json.loads(E08_RESULTS.read_text())["log"]["station_coverage"]
check("coverage_2026_matches_frozen", (cov.abs_diff < 5e-5).all(), f"max abs diff {cov.abs_diff.max():.2e} (frozen stored to 4 dp)")
check("excluded_station_rule", [s for s in STUDY if froz[s] < 0.5] == EXCLUDED, f"stations < 50%: {[s for s in STUDY if froz[s] < 0.5]}")
for f, nd in (("ch4_daily_availability_2026_jan_sep.csv", 273), ("ch4_daily_availability_2021_2025.csv", 1796)):
    d = pd.read_csv(DATA / f, parse_dates=["day"])
    check(f"days_and_hours_{nd}", d.day.nunique() == nd and (d.hours == 24).all() and len(d) == nd * 12, f"{d.day.nunique()} days x 12 stations, 24 h each (hour-ending: 00:00 assigned to previous day)")
    check(f"hour_accounting_{nd}", ((d["valid_hours"] + d["Z"] + d["C"] + d["dot"] + d["other_missing"]) == d["hours"]).all(), "valid + Z + C + '.' + other = 24 for every station-day")
check("first_last_days", str(pd.read_csv(DATA / "ch4_daily_availability_2026_jan_sep.csv").day.min())[:10] == "2026-01-01" and str(pd.read_csv(DATA / "ch4_daily_availability_2026_jan_sep.csv").day.max())[:10] == "2026-09-30", "2026: 1 Jan - 30 Sep")
conf = {d.station.iloc[0]: d for d in (pd.read_parquet(f) for f in (ROOT / "sealed/e08_panel").glob("AMS*.parquet"))}
nonpos = sum(int((d["CH4 (ppm)"] <= 0).sum()) for d in conf.values()); tokvals = sum(int(d["CH4 (ppm)"][d["CH4 (ppm)__token"].isin(["Z", "C", "."])].notna().sum()) for d in conf.values())
check("no_missing_as_zero", nonpos == 0 and tokvals == 0, f"CH4 <= 0: {nonpos}; coded hours with numeric value: {tokvals}")
SPEC = {"fig01_wbea_network": (174.5, 118.0), "fig02_ch4_availability": (174.5, 155.0)}
c2 = json.loads((DATA / "fig02_components.json").read_text())
check("fig02_combined_components", [(p["rows"], p["cols"], p["nan_cells"]) for p in c2["panels"]] == [(12, 59, 0), (12, 1796, 0), (12, 273, 0)] and "cividis" in c2["colormap"],
      "upper monthly 12x59, middle daily 12x1796, lower daily 12x273; no missing cells (missing hours are 0%, not blank); one cividis 0-100% scale")
dv_ = pd.read_csv(DATA / "ch4_daily_availability_2021_2025.csv", parse_dates=["day"]); mm = pd.read_csv(DATA / "ch4_monthly_availability_2021_2025.csv")
dv_["m"] = dv_.day.dt.to_period("M").astype(str); rec_ = dv_[dv_.m != "2025-12"].groupby(["station", "m"]).valid_hours.sum() / dv_[dv_.m != "2025-12"].groupby(["station", "m"]).hours.sum()
check("same_completeness_definition", np.allclose(np.sort(100 * rec_.values), np.sort(mm.pct.values)), "monthly % = sum(valid hours)/sum(hours) of the same daily records used in the daily plots")
aux = (ROOT / "manuscript/latex_check/manuscript_check.aux").read_text(); pg = {k: int(v) for k, v in re.findall(r"newlabel\{(fig:network|fig:avail|tab:stations|tab:data|refs:start)\}\{\{[^}]*\}\{(\d+)\}", aux)}
check("floats_before_references", len(pg) == 5 and max(pg[k] for k in ("fig:network", "fig:avail", "tab:stations", "tab:data")) < pg["refs:start"], f"pages: {pg}")
comp = json.loads((DATA / "fig01_components.json").read_text())
check("fig01_all_components_present", comp["map_components"] == 3 and comp["regional_context"] and comp["network_map"]["pair_lines"] == 21
      and comp["cluster_map"]["pair_lines"] == 21 and comp["network_map"]["stations"] == sorted(STUDY) and comp["cluster_map"]["stations"] == sorted(STUDY) and len(comp["cluster_map"]["labelled_stations"]) == 10
      and comp["network_labelled"] == ["AMS 14", "AMS 18"] and comp["panel_letters"] == [],
      f"3 maps; network and enlarged maps each plot all 12 stations (by gid) and 21 pair lines; enlarged map: 21 pair lines, 10 labelled cluster stations; AMS 14/18 labelled on network map; panel letters: {comp['panel_letters']}")
d26 = pd.read_csv(DATA / "ch4_daily_availability_2026_jan_sep.csv")
check("fig02_all_rows_and_days", sorted(d26.station.unique()) == sorted(STUDY) and d26.day.nunique() == 273, "12 station rows x 273 daily columns")
import hashlib
H0 = {"ch4_daily_availability_2026_jan_sep.csv": "3437362b65ac7088", "ch4_daily_availability_2021_2025.csv": "77a6cbf51d15d8f6",
      "pairs_frozen.csv": "3c6270da973e531d", "stations_study.csv": "fcc9a89e7e62a968"}
check("validated_data_unchanged", all(hashlib.sha256((DATA / f).read_bytes()).hexdigest().startswith(h) for f, h in H0.items()), "SHA-256 prefixes equal those recorded before revision 3")
fz1 = subprocess.run(["git", "diff", "--stat", "protocol-freeze", "--", "src/wbea", "config", "PROTOCOL_E08_DRAFT_v2.md", "experiments/E08_confirmation/run_e08.py", "experiments/E08_confirmation/run_e08_descriptive.py"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
fz2 = subprocess.run(["git", "diff", "--stat", "e08-confirmation", "--", "experiments/E08_confirmation/confirmation_2026"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
check("frozen_files_unchanged", fz1 == "" and fz2 == "", "empty diff vs protocol-freeze (code, config, protocol) and e08-confirmation (results)")
for stem, (wmm, hmm) in SPEC.items():
    info = subprocess.run(["pdfinfo", str(FIG / f"{stem}.pdf")], capture_output=True, text=True).stdout
    pw, ph = [float(v) for v in re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info).groups()]
    check(f"{stem}_exact_size", abs(pw * 25.4 / 72 - wmm) < 0.1 and abs(ph * 25.4 / 72 - hmm) < 0.1, f"{pw * 25.4 / 72:.2f} x {ph * 25.4 / 72:.2f} mm (spec {wmm} x {hmm})")
    words = subprocess.run(["pdftotext", "-bbox", str(FIG / f"{stem}.pdf"), "-"], capture_output=True, text=True).stdout
    boxes = [tuple(float(v) for v in m) for m in re.findall(r'xMin="([\d.-]+)" yMin="([\d.-]+)" xMax="([\d.-]+)" yMax="([\d.-]+)"', words)]
    inside = all(b[0] >= -0.5 and b[1] >= -0.5 and b[2] <= pw + 0.5 and b[3] <= ph + 0.5 for b in boxes)
    texts = re.findall(r">([^<]+)</word>", words); panel = [t for t in texts if re.fullmatch(r"\([a-z]\)", t.strip())]
    check(f"{stem}_text_inside_no_panel_labels", inside and not panel, f"{len(boxes)} words, all inside page: {inside}; panel labels: {panel}")
for stem in SPEC:
    pdf = FIG / f"{stem}.pdf"; fonts = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
    emb = all(l.split()[-5] == "yes" for l in fonts if l.strip()); imgs = subprocess.run(["pdfimages", "-list", str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
    svg = (FIG / f"{stem}.svg").read_text(); png = FIG / f"{stem}_600dpi.png"
    from PIL import Image
    dpi = Image.open(png).info.get("dpi", (0, 0))[0]
    check(f"{stem}_vector_embedded", emb and len(fonts) > 0 and len(imgs) == 0 and "<image" not in svg and "<text" in svg and round(dpi) == 600,
          f"fonts embedded: {emb} ({len(fonts)} font(s)); raster images in PDF: {len(imgs)}; SVG text as text: {'<text' in svg}; PNG dpi: {round(dpi)}")
t1 = (TAB / "table01_station_characteristics.tex").read_text(); t2 = (TAB / "table02_data_sources_temporal_design.tex").read_text()
bad = re.compile(r"E0\d|H[123]\b|passed|failed|significan|p-value|confirmed", re.I)
check("tables_booktabs_no_results", all(k in t for t in (t1, t2) for k in (r"\toprule", r"\midrule", r"\bottomrule")) and "|" not in t1 + t2 and not bad.search(t1 + t2),
      "booktabs rules present; no vertical lines; no experiment IDs, hypothesis results or significance language")
(DATA / "validation_report.json").write_text(json.dumps(R, indent=1)); [print(("PASS " if v["passed"] else "FAIL ") + k + ": " + v["detail"]) for k, v in R.items()]
sys.exit(0 if ok else 1)
