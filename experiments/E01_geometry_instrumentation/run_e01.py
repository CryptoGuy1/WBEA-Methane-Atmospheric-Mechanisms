"""E01 - Station geometry and instrumentation verification (development data; re-implements the R1
geometry with the repository library so that all later experiments share one code path).
Outputs: pairwise geometry (66 pairs), frozen H2 family (<= 30 km), eligibility counts, instrumentation
table, wind roses, main Figure 1."""
import sys, pathlib, numpy as np, pandas as pd
EXP = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(EXP.parents[1] / "src"))
from wbea.config import CFG
from wbea.io import load_dev
from wbea.geometry import stations, pair_table
from wbea.wind import composite
from wbea import runmeta
from wbea.plotstyle import plt, save

RES = EXP / "results"; FIG = EXP / "figures"; RES.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
P = load_dev(); ST = CFG["stations"]["usable"]; XY = stations(); H2 = CFG["h2"]
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); W = {s: composite(P[s]) for s in ST}

geo = pair_table(ST).round({"km": 3, "bearing": 1}); geo["in_h2_family"] = geo.km <= H2["max_pair_km"]
geo.to_csv(RES / "pairwise_geometry.csv", index=False)
fam = geo[geo.in_h2_family].reset_index(drop=True)

rows = []
for _, r in fam.iterrows():
    a, b = r.i, r.j; phi = np.deg2rad(r.bearing)
    u = (W[a].u + W[b].u) / 2; v = (W[a].v + W[b].v) / 2
    upar = u * np.sin(phi) + v * np.cos(phi); sp = np.hypot(u, v); tau = r.km / (3.6 * upar.abs())
    ok = CH[a].diff().notna() & CH[b].diff().notna() & CH.drop(columns=[a, b]).notna().sum(1).ge(H2["kmin_other_stations"])
    e = ok & (upar.abs() >= H2["align_cos"] * sp) & (upar.abs() >= H2["u_min_ms"]) & (tau <= H2["max_tau_h"])
    rows.append(dict(pair=f"{a}->{b}", km=r.km, bearing=r.bearing, aligned_h=int((e & (upar > 0)).sum()),
                     reversed_h=int((e & (upar < 0)).sum()), median_tau_h=round(float(tau[e].median()), 2),
                     share_tau_lt_0_5=round(float((tau[e] < .5).mean()), 2),
                     share_hours_20m_wind=round(float(((W[a].height_m == 20) | (W[b].height_m == 20))[e].mean()), 2)))
elig = pd.DataFrame(rows); elig.to_csv(RES / "h2_family_eligibility.csv", index=False)

inst = []
for s in ST:
    d = P[s]; hs = sorted({c.split(" ")[0][2:] for c in d.columns if c.startswith("WS") and "STD" not in c and "__" not in c})
    inst.append(dict(station=s, lat=XY[s][0], lon=XY[s][1], wind_heights_m=";".join(hs),
                     composite_wind_share_20m=round(float((W[s].height_m == 20).mean()), 3),
                     temperature_levels=";".join(sorted(c.split(" ")[0] for c in d.columns if c.startswith("AT") and "__" not in c)),
                     stability_proxy_usable={"AMS 5": "T90-T20 (tower)", "AMS 1": "T10-T2"}.get(s, "no"),
                     analyser_and_history="Thermo 55i installed 2021; tower sensors replaced 2022 (SDOC Mar 2024)" if s == "AMS 5"
                     else "pending site documents"))
pd.DataFrame(inst).to_csv(RES / "instrumentation.csv", index=False)

# ---------------- Figure 1: core network in km relative to AMS 5, overview inset, wind roses
fig = plt.figure(figsize=(7.4, 4.9)); gs = fig.add_gridspec(2, 3, width_ratios=[1.3, 1, 1], hspace=0.55, wspace=0.35)
ax = fig.add_subplot(gs[:, 0]); la0, lo0 = XY["AMS 5"]
def km(s): return ((XY[s][1] - lo0) * 111.32 * np.cos(np.deg2rad(57.0)), (XY[s][0] - la0) * 110.57)
for _, r in fam.iterrows():
    (x1, y1), (x2, y2) = km(r.i), km(r.j); ax.plot([x1, x2], [y1, y2], "-", c="0.8", lw=0.6, zorder=1)
core = CFG["stations"]["h1_core_response"]
off = {"AMS 1": (-14, 2), "AMS 9": (4, 3), "AMS 13": (-14, -7), "AMS 30": (-14, 2), "AMS 2": (-12, 1), "AMS 11": (4, 1)}
for s in ST:
    if s in ("AMS 14", "AMS 18"): continue
    x, y = km(s); col = "C3" if s == "AMS 5" else ("k" if s in core else "C0")
    ax.scatter(x, y, s=24, c=col, zorder=3)
    ax.annotate(s.replace("AMS ", ""), (x, y), xytext=off.get(s, (4, 2)), textcoords="offset points", fontsize=7)
ax.set_aspect("equal"); ax.set_xlabel("km east of AMS 5"); ax.set_ylabel("km north of AMS 5")
ax.set_title("a  Core network, 27 H2 pairs (<= 30 km)")
ins = fig.add_subplot(gs[0, 1])

for s in ST:
    ins.scatter(XY[s][1], XY[s][0], s=6, c="C3" if s == "AMS 5" else ("k" if s in core else "C0"))
for s in ("AMS 14", "AMS 18"):
    ins.annotate(s.replace("AMS ", ""), (XY[s][1], XY[s][0]), xytext=(3, 0), textcoords="offset points", fontsize=6)
ins.set_aspect(1 / np.cos(np.deg2rad(57.0))); ins.set_xticks([])
ins.tick_params(labelsize=6); ins.set_title("b  All 12 stations (111.0-111.7 W)", fontsize=7); ins.set_ylabel("Latitude (deg N)", fontsize=6)
for k, s in enumerate(["AMS 1", "AMS 5", "AMS 7"]):
    a = fig.add_subplot([gs[0, 2], gs[1, 1], gs[1, 2]][k], projection="polar"); a.set_theta_zero_location("N"); a.set_theta_direction(-1)
    wd = W[s].wd.dropna(); sec = (np.round(wd / 22.5) % 16).astype(int); f = sec.value_counts(normalize=True).reindex(range(16), fill_value=0)
    a.bar(np.deg2rad(np.arange(16) * 22.5), 100 * f.values, width=np.deg2rad(20), color="0.4")
    a.set_yticklabels([]); a.set_xticks(np.deg2rad([0, 90, 180, 270])); a.set_xticklabels(["N", "E", "S", "W"], fontsize=6)
    a.set_title(f"{'cde'[k]}  {s} wind-from\nn = {len(wd):,}", fontsize=7, pad=10)
fig.text(0.01, -0.02, "Black: H1 core-response stations; red: AMS 5 tower (stability S); blue: stations added in R1. Official 2024 coordinates.\nWind roses: composite station wind (10 m with 20 m fill; AMS 5 at 20 m), "
         "16 sectors, development period 2021-01-01 to 2025-12-02.", fontsize=6.3)
save(fig, FIG / "figure01_network_geometry")
runmeta.write(EXP, dict(experiment="E01_geometry_instrumentation", status="exploratory (metadata verification)"))
print(len(geo), "pairs;", len(fam), "in family"); print(elig[["pair", "aligned_h", "reversed_h"]].min(numeric_only=True).to_dict())
