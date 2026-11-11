"""Table 1 (station characteristics) and Table 2 (datasets and temporal design), LaTeX booktabs. Facts come from
metadata, the exported variable lists (non-empty columns), the frozen protocol/config and official WBEA documents."""
import pandas as pd
from common import ROOT, TAB, DATA, STUDY
from wbea.io import load_dev
st = pd.read_csv(DATA / "stations_study.csv").set_index("station_id"); P = load_dev(STUDY)
def present(d, pref):                                    # heights with >= 5% valid hours in the development export
    return sorted({int(c.split()[0][len(pref):]) for c in d.columns if c.startswith(pref) and "__" not in c and "STD" not in c
                   and c.split()[0][len(pref):].isdigit() and d[c].notna().mean() >= 0.05})
rows = []
for s in STUDY:
    d = P[s]; ws = present(d, "WS"); at = present(d, "AT")
    rows.append(dict(id=s, name=st.loc[s, "station_name"], lat=f"{st.loc[s, 'latitude_deg_n']:.4f}", lon=f"{-st.loc[s, 'longitude_deg_e']:.4f}",
                     wind=", ".join(str(h) for h in ws), temp=", ".join(str(h) for h in at)))
T = pd.DataFrame(rows); T.to_csv(DATA / "table01_station_characteristics.csv", index=False)
esc = lambda x: str(x).replace("&", r"\&").replace("_", r"\_")
L = [r"\begin{table*}[t]", r"\centering", r"\caption{Geographic characteristics and meteorological measurement heights of the WBEA atmospheric monitoring stations included in the study.}",
     r"\label{tab:stations}", r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}llrrll@{}}", r"\toprule",
     r"Station & Name & Latitude ($^\circ$N) & Longitude ($^\circ$W) & Wind height (m) & Temperature height (m) \\", r"\midrule"]
for r in rows: L.append(f"{r['id']} & {esc(r['name'])} & {r['lat']} & {r['lon']} & {r['wind']} & {r['temp']} \\\\")
L += [r"\bottomrule", r"\end{tabular*}", r"\par\smallskip\begin{minipage}{\textwidth}\footnotesize",
      r"Coordinates (WGS84) from WBEA 2024 site documents. Heights (m above ground) list variables with at least 5\% valid hourly values in the 2021--2025 exports; where 10 and 20~m are both listed, the 10~m sensor is used when valid. "
      r"Methane, total hydrocarbons and non-methane hydrocarbons are reported together at every station (ppm, hourly) by WBEA's continuous hydrocarbon analysers, with an automated zero/span check that occupies one hour per day and is flagged in the data (WBEA SOP-ANA-008; WBEA monthly reports). "
      r"The analyser model is documented here only for AMS~5 (Thermo~55i, installed 2021); WBEA reports analyser replacements at AMS~5 and AMS~23 in September 2024. AMS~5 has a meteorological tower with sensors at 20--90~m; its 90 minus 20~m temperature difference is the stability measure.",
      r"\end{minipage}", r"\end{table*}"]
(TAB / "table01_station_characteristics.tex").write_text("\n".join(L) + "\n")
D = [("Methane", "CH$_4$ (ppm)", "WBEA continuous monitoring, final validated data", "1~h", "2021--2026"),
     ("Surface wind", "Speed (m\\,s$^{-1}$) and direction ($^\\circ$)", "WBEA continuous monitoring", "1~h", "2021--2026"),
     ("Air temperature", "Temperature ($^\\circ$C) at 2--90~m; AMS~5 tower gradient", "WBEA continuous monitoring", "1~h", "2021--2026"),
     ("Boundary-layer height", "ERA5 boundary-layer height (m)", "Copernicus Climate Change Service, ERA5", "1~h", "2021--2026"),
     ("Station locations", "Latitude, longitude (WGS84)", "WBEA site documents (2024)", "--", "--")]
dv = pd.read_csv(DATA / "ch4_daily_availability_2021_2025.csv", parse_dates=["day"]); cf = pd.read_csv(DATA / "ch4_daily_availability_2026_jan_sep.csv")
def rng(d):
    v = 100 * d.groupby("station").valid_hours.sum() / d.groupby("station").hours.sum(); return f"{v.min():.1f}--{v.max():.1f}\\%", v
r_dev, _ = rng(dv); r_ref, _ = rng(dv[dv.day.dt.year <= 2023]); r_cf, v_cf = rng(cf)
r_cf = f"{v_cf.drop('AMS 2').min():.1f}--{v_cf.max():.1f}\\%\\textsuperscript{{a}}"
T = [("Development", "1 Jan 2021 01:00 -- 2 Dec 2025 00:00", r_dev, "Exploratory analysis and method development"),
     ("Reference", "1 Jan 2021 01:00 -- 31 Dec 2023 23:00", r_ref, "Fixed station medians, thresholds and stability scaling"),
     ("Confirmation", "1 Jan 2026 01:00 -- 1 Oct 2026 00:00", r_cf, "Independent confirmation, sealed until methods were frozen")]
L = [r"\begin{table*}[t]", r"\centering", r"\caption{Observational datasets and temporal design of the methane-monitoring analysis.}", r"\label{tab:data}",
     r"\begin{tabularx}{\textwidth}{@{}l>{\raggedright\arraybackslash}X>{\raggedright\arraybackslash}Xll@{}}", r"\toprule", r"Dataset & Variables (units) & Source & Resolution & Years \\", r"\midrule"]
L += [" & ".join(x) + r" \\" for x in D] + [r"\bottomrule", r"\end{tabularx}", r"\par\medskip",
      r"\begin{tabularx}{\textwidth}{@{}llc>{\raggedright\arraybackslash}X@{}}", r"\toprule", r"Temporal partition & Dates (MST, hour-ending) & Valid CH$_4$ hours by station & Use \\", r"\midrule"]
L += [f"{a} & {b} & {c} & {d} \\\\" for a, b, c, d in T]
L += [r"\bottomrule", r"\end{tabularx}", r"\par\smallskip\begin{minipage}{\textwidth}\footnotesize",
      r"All timestamps are Mountain Standard Time (UTC$-$7, no daylight saving) and refer to the end of the hourly averaging period, as in WBEA reporting. Valid CH$_4$ hours: range across stations of the share of hours with a valid value (zero/span, calibration and invalid hours count as missing). Missing-value handling, station and pair eligibility, and comparison windows are described in Section~3. \textsuperscript{a}Excluding AMS~2 (41.2\%), which fell below the 50\% completeness criterion.",
      r"\end{minipage}", r"\end{table*}"]
(TAB / "table02_data_sources_temporal_design.tex").write_text("\n".join(L) + "\n")
pd.DataFrame(D, columns=["dataset", "variables", "source", "resolution", "years"]).to_csv(DATA / "table02_datasets.csv", index=False)
pd.DataFrame(T, columns=["partition", "dates", "valid_ch4_hours_station_range", "use"]).to_csv(DATA / "table02_temporal_partitions.csv", index=False)
print(T)
