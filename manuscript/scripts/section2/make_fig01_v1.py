"""Fig. 1: regional location and network configuration. Natural Earth (public domain) boundaries; WBEA official 2024
station coordinates; the 21 eligible pairs read from the frozen E08 output. Panels (a) EPSG:3978, (b, c) EPSG:32612."""
import numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import box, LineString, Point
from pyproj import Transformer
from matplotlib.patches import Rectangle
from common import plt, MM, DATA, GIS, STUDY, EXCLUDED, save
import common; common.FIG = common.FIG / "archive_v1"; save.__globals__["FIG"] = common.FIG   # v1 outputs go to archive_v1
LCC, UTM = "EPSG:3978", "EPSG:32612"
st = pd.read_csv(DATA / "stations_study.csv").set_index("station_id"); pairs = pd.read_csv(DATA / "pairs_frozen.csv")
g = lambda n: gpd.read_file(GIS / n)
countries, prov = g("ne_50m_admin_0_countries_clip.geojson"), g("ne_50m_admin_1_states_provinces_clip.geojson")
lakes, rivers, places = g("ne_10m_lakes_clip.geojson"), g("ne_10m_rivers_lake_centerlines_clip.geojson"), g("ne_10m_populated_places_selected.geojson")
pts = gpd.GeoDataFrame(st, geometry=[Point(lo, la) for la, lo in zip(st.latitude_deg_n, st.longitude_deg_e)], crs="EPSG:4326").to_crs(UTM)
P = {s: (p.x, p.y) for s, p in zip(pts.index, pts.geometry)}
C_LAND, C_AB, C_WATER, C_LINE, C_ST, C_EX, C_PAIR = "#f2f2f2", "#d9d9d9", "#c6dbef", "#7f7f7f", "#08519c", "#969696", "#9e9e9e"

def graticule(ax, crs, lons, lats, extent, lon_lbl=True, lat_lbl=True):
    tr = Transformer.from_crs("EPSG:4326", crs, always_xy=True); inv = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    x0, x1, y0, y1 = extent
    for lo in lons:
        la = np.linspace(-90 if crs == LCC else 50, 85 if crs == LCC else 62, 400); x, y = tr.transform(np.full_like(la, lo), la)
        ax.plot(x, y, lw=0.3, c="#bdbdbd", zorder=0.5)
    for la in lats:
        lo = np.linspace(-170 if crs == LCC else -116, -40 if crs == LCC else -106, 400); x, y = tr.transform(lo, np.full_like(lo, la))
        ax.plot(x, y, lw=0.3, c="#bdbdbd", zorder=0.5)
    xt, xl = [], []
    for lo in lons:                                  # where the meridian crosses the bottom edge
        lat_b = inv.transform((x0 + x1) / 2, y0)[1]; xb, _ = tr.transform(lo, lat_b)
        if x0 < xb < x1: xt.append(xb); xl.append(f"{abs(lo):g}°W")
    yt, yl = [], []
    for la in lats:
        lon_l = inv.transform(x0, (y0 + y1) / 2)[0]; _, yb = tr.transform(lon_l, la)
        if y0 < yb < y1: yt.append(yb); yl.append(f"{la:g}°N")
    ax.set_xticks(xt, xl if lon_lbl else [""] * len(xt)); ax.set_yticks(yt, yl if lat_lbl else [""] * len(yt))
    ax.tick_params(length=2, pad=1.5); ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal")

def scalebar(ax, km, xfrac=0.06, yfrac=0.05):
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim(); x = x0 + xfrac * (x1 - x0); y = y0 + yfrac * (y1 - y0)
    ax.plot([x, x + km * 1000], [y, y], c="k", lw=1.2, solid_capstyle="butt"); ax.text(x + km * 500, y + 0.012 * (y1 - y0), f"{km} km", ha="center", va="bottom", fontsize=6)

def north(ax, xfrac=0.92, yfrac=0.9):
    ax.annotate("N", xy=(xfrac, yfrac), xytext=(xfrac, yfrac - 0.08), xycoords="axes fraction", ha="center", va="center", fontsize=6.5,
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color="k", shrinkA=0, shrinkB=0))

def base_local(ax, extent):
    x0, x1, y0, y1 = extent; clip = gpd.GeoSeries([box(x0, y0, x1, y1)], crs=UTM).to_crs(4326).iloc[0].buffer(0.05)
    ax.set_facecolor(C_LAND)
    lk = lakes[lakes.intersects(clip)].to_crs(UTM); lk.plot(ax=ax, color=C_WATER, edgecolor="none", zorder=1)
    rv = rivers[rivers.intersects(clip)].to_crs(UTM); rv.plot(ax=ax, color="#6baed6", lw=0.7, zorder=1.2)
    return rv

def draw_network(ax, label_offsets, show_labels=True):
    for _, r in pairs.iterrows():
        (xa, ya), (xb, yb) = P[r.i], P[r.j]; ax.plot([xa, xb], [ya, yb], c=C_PAIR, lw=0.45, alpha=0.9, zorder=2, solid_capstyle="round")
    for s in STUDY:
        x, y = P[s]
        if s in EXCLUDED: ax.scatter(x, y, s=16, marker="s", facecolor="white", edgecolor=C_EX, lw=0.8, zorder=4)
        else: ax.scatter(x, y, s=14, marker="o", facecolor=C_ST, edgecolor="white", lw=0.4, zorder=4)
        if show_labels and s in label_offsets:
            dx, dy, ha = label_offsets[s]
            ax.annotate(s.replace("AMS ", "AMS "), (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=6,
                        color=C_EX if s in EXCLUDED else "k", zorder=5)

def place(ax, name, dx=4, dy=-4, ha="left"):
    p = places[places["name"] == name].to_crs(ax._crs).iloc[0].geometry
    ax.scatter(p.x, p.y, s=9, marker="^", c="#525252", zorder=3, lw=0)
    ax.annotate(name, (p.x, p.y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=6, style="italic", color="#525252")

fig = plt.figure(figsize=(180 * MM, 112 * MM))
gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 0.62, 1.0], wspace=0.12)
# ---------------- (a) regional
a = fig.add_subplot(gs[0]); a._crs = LCC
cty = countries.to_crs(LCC); pv = prov.to_crs(LCC)
a.set_facecolor(C_WATER); cty.plot(ax=a, color=C_LAND, edgecolor=C_LINE, lw=0.4, zorder=1)
pv[pv.iso_a2 == "CA"].plot(ax=a, facecolor="none", edgecolor="#a6a6a6", lw=0.3, zorder=1.5)
pv[pv["name"] == "Alberta"].plot(ax=a, color=C_AB, edgecolor="#525252", lw=0.6, zorder=1.6)
sa = gpd.GeoSeries([box(-112.3, 55.4, -110.6, 57.6)], crs=4326).to_crs(LCC); sa.plot(ax=a, facecolor="none", edgecolor="#b2182b", lw=0.9, zorder=3)
ab = pv[pv["name"] == "Alberta"].geometry.iloc[0].representative_point(); a.text(ab.x - 2.2e5, ab.y - 2.5e5, "Alberta", fontsize=6.5, ha="center", color="#252525")
trl = Transformer.from_crs("EPSG:4326", LCC, always_xy=True)
a.text(*trl.transform(-98, 62), "CANADA", fontsize=7, ha="center", color="#636363")
graticule(a, LCC, [-130, -110, -90, -70], [50, 60, 70], (-2.45e6, 3.0e6, -0.85e6, 3.9e6)); a.set_xticks([]); a.set_yticks([])
for la in (50, 60): a.text(*trl.transform(-121, la), f"{la}°N", fontsize=5.5, color="#969696", ha="center", va="bottom")
for lo in (-110, -90): a.text(*trl.transform(lo, 45.2), f"{abs(lo)}°W", fontsize=5.5, color="#969696", ha="left", va="bottom")
place(a, "Fort McMurray", dx=7, dy=2)
a.text(0.02, 0.98, "(a)", transform=a.transAxes, fontsize=8, fontweight="bold", va="top")
# ---------------- (b) full network
ext_b = (P["AMS 18"][0] - 52e3, P["AMS 18"][0] + 52e3, P["AMS 18"][1] - 18e3, P["AMS 23"][1] + 20e3)
b = fig.add_subplot(gs[1]); b._crs = UTM; base_local(b, ext_b)
draw_network(b, {"AMS 14": (5, 0, "left"), "AMS 18": (5, 0, "left")})
place(b, "Fort McMurray", dx=6, dy=-5, ha="left")
core = (P["AMS 30"][0] - 6e3, P["AMS 7"][0] + 9e3, P["AMS 7"][1] - 7e3, P["AMS 23"][1] + 6e3)
b.add_patch(Rectangle((core[0], core[2]), core[1] - core[0], core[3] - core[2], fill=False, ec="#252525", lw=0.6, ls="--", zorder=6))
b.text(core[1] + 1.5e3, core[3], "(c)", fontsize=6.5, va="top")
graticule(b, UTM, [-112, -111], [55.5, 56, 56.5, 57, 57.5], ext_b); scalebar(b, 25); north(b)
b.text(0.04, 0.98, "(b)", transform=b.transAxes, fontsize=8, fontweight="bold", va="top")
# ---------------- (c) core
c = fig.add_subplot(gs[2]); c._crs = UTM; base_local(c, core)
offs = {"AMS 23": (5, 0, "left"), "AMS 30": (0, 7, "center"), "AMS 9": (5, 2, "left"), "AMS 1": (-5, 2, "right"), "AMS 13": (-5, -2, "right"),
        "AMS 2": (-5, 0, "right"), "AMS 11": (5, 2, "left"), "AMS 5": (5, -2, "left"), "AMS 6": (-5, 0, "right"), "AMS 7": (5, 0, "left")}
draw_network(c, offs); place(c, "Fort McMurray", dx=2, dy=-8, ha="center")
graticule(c, UTM, [-111.8, -111.6, -111.4, -111.2], [56.8, 57.0, 57.2, 57.4], core, lat_lbl=True); scalebar(c, 10, xfrac=0.06, yfrac=0.05)
c.text(0.02, 0.98, "(c)", transform=c.transAxes, fontsize=8, fontweight="bold", va="top")
h = [plt.Line2D([], [], marker="o", ls="", mfc=C_ST, mec="white", ms=4.5, label="Monitoring station"),
     plt.Line2D([], [], marker="s", ls="", mfc="white", mec=C_EX, ms=4.5, label="Station excluded (CH$_4$ completeness < 50%)"),
     plt.Line2D([], [], c=C_PAIR, lw=0.8, label="Eligible station pair (n = 21; statistical, not a transport path)"),
     plt.Line2D([], [], marker="^", ls="", c="#525252", ms=4, label="Community (Natural Earth)"),
     plt.Line2D([], [], c="#6baed6", lw=1, label="Athabasca River"), Rectangle((0, 0), 1, 1, fc="none", ec="#b2182b", lw=0.9, label="Study-area extent")]
fig.legend(handles=h, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.02), fontsize=6.2, handlelength=1.6, columnspacing=1.2)
for ax_ in (a, b, c): ax_.set_xlabel(""); ax_.set_ylabel("")
save(fig, "fig01_wbea_network")
print("fig01 written; pairs drawn:", len(pairs))
