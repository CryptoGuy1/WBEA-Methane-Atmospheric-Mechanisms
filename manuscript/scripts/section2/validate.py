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
SPEC = {"fig01_wbea_network": (180.0, 158.0), "fig02_ch4_availability_2026": (180.0, 70.0), "fig02_ch4_availability_2026_single_column": (90.0, 92.0),
        "figS1_ch4_availability_2021_2025": (180.0, 70.0), "figS1b_ch4_availability_2021_2025_monthly": (180.0, 66.0)}
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
