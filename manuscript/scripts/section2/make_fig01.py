"""Fig. 1 (revision 3, final specification): the three original map components are retained - regional context
(EPSG:3978), full monitoring network (UTM 12N) and enlarged station cluster (UTM 12N) - without panel letters or internal
titles. Exact canvas = Elsevier CAS double-column \\textwidth (174.5 mm), saved without bbox cropping."""
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import box, Point
from pyproj import Transformer
from matplotlib.patches import Rectangle
from common import plt, MM, DATA, GIS, STUDY, EXCLUDED, save_exact
LCC, UTM = "EPSG:3978", "EPSG:32612"
st = pd.read_csv(DATA / "stations_study.csv").set_index("station_id"); pairs = pd.read_csv(DATA / "pairs_frozen.csv")
g = lambda n: gpd.read_file(GIS / n)
countries, prov = g("ne_50m_admin_0_countries_clip.geojson"), g("ne_50m_admin_1_states_provinces_clip.geojson")
lakes, rivers, places = g("ne_10m_lakes_clip.geojson"), g("ne_10m_rivers_lake_centerlines_clip.geojson"), g("ne_10m_populated_places_selected.geojson")
pts = gpd.GeoDataFrame(st, geometry=[Point(lo, la) for la, lo in zip(st.latitude_deg_n, st.longitude_deg_e)], crs="EPSG:4326").to_crs(UTM)
P = {s: (p.x, p.y) for s, p in zip(pts.index, pts.geometry)}
C_LAND, C_AB, C_WATER, C_RIVER, C_ST, C_EX, C_PAIR, C_BOX = "#f4f4f4", "#d9d9d9", "#c6dbef", "#6baed6", "#08519c", "#8c8c8c", "#a3a3a3", "#b2182b"
tu = Transformer.from_crs("EPSG:4326", UTM, always_xy=True); iu = Transformer.from_crs(UTM, "EPSG:4326", always_xy=True)
tl = Transformer.from_crs("EPSG:4326", LCC, always_xy=True)
FIG_W, FIG_H = 174.5, 118.0; BOT, TOP = 7.0, 1.5; MAP_H = FIG_H - BOT - TOP
fig = plt.figure(figsize=(FIG_W * MM, FIG_H * MM))
def axes_mm(x, y, w, h): return fig.add_axes([x / FIG_W, y / FIG_H, w / FIG_W, h / FIG_H])

def utm_ticks(ax, ext, lons, lats, fmt_lon="{:.1f}°W", fmt_lat="{:.1f}°N"):
    x0, x1, y0, y1 = ext
    for lo in lons:
        la = np.linspace(55.0, 58.0, 200); xs, ys = tu.transform(np.full_like(la, lo), la); ax.plot(xs, ys, lw=0.3, c="#d0d0d0", zorder=0.6)
    for la in lats:
        lo = np.linspace(-113.0, -110.0, 200); xs, ys = tu.transform(lo, np.full_like(lo, la)); ax.plot(xs, ys, lw=0.3, c="#d0d0d0", zorder=0.6)
    xt = [tu.transform(lo, iu.transform((x0 + x1) / 2, y0)[1])[0] for lo in lons]; yt = [tu.transform(iu.transform(x0, (y0 + y1) / 2)[0], la)[1] for la in lats]
    keep_x = [(x, fmt_lon.format(abs(lo))) for x, lo in zip(xt, lons) if x0 < x < x1]; keep_y = [(y, fmt_lat.format(la)) for y, la in zip(yt, lats) if y0 < y < y1]
    ax.set_xticks([k[0] for k in keep_x], [k[1] for k in keep_x]); ax.set_yticks([k[0] for k in keep_y], [k[1] for k in keep_y])
    ax.tick_params(length=2, pad=1.5, labelsize=6.5); ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.set_xlabel(""); ax.set_ylabel("")

def local_base(ax, ext):
    x0, x1, y0, y1 = ext; ax.set_facecolor(C_LAND)
    clip = gpd.GeoSeries([box(x0, y0, x1, y1)], crs=UTM).to_crs(4326).iloc[0].buffer(0.05)
    lakes[lakes.intersects(clip)].to_crs(UTM).plot(ax=ax, color=C_WATER, edgecolor="none", zorder=1)
    rivers[rivers.intersects(clip)].to_crs(UTM).plot(ax=ax, color=C_RIVER, lw=0.8, zorder=1.2)

def network(ax, labels, lw=0.5, ms=20):
    for _, r in pairs.iterrows():
        (xa, ya), (xb, yb) = P[r.i], P[r.j]; ax.plot([xa, xb], [ya, yb], c=C_PAIR, lw=lw, zorder=2, solid_capstyle="round")
    for s in STUDY:
        x, y = P[s]
        if s in EXCLUDED: ax.scatter(x, y, s=ms * 1.1, marker="s", facecolor="white", edgecolor=C_EX, lw=0.9, zorder=4, gid=f"station:{s}")
        else: ax.scatter(x, y, s=ms, marker="o", facecolor=C_ST, edgecolor="white", lw=0.5, zorder=4, gid=f"station:{s}")
        if s in labels:
            dx, dy, ha = labels[s]
            ax.annotate(s, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=6.8, color=C_EX if s in EXCLUDED else "k", zorder=5)

def fort_mcmurray(ax, crs, dx, dy, ha="left"):
    p = places[places["name"] == "Fort McMurray"].to_crs(crs).iloc[0].geometry
    ax.scatter(p.x, p.y, s=12, marker="^", c="#525252", lw=0, zorder=3.5)
    ax.annotate("Fort McMurray", (p.x, p.y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=6.3, style="italic", color="#525252")

def scalebar(ax, km, xf, yf):
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim(); x = x0 + xf * (x1 - x0); y = y0 + yf * (y1 - y0)
    ax.plot([x, x + km * 1e3], [y, y], c="k", lw=1.2, solid_capstyle="butt"); ax.text(x + km * 500, y + 0.012 * (y1 - y0), f"{km} km", ha="center", va="bottom", fontsize=6.3)

def north(ax, xf, yf):
    ax.annotate("N", xy=(xf, yf), xytext=(xf, yf - 0.06), xycoords="axes fraction", ha="center", va="center", fontsize=6.8,
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color="k", shrinkA=0, shrinkB=0))

# ---------------- component 3: enlarged station cluster (right)
core = (P["AMS 30"][0] - 6e3, P["AMS 7"][0] + 9e3, P["AMS 7"][1] - 7e3, P["AMS 23"][1] + 6e3)
cw = MAP_H * (core[1] - core[0]) / (core[3] - core[2]); cx = FIG_W - 1.5 - cw
c = axes_mm(cx, BOT, cw, MAP_H); local_base(c, core)
network(c, {"AMS 23": (5, 0, "left"), "AMS 30": (0, 7, "center"), "AMS 9": (5, 2, "left"), "AMS 1": (-5, 2, "right"), "AMS 13": (-5, -2, "right"),
            "AMS 2": (-5, 0, "right"), "AMS 11": (5, 2, "left"), "AMS 5": (5, -2, "left"), "AMS 6": (-5, 0, "right"), "AMS 7": (5, 1, "left")}, lw=0.55, ms=22)
fort_mcmurray(c, UTM, 2, -8, "center")
utm_ticks(c, core, [-111.7, -111.5], [56.8, 57.0, 57.2, 57.4]); scalebar(c, 10, 0.06, 0.04); north(c, 0.9, 0.97)
# ---------------- component 2: full monitoring network (middle)
ext = (P["AMS 18"][0] - 50e3, P["AMS 18"][0] + 42e3, P["AMS 18"][1] - 14e3, P["AMS 23"][1] + 14e3)
nw = MAP_H * (ext[1] - ext[0]) / (ext[3] - ext[2]); nx = cx - 10.5 - nw
b = axes_mm(nx, BOT, nw, MAP_H); local_base(b, ext)
network(b, {"AMS 14": (5, 0, "left"), "AMS 18": (5, 0, "left")}, lw=0.4, ms=14)
fort_mcmurray(b, UTM, 6, -5)
b.add_patch(Rectangle((core[0], core[2]), core[1] - core[0], core[3] - core[2], fill=False, ec="#252525", lw=0.6, ls="--", zorder=6))
utm_ticks(b, ext, [-112.0, -111.5, -111.0], [55.5, 56.0, 56.5, 57.0], fmt_lon="{:.1f}°W"); scalebar(b, 25, 0.08, 0.04); north(b, 0.85, 0.97)
# ---------------- component 1: regional context (left, top) + legend
lw_ = nx - 10.5 - 1.0; lh = lw_ * 0.98; ly = BOT + MAP_H - lh
a = axes_mm(1.0, ly, lw_, lh); a.set_facecolor(C_WATER)
countries.to_crs(LCC).plot(ax=a, color=C_LAND, edgecolor="#8c8c8c", lw=0.35, zorder=1)
pv = prov.to_crs(LCC); pv[pv.iso_a2 == "CA"].plot(ax=a, facecolor="none", edgecolor="#b0b0b0", lw=0.3, zorder=1.5)
pv[pv["name"] == "Alberta"].plot(ax=a, color=C_AB, edgecolor="#525252", lw=0.6, zorder=1.6)
gpd.GeoSeries([box(-112.3, 55.4, -110.6, 57.6)], crs=4326).to_crs(LCC).plot(ax=a, facecolor="none", edgecolor=C_BOX, lw=1.0, zorder=3)
for lo in (-130, -110, -90, -70):
    la = np.linspace(35, 85, 200); xs, ys = tl.transform(np.full_like(la, lo), la); a.plot(xs, ys, lw=0.3, c="#c8c8c8", zorder=1.7)
for la in (50, 60, 70):
    lo = np.linspace(-170, -40, 300); xs, ys = tl.transform(lo, np.full_like(lo, la)); a.plot(xs, ys, lw=0.3, c="#c8c8c8", zorder=1.7)
for la in (60,): a.text(*tl.transform(-129.0, la + 0.4), f"{la}°N", fontsize=5.6, color="#8c8c8c", ha="center", va="bottom", zorder=2)
for lo in (-110, -90): a.text(*tl.transform(lo + 0.6, 45.6), f"{abs(lo)}°W", fontsize=5.6, color="#8c8c8c", ha="left", va="bottom", zorder=2)
a.text(*tl.transform(-114.6, 52.2), "Alberta", fontsize=6.5, ha="center", color="#252525", zorder=4)
a.text(*tl.transform(-103, 63), "CANADA", fontsize=6.8, ha="center", color="#636363", zorder=4)
a.text(*tl.transform(-100, 44.3), "USA", fontsize=6.3, ha="center", color="#8c8c8c", zorder=4)
fort_mcmurray(a, LCC, 6, 3)
a.set_xlim(-2.1e6, 2.3e6); a.set_ylim(-0.6e6, -0.6e6 + 4.4e6 * lh / lw_); a.set_xticks([]); a.set_yticks([]); a.set_aspect("auto")
for ax_ in (a, b, c):
    for sp in ax_.spines.values(): sp.set_linewidth(0.6)
    ax_.set_xlabel(""); ax_.set_ylabel("")
H = [plt.Line2D([], [], marker="o", ls="", mfc=C_ST, mec="white", ms=5, label="Monitoring station"),
     plt.Line2D([], [], marker="s", ls="", mfc="white", mec=C_EX, ms=5, label="Excluded station\n(< 50% valid CH$_4$ hours, 2026)"),
     plt.Line2D([], [], c=C_PAIR, lw=1.0, label="Eligible station pair (n = 21)"),
     plt.Line2D([], [], marker="^", ls="", c="#525252", ms=4.5, label="Community"),
     plt.Line2D([], [], c=C_RIVER, lw=1.2, label="Athabasca River; lakes"),
     Rectangle((0, 0), 1, 1, fc="none", ec=C_BOX, lw=1.0, label="Study area"),
     Rectangle((0, 0), 1, 1, fc="none", ec="#252525", lw=0.6, ls="--", label="Extent of enlarged map")]
fig.legend(handles=H, loc="upper left", bbox_to_anchor=(1.0 / FIG_W, (ly - 3.0) / FIG_H), frameon=False, fontsize=6.5, handlelength=1.7,
           labelspacing=0.65, borderaxespad=0)
fig.text(1.0 / FIG_W, (BOT - 4.5) / FIG_H, "Base data: Natural Earth. Stations: WBEA (2024).\nProjections: Canada Atlas Lambert; UTM zone 12N.", fontsize=5.6, color="#5a5a5a", va="bottom")
import json
comp = {"map_components": 3, "regional_context": bool(a.collections), "network_map": {"stations": sorted(ch.get_gid()[8:] for ch in b.collections if (ch.get_gid() or "").startswith("station:")),
        "pair_lines": sum(1 for ln in b.lines if ln.get_color() == C_PAIR)}, "cluster_map": {"stations": sorted(ch.get_gid()[8:] for ch in c.collections if (ch.get_gid() or "").startswith("station:")), "pair_lines": sum(1 for ln in c.lines if ln.get_color() == C_PAIR),
        "labelled_stations": sorted(t.get_text() for t in c.texts if t.get_text().startswith("AMS"))}, "network_labelled": sorted(t.get_text() for t in b.texts if t.get_text().startswith("AMS")),
        "panel_letters": [t.get_text() for ax_ in (a, b, c) for t in ax_.texts if t.get_text().strip() in ("(a)", "(b)", "(c)")]}
(DATA / "fig01_components.json").write_text(json.dumps(comp, indent=1))
save_exact(fig, "fig01_wbea_network")
print(f"fig01 rev3 canvas {FIG_W} x {FIG_H} mm; regional {lw_:.1f} x {lh:.1f}; network {nw:.1f} x {MAP_H:.1f}; cluster {cw:.1f} x {MAP_H:.1f} mm; pairs drawn per map: {len(pairs)}")
