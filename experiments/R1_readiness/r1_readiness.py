"""R1 research-readiness checks on the development panel only (no confirmation-period values).
Outputs CSVs to results/R1/."""
import glob, itertools, numpy as np, pandas as pd, netCDF4 as nc

R = '/mnt/user-data/outputs/wbea_repo'
OUT = f'{R}/results/R1'
CUT = pd.Timestamp('2025-12-02 00:00')
coords = pd.read_csv('/mnt/user-data/uploads/WBEA_12_station_official_2024_coordinates.csv').set_index('station_id')
P = {pd.read_parquet(f).station.iloc[0]: pd.read_parquet(f).set_index('time_mst_hour_ending')
     for f in glob.glob(f'{R}/data/dev/*.parquet')}
ST = sorted(P, key=lambda s: int(s.split()[1]))
assert all(P[s].index.max() == CUT for s in ST)

# ---------------- 1. variables, heights, completeness, tokens
meta, comp, tok = [], [], []
for s in ST:
    d = P[s]
    vars_ = [c for c in d.columns if not c.endswith('__token') and c != 'station']
    wind = sorted({c.split(' ')[0][2:] or 'unstated' for c in vars_ if c.startswith('WS') and 'STD' not in c})
    meta.append(dict(station=s, name=coords.loc[s, 'station_name'], lat=coords.loc[s, 'latitude_deg_n'],
                     lon=coords.loc[s, 'longitude_deg_e'], wind_heights_m=';'.join(wind),
                     temp_levels=';'.join(sorted(c.split(' ')[0] for c in vars_ if c.startswith('AT'))),
                     has_NMHC='NMHC (ppm)' in vars_, has_PM25='PM2.5 (ug/m3)' in vars_,
                     has_WD_STD=any(c.startswith('WD') and 'STD' in c for c in vars_), n_variables=len(vars_)))
    ch = d['CH4 (ppm)']; t = d['CH4 (ppm)__token']
    row = dict(station=s)
    for y in range(2021, 2026):
        m = ch.index.year == y
        row[str(y)] = round(100 * ch[m].notna().mean(), 1)
    row['valid_hours'] = int(ch.notna().sum()); row['overall_pct'] = round(100 * ch.notna().mean(), 1)
    comp.append(row)
    vc = t[t != ''].value_counts()
    for k, v in vc.items():
        hrs = t.index[t == k].hour
        tok.append(dict(station=s, token=k, hours=int(v), share_pct=round(100 * v / len(t), 2),
                        modal_hours=';'.join(str(h) for h in pd.Series(hrs).value_counts().index[:3]),
                        share_in_01_06=round(float(np.isin(hrs, range(1, 7)).mean()), 2)))
pd.DataFrame(meta).to_csv(f'{OUT}/station_metadata_from_exports.csv', index=False)
pd.DataFrame(comp).to_csv(f'{OUT}/ch4_completeness_station_year.csv', index=False)
pd.DataFrame(tok).to_csv(f'{OUT}/ch4_token_counts.csv', index=False)

# ---------------- 2. consistency with the earlier 8-station pipeline
try:
    old = pd.read_pickle('/home/claude/a/raw.pkl')
    cons = []
    for s in [x for x in ST if x in old]:
        a = old[s]['CH4 (ppm)']; b = P[s]['CH4 (ppm)']
        j = pd.concat([a, b], axis=1, keys=['old', 'new'])
        cons.append(dict(station=s, both_valid=int(j.dropna().shape[0]),
                         max_abs_diff=float((j.old - j.new).abs().max()),
                         validity_mismatch=int((j.old.isna() != j.new.isna()).sum())))
    pd.DataFrame(cons).to_csv(f'{OUT}/consistency_with_earlier_exports.csv', index=False)
except FileNotFoundError:
    pass

# ---------------- 3. geometry and frozen-rule H2 pair family (all pairs <= 30 km)
def hav(a, b):
    la1, lo1, la2, lo2 = map(np.deg2rad, (*a, *b))
    return 6371.0088 * 2 * np.arcsin(np.sqrt(np.sin((la2 - la1) / 2) ** 2 +
                                             np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2))
def bearing(a, b):
    la1, lo1, la2, lo2 = map(np.deg2rad, (*a, *b)); dl = lo2 - lo1
    return (np.rad2deg(np.arctan2(np.sin(dl) * np.cos(la2),
                                  np.cos(la1) * np.sin(la2) - np.sin(la1) * np.cos(la2) * np.cos(dl))) + 360) % 360
xy = {s: (coords.loc[s, 'latitude_deg_n'], coords.loc[s, 'longitude_deg_e']) for s in ST}
geo = []
for a, b in itertools.combinations(ST, 2):
    geo.append(dict(station_i=a, station_j=b, distance_km=round(hav(xy[a], xy[b]), 3),
                    bearing_i_to_j_deg=round(bearing(xy[a], xy[b]), 1),
                    min_U_for_tau_le_3h_ms=round(hav(xy[a], xy[b]) / (3.6 * 3), 2),
                    in_H2_family=hav(xy[a], xy[b]) <= 30.0))
geo = pd.DataFrame(geo); geo.to_csv(f'{OUT}/pairwise_geometry_66_pairs.csv', index=False)

# ---------------- 4. H2 eligibility per family pair (|U_par| >= 1 m/s, within 45 deg, tau <= 3 h, Kmin 4 others)
def wind(s):
    """Composite station wind (decision D-03): 10 m where valid, else 20 m; AMS 5 uses 20 m.
    Returns u, v (toward-components, m/s), a label, and the height used each hour."""
    d = P[s]
    def get(h):
        ws, wd = f'WS{h} (km/h)', f'WD{h} (deg)'
        return (d[ws] / 3.6, d[wd]) if ws in d and wd in d else (None, None)
    ws10, wd10 = get(10); ws20, wd20 = get(20)
    if ws10 is None:
        ws, wd, h = ws20, wd20, pd.Series(20.0, index=d.index); lab = 'WS20'
    else:
        use10 = ws10.notna() & wd10.notna()
        ws = ws10.where(use10, ws20 if ws20 is not None else None)
        wd = wd10.where(use10, wd20 if wd20 is not None else None)
        h = pd.Series(10.0, index=d.index).where(use10, 20.0 if ws20 is not None else float('nan'))
        lab = 'WS10' + ('+WS20 fill' if ws20 is not None else '')
    h = h.where(ws.notna() & wd.notna())
    return -ws * np.sin(np.deg2rad(wd)), -ws * np.cos(np.deg2rad(wd)), lab, h
UV = {s: wind(s) for s in ST}
CH = pd.DataFrame({s: P[s]['CH4 (ppm)'] for s in ST})
el = []
for _, r in geo[geo.in_H2_family].iterrows():
    a, b = r.station_i, r.station_j; phi = np.deg2rad(r.bearing_i_to_j_deg)
    u = (UV[a][0] + UV[b][0]) / 2; v = (UV[a][1] + UV[b][1]) / 2
    upar = u * np.sin(phi) + v * np.cos(phi); sp = np.hypot(u, v); tau = r.distance_km / (3.6 * upar.abs())
    ok = CH[a].diff().notna() & CH[b].diff().notna() & CH.drop(columns=[a, b]).notna().sum(1).ge(4)
    e = ok & (upar.abs() >= 0.707 * sp) & (upar.abs() >= 1) & (tau <= 3)
    el.append(dict(pair=f'{a}-{b}', distance_km=r.distance_km, wind_used=f'{UV[a][2]} / {UV[b][2]}', share_any_20m=round(float(((UV[a][3]==20)|(UV[b][3]==20))[e].mean()),2),
                   aligned_h=int((e & (upar > 0)).sum()), reversed_h=int((e & (upar < 0)).sum()),
                   median_tau_h=round(float(tau[e].median()), 2),
                   share_tau_lt_0_5=round(float((tau[e] < 0.5).mean()), 2)))
pd.DataFrame(el).to_csv(f'{OUT}/h2_family_eligibility.csv', index=False)

# ---------------- 5. ERA5 cell mapping and hour-convention test (development period)
ds = nc.Dataset(glob.glob('/home/claude/raw_ext/era5c/*.nc')[0])
lat = np.array(ds['latitude'][:]); lon = np.array(ds['longitude'][:])
tt = pd.to_datetime(np.array(ds['valid_time'][:]), unit='s'); dev = tt <= CUT + pd.Timedelta(hours=8)
T2 = np.array(ds['t2m'][:])[dev] - 273.15
def dsn(x): return x - x.rolling(24 * 15, center=True, min_periods=100).mean()
cells = []
for s in ST:
    i = int(np.argmin(abs(lat - xy[s][0]))); j = int(np.argmin(abs(lon - xy[s][1])))
    e = pd.Series(T2[:, i, j], index=tt[dev])
    stn = P[s]['AT2 (C)'] if 'AT2 (C)' in P[s] else None
    r_end = r_beg = np.nan
    if stn is not None:
        st_utc = stn.copy(); st_utc.index = st_utc.index + pd.Timedelta(hours=7)
        r_end = pd.concat([dsn((e + e.shift(1)) / 2), dsn(st_utc)], axis=1, sort=True).dropna().corr().iloc[0, 1]
        r_beg = pd.concat([dsn((e + e.shift(-1)) / 2), dsn(st_utc)], axis=1, sort=True).dropna().corr().iloc[0, 1]
    cells.append(dict(station=s, era5_cell_lat=lat[i], era5_cell_lon=lon[j],
                      cell_offset_km=round(hav(xy[s], (lat[i], lon[j])), 1),
                      r_hour_ending=round(r_end, 4), r_hour_beginning=round(r_beg, 4)))
cells = pd.DataFrame(cells)
cells['cell_shared_with'] = cells.apply(lambda r: ';'.join(cells[(cells.era5_cell_lat == r.era5_cell_lat) &
                                        (cells.era5_cell_lon == r.era5_cell_lon) & (cells.station != r.station)].station), axis=1)
cells.to_csv(f'{OUT}/era5_cells_and_timestamp_test.csv', index=False)
wc = pd.DataFrame({s: UV[s][3].notna().groupby(UV[s][3].index.year).mean().round(3) for s in ST}).T
wc.to_csv(f'{OUT}/composite_wind_coverage_station_year.csv')
hz = pd.DataFrame({s: (UV[s][3] == 20).groupby(UV[s][3].index.year).mean().round(3) for s in ST}).T
hz.to_csv(f'{OUT}/composite_wind_share_20m_station_year.csv')
print('done')
