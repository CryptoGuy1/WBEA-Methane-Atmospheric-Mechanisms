"""Prepare descriptive inputs: station table, frozen pair list, Natural Earth clips, and DAILY CH4 availability computed
from actual hourly validity indicators (numeric CH4 present = valid; codes Z, C, '.' and blanks = not valid)."""
import json, pathlib, numpy as np, pandas as pd, geopandas as gpd
from shapely.geometry import box
from common import ROOT, DATA, GIS, STUDY, PAIRS_CSV
from wbea.io import load_dev
from wbea.geometry import stations, haversine_km
RAW_GIS = pathlib.Path("/home/claude/gis")             # Natural Earth geojson downloaded from github.com/nvkelso/natural-earth-vector
meta = pd.read_csv(ROOT / "metadata/stations_official_2024.csv").set_index("station_id").loc[STUDY]
meta[["station_name", "latitude_deg_n", "longitude_deg_e", "metadata_year", "source_url"]].to_csv(DATA / "stations_study.csv")
pairs = pd.read_csv(PAIRS_CSV)[["pair"]]; pairs[["i", "j"]] = pairs.pair.str.split("->", expand=True)
xy = stations(); pairs["km"] = [haversine_km(xy[a], xy[b]) for a, b in zip(pairs.i, pairs.j)]; pairs.to_csv(DATA / "pairs_frozen.csv", index=False)
# Natural Earth clips (public domain), kept small
wide = box(-142, 41, -52, 75); local = box(-113.5, 54.8, -109.5, 59.2)
for name, clip in (("ne_50m_admin_0_countries", wide), ("ne_50m_admin_1_states_provinces", wide), ("ne_10m_lakes", local),
                   ("ne_10m_rivers_lake_centerlines", local), ("ne_10m_admin_1_states_provinces_lines", local)):
    g = gpd.read_file(RAW_GIS / f"{name}.geojson"); g = g[g.intersects(clip)].copy(); g["geometry"] = g.geometry.intersection(clip)
    g.columns = [c.lower() if c != "geometry" else c for c in g.columns]; g = g.set_geometry("geometry")
    keep = [c for c in ("name", "admin", "iso_a2", "featurecla") if c in g.columns]; g[keep + ["geometry"]].to_file(GIS / f"{name}_clip.geojson", driver="GeoJSON")
pp = gpd.read_file(RAW_GIS / "ne_10m_populated_places_simple.geojson"); pp = pp[pp["name"].isin(["Fort McMurray", "Fort Chipewyan", "Edmonton", "Calgary"])]
pp[["name", "latitude", "longitude", "geometry"]].to_file(GIS / "ne_10m_populated_places_selected.geojson", driver="GeoJSON")

def daily(panel, start, end):
    idx = pd.date_range(start, end, freq="h"); day = (idx - pd.Timedelta(minutes=1)).normalize()    # hour-ending: 00:00 belongs to previous day
    rows = []
    for s in STUDY:
        d = panel[s].reindex(idx); v = d["CH4 (ppm)"].notna(); tok = d["CH4 (ppm)__token"].fillna("")
        g = pd.DataFrame({"day": day, "valid": v.values, "Z": (tok == "Z").values, "C": (tok == "C").values,
                          "dot": (tok == ".").values, "other_missing": (~v & ~tok.isin(["Z", "C", "."])).values})
        a = g.groupby("day").agg(hours=("valid", "size"), valid_hours=("valid", "sum"), Z=("Z", "sum"), C=("C", "sum"), dot=("dot", "sum"), other_missing=("other_missing", "sum"))
        a.insert(0, "station", s); rows.append(a.reset_index())
    out = pd.concat(rows); out["valid_fraction"] = out.valid_hours / out.hours; return out
conf = {d.station.iloc[0]: d.set_index("time_mst_hour_ending") for d in (pd.read_parquet(f) for f in (ROOT / "sealed/e08_panel").glob("AMS*.parquet"))}
d26 = daily(conf, "2026-01-01 01:00", "2026-10-01 00:00"); d26.to_csv(DATA / "ch4_daily_availability_2026_jan_sep.csv", index=False)
dev = load_dev(STUDY); ddev = daily(dev, "2021-01-01 01:00", "2025-12-02 00:00"); ddev.to_csv(DATA / "ch4_daily_availability_2021_2025.csv", index=False)
cov = d26.groupby("station").agg(valid_hours=("valid_hours", "sum"), hours=("hours", "sum")); cov["recomputed"] = cov.valid_hours / cov.hours
frozen = json.loads((ROOT / "experiments/E08_confirmation/confirmation_2026/e08_results.json").read_text())["log"]["station_coverage"]
cov["frozen_e08"] = [frozen[s] for s in cov.index]; cov["abs_diff"] = (cov.recomputed - cov.frozen_e08).abs()
cov.round(6).to_csv(DATA / "ch4_station_coverage_2026_check.csv")
cdev = ddev.groupby("station").agg(valid_hours=("valid_hours", "sum"), hours=("hours", "sum")); cdev["valid_fraction"] = cdev.valid_hours / cdev.hours
cdev.round(6).to_csv(DATA / "ch4_station_coverage_2021_2025.csv")
print(cov.round(4).to_string()); print(len(d26.day.unique()), "days 2026;", len(ddev.day.unique()), "days 2021-2025;", "hours per day:", sorted(set(d26.hours)), sorted(set(ddev.hours)))
