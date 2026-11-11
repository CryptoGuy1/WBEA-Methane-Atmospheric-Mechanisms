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
L = [r"\begin{table}[t]", r"\centering", r"\caption{Geographic characteristics and observational variables of the WBEA atmospheric monitoring stations included in the study.}",
     r"\label{tab:stations}", r"\small", r"\begin{tabular}{llrrll}", r"\toprule",
     r"Station & Name & Lat. ($^\circ$N) & Long. ($^\circ$W) & Wind heights (m)\textsuperscript{a} & Air temperature heights (m) \\", r"\midrule"]
for r in rows: L.append(f"{r['id']} & {esc(r['name'])} & {r['lat']} & {r['lon']} & {r['wind']} & {r['temp']} \\\\")
L += [r"\bottomrule", r"\end{tabular}", r"\par\smallskip\footnotesize",
      r"\textit{Notes.} Hourly methane (CH$_4$, ppm) is measured at all 12 stations by WBEA continuous total hydrocarbon/methane/non-methane hydrocarbon analysers with a daily automated zero/span check (WBEA SOP-ANA-008); the analyser model is verified from site documentation only for AMS~5 (Thermo~55i). Coordinates: WBEA 2024 site documents. Heights list variables with at least 5\% valid hours in 2021--2025 exports. "
      r"\textsuperscript{a}Where both 10 and 20~m are listed, 10~m is used when valid and 20~m otherwise. AMS~5 provides the 20--90~m tower temperature gradient used for atmospheric stability. Station relocations before 2024 have not been verified.",
      r"\end{table}"]
(TAB / "table01_station_characteristics.tex").write_text("\n".join(L) + "\n")
D = [("Methane (CH$_4$)", "Hourly averages (ppm), WBEA continuous monitoring, final validated data (exported 9 Nov 2026)", "WBEA"),
     ("Surface wind", "Hourly speed and direction; 10~m where valid, otherwise 20~m; converted to m\\,s$^{-1}$", "WBEA"),
     ("Atmospheric stability", "AMS~5 tower temperature difference, 90~m minus 20~m ($^\\circ$C); ERA5 boundary-layer height as an independent proxy", "WBEA; Copernicus ERA5"),
     ("Station coordinates", "Latitude/longitude, WGS84 (Table~\\ref{tab:stations})", "WBEA site documents (2024)"),
     ("Temporal resolution", "1~h", "--"),
     ("Time convention", "Mountain Standard Time (UTC$-$7, no daylight saving), hour-ending", "WBEA monthly reports"),
     ("Development period", "1 Jan 2021 01:00 -- 2 Dec 2025 00:00 (1,796 days); exploratory analysis", "--"),
     ("Fixed reference period", "2021--2023: station medians, 95th-percentile thresholds, stability standardisation and terciles", "--"),
     ("Independent confirmation period", "1 Jan 2026 01:00 -- 1 Oct 2026 00:00 (273 days); sealed until methods were frozen; final validated under WBEA's 30-day rule", "WBEA"),
     ("Seasonal comparison windows", "1 Jan -- 30 Sep of each year, used only where development and confirmation years are compared", "--"),
     ("Missing values", "Zero/span (Z), calibration (C) and invalid/maintenance (.) hours treated as missing, never as zero; no imputation; stations with $<50$\\% valid CH$_4$ hours in the confirmation period excluded", "WBEA monthly report (Sep 2024); Alberta AMD Ch.~6")]
L = [r"\begin{table}[t]", r"\centering", r"\caption{Observational datasets, temporal partitions, and preprocessing characteristics used in the methane-monitoring analysis.}",
     r"\label{tab:data}", r"\small", r"\begin{tabular}{p{0.22\linewidth}p{0.52\linewidth}p{0.19\linewidth}}", r"\toprule", r"Item & Specification & Source \\", r"\midrule"]
L += [f"{a} & {b} & {c} \\\\" for a, b, c in D] + [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
(TAB / "table02_data_sources_temporal_design.tex").write_text("\n".join(L) + "\n")
pd.DataFrame(D, columns=["item", "specification", "source"]).to_csv(DATA / "table02_data_sources_temporal_design.csv", index=False)
print(T.to_string(index=False))
