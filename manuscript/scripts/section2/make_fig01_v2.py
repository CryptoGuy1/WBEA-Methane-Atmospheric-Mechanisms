"""Fig. 1 (revision 2): one coherent network map (UTM 12N) with a compact, unlabelled location inset (EPSG:3978).
No titles, no panel labels. Exact canvas 180 mm wide (saved without bbox cropping). Pairs: frozen E08 list (21)."""
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import box, Point
from pyproj import Transformer
from common import plt, MM, DATA, GIS, STUDY, EXCLUDED, save_exact
import common; save_exact.__globals__["FIG"] = common.FIG / "archive_v2"   # v2 outputs go to archive_v2
LCC, UTM = "EPSG:3978", "EPSG:32612"
st = pd.read_csv(DATA / "stations_study.csv").set_index("station_id"); pairs = pd.read_csv(DATA / "pairs_frozen.csv")
g = lambda n: gpd.read_file(GIS / n)
countries, prov = g("ne_50m_admin_0_countries_clip.geojson"), g("ne_50m_admin_1_states_provinces_clip.geojson")
lakes, rivers, places = g("ne_10m_lakes_clip.geojson"), g("ne_10m_rivers_lake_centerlines_clip.geojson"), g("ne_10m_populated_places_selected.geojson")
pts = gpd.GeoDataFrame(st, geometry=[Point(lo, la) for la, lo in zip(st.latitude_deg_n, st.longitude_deg_e)], crs="EPSG:4326").to_crs(UTM)
P = {s: (p.x, p.y) for s, p in zip(pts.index, pts.geometry)}
C_LAND, C_WATER, C_RIVER, C_ST, C_EX, C_PAIR = "#f4f4f4", "#c6dbef", "#6baed6", "#08519c", "#8c8c8c", "#a3a3a3"
tr = Transformer.from_crs("EPSG:4326", UTM, always_xy=True); inv = Transformer.from_crs(UTM, "EPSG:4326", always_xy=True)
x0, y0 = tr.transform(-111.97, 56.38); x1, y1 = tr.transform(-110.80, 57.43)
W_MM = 92.0; H_MM = W_MM * (y1 - y0) / (x1 - x0)
FIG_W, LEFT, BOT, TOP = 180.0, 11.0, 7.0, 2.0; FIG_H = BOT + H_MM + TOP
fig = plt.figure(figsize=(FIG_W * MM, FIG_H * MM))
ax = fig.add_axes([LEFT / FIG_W, BOT / FIG_H, W_MM / FIG_W, H_MM / FIG_H]); ax.set_facecolor(C_LAND)
clip = gpd.GeoSeries([box(x0, y0, x1, y1)], crs=UTM).to_crs(4326).iloc[0].buffer(0.05)
lakes[lakes.intersects(clip)].to_crs(UTM).plot(ax=ax, color=C_WATER, edgecolor="none", zorder=1)
rivers[rivers.intersects(clip)].to_crs(UTM).plot(ax=ax, color=C_RIVER, lw=0.8, zorder=1.2)
for _, r in pairs.iterrows():
    (xa, ya), (xb, yb) = P[r.i], P[r.j]; ax.plot([xa, xb], [ya, yb], c=C_PAIR, lw=0.5, zorder=2, solid_capstyle="round")
OFF = {"AMS 23": (6, 0, "left"), "AMS 30": (-6, 0, "right"), "AMS 9": (6, 2, "left"), "AMS 1": (-6, 3, "right"), "AMS 13": (-6, -3, "right"),
       "AMS 2": (-6, 0, "right"), "AMS 11": (6, 0, "left"), "AMS 5": (6, -1, "left"), "AMS 6": (-6, 0, "right"), "AMS 7": (6, 3, "left"), "AMS 14": (6, 0, "left")}
for s in STUDY:
    if s == "AMS 18": continue
    x, y = P[s]
    if s in EXCLUDED: ax.scatter(x, y, s=24, marker="s", facecolor="white", edgecolor=C_EX, lw=0.9, zorder=4)
    else: ax.scatter(x, y, s=22, marker="o", facecolor=C_ST, edgecolor="white", lw=0.5, zorder=4)
    dx, dy, ha = OFF[s]
    ax.annotate(s, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=7, color=C_EX if s in EXCLUDED else "k", zorder=5)
fm = places[places["name"] == "Fort McMurray"].to_crs(UTM).iloc[0].geometry
ax.scatter(fm.x, fm.y, s=14, marker="^", c="#525252", lw=0, zorder=3)
ax.annotate("Fort McMurray", (fm.x, fm.y), xytext=(4, -8), textcoords="offset points", ha="left", va="center", fontsize=6.5, style="italic", color="#525252")
ax.text(*tr.transform(-111.53, 57.30), "Athabasca\nRiver", fontsize=6, style="italic", color="#2171b5", ha="left", va="center")
x18, _ = P["AMS 18"]
ax.annotate("", xy=(x18, y0 + 0.003 * (y1 - y0)), xytext=(x18, y0 + 0.055 * (y1 - y0)), arrowprops=dict(arrowstyle="-|>", lw=0.6, color="#525252"))
ax.text(x18 - 1.5e3, y0 + 0.033 * (y1 - y0), "AMS 18 (Stony Mountain), off map:\n55.62°N, 111.17°W; 92 km S of AMS 14", fontsize=6, va="center", ha="right", color="#3a3a3a")
for lo in (-111.8, -111.4, -111.0):
    la = np.linspace(56.2, 57.6, 200); xs, ys = tr.transform(np.full_like(la, lo), la); ax.plot(xs, ys, lw=0.3, c="#d0d0d0", zorder=0.6)
LATS = (56.4, 56.6, 56.8, 57.0, 57.2, 57.4)
for la in LATS:
    lo = np.linspace(-112.2, -110.6, 200); xs, ys = tr.transform(lo, np.full_like(lo, la)); ax.plot(xs, ys, lw=0.3, c="#d0d0d0", zorder=0.6)
xt = [tr.transform(lo, inv.transform((x0 + x1) / 2, y0)[1])[0] for lo in (-111.8, -111.4, -111.0)]
yt = [tr.transform(inv.transform(x0, (y0 + y1) / 2)[0], la)[1] for la in LATS]
ax.set_xticks(xt, ["111.8°W", "111.4°W", "111.0°W"]); ax.set_yticks(yt, [f"{la:.1f}°N" for la in LATS])
ax.tick_params(length=2, pad=1.5, labelsize=6.5); ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.set_xlabel(""); ax.set_ylabel("")
sb_x, sb_y = x0 + 0.60 * (x1 - x0), y0 + 0.13 * (y1 - y0)
ax.plot([sb_x, sb_x + 20e3], [sb_y, sb_y], c="k", lw=1.3, solid_capstyle="butt")
ax.text(sb_x + 10e3, sb_y + 0.012 * (y1 - y0), "20 km", ha="center", va="bottom", fontsize=6.5)
ax.annotate("N", xy=(0.93, 0.965), xytext=(0.93, 0.905), xycoords="axes fraction", ha="center", va="center", fontsize=7,
            arrowprops=dict(arrowstyle="-|>", lw=0.7, color="k", shrinkA=0, shrinkB=0))
IX = LEFT + W_MM + 9.0; IW = FIG_W - IX - 2.0; IH = IW * 0.95; IY = BOT + H_MM - IH
ins = fig.add_axes([IX / FIG_W, IY / FIG_H, IW / FIG_W, IH / FIG_H]); ins.set_facecolor(C_WATER)
countries.to_crs(LCC).plot(ax=ins, color=C_LAND, edgecolor="#8c8c8c", lw=0.35, zorder=1)
pv = prov.to_crs(LCC); pv[pv.iso_a2 == "CA"].plot(ax=ins, facecolor="none", edgecolor="#b0b0b0", lw=0.3, zorder=1.5)
pv[pv["name"] == "Alberta"].plot(ax=ins, color="#d9d9d9", edgecolor="#525252", lw=0.6, zorder=1.6)
gpd.GeoSeries([box(-111.97, 56.38, -110.80, 57.43)], crs=4326).to_crs(LCC).plot(ax=ins, facecolor="none", edgecolor="#b2182b", lw=1.0, zorder=3)
tl = Transformer.from_crs("EPSG:4326", LCC, always_xy=True)
ins.text(*tl.transform(-115.5, 52.6), "Alberta", fontsize=6.5, ha="center", color="#252525")
ins.text(*tl.transform(-103, 63), "CANADA", fontsize=7, ha="center", color="#636363")
ins.text(*tl.transform(-101, 44.5), "USA", fontsize=6.5, ha="center", color="#8c8c8c")
ins.set_xlim(-2.2e6, 2.2e6); ins.set_ylim(-0.6e6, -0.6e6 + 4.4e6 * IH / IW); ins.set_xticks([]); ins.set_yticks([]); ins.set_aspect("auto")
for sp in ins.spines.values(): sp.set_linewidth(0.6)
ins.set_xlabel(""); ins.set_ylabel("")
H = [plt.Line2D([], [], marker="o", ls="", mfc=C_ST, mec="white", ms=5, label="Monitoring station"),
     plt.Line2D([], [], marker="s", ls="", mfc="white", mec=C_EX, ms=5, label="Excluded station (< 50% valid CH$_4$, 2026)"),
     plt.Line2D([], [], c=C_PAIR, lw=1.0, label="Eligible station pair (n = 21)"),
     plt.Line2D([], [], marker="^", ls="", c="#525252", ms=4.5, label="Community"),
     plt.Line2D([], [], c=C_RIVER, lw=1.2, label="River and lakes"),
     plt.Rectangle((0, 0), 1, 1, fc="none", ec="#b2182b", lw=1.0, label="Extent of main map")]
fig.legend(handles=H, loc="upper left", bbox_to_anchor=(IX / FIG_W, (IY - 4.0) / FIG_H), frameon=False, fontsize=7, handlelength=1.8, labelspacing=0.75, borderaxespad=0)
fig.text(IX / FIG_W, (IY - 36.0) / FIG_H, "Base data: Natural Earth (public domain).\nStations: WBEA site documents (2024).\nProjection: UTM zone 12N; inset: Canada Atlas Lambert.",
         fontsize=6, color="#5a5a5a", va="top")
save_exact(fig, "fig01_wbea_network")
print(f"fig01 canvas {FIG_W:.1f} x {FIG_H:.1f} mm; map {W_MM:.1f} x {H_MM:.1f} mm; pairs {len(pairs)}")
