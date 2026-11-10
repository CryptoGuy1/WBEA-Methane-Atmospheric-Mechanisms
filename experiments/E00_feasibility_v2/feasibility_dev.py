"""Feasibility checks for WBEA v2.0. Uses ONLY 2021-01-01..2025-12-02 exports (raw.pkl built from
the eight five-year files). The AMS 2 CH4-only file containing 2026 values is never loaded."""
import time, numpy as np, pandas as pd
rng = np.random.default_rng(7)
S8 = ['AMS 1','AMS 2','AMS 5','AMS 6','AMS 7','AMS 11','AMS 13','AMS 23']
CO = {'AMS 1':(57.1894,-111.6406),'AMS 2':(57.0500,-111.5641),'AMS 5':(56.9680,-111.4821),'AMS 6':(56.7514,-111.4767),
      'AMS 7':(56.7334,-111.3905),'AMS 11':(57.0325,-111.5064),'AMS 13':(57.1492,-111.6423),'AMS 23':(57.3489,-111.63969)}

# ------------------------------------------------ 1. LOO vs LPO residualization under NO transport
def sim_resid_bias(n=20000, seeds=40):
    out = {'raw': [], 'LOO': [], 'LPO': []}
    for s in range(seeds):
        r = np.random.default_rng(s)
        F = np.zeros(n); e = np.zeros((8, n))
        for t in range(1, n):
            F[t] = .97 * F[t-1] + r.normal()
            e[:, t] = .9 * e[:, t-1] + r.normal(size=8)
        wd = (np.cumsum(r.normal(0, 15, n)) % 360)                # wandering wind direction (deg from)
        plume_i = np.exp(2 * np.cos(np.deg2rad(wd - 200)))        # station 0 sees a local plume for SSW winds
        X = F + e * 0.5; X[0] += 0.5 * e[0] * plume_i             # no inter-station transport at all
        aligned = np.cos(np.deg2rad(wd - 180 - 0)) > .707          # pair 0->1 bearing 0 deg: aligned = wind from S
        revers = np.cos(np.deg2rad(wd - 180 - 0)) < -.707
        med_loo = lambda k: np.median(np.delete(X, k, 0), 0)
        med_lpo = np.median(np.delete(X, [0, 1], 0), 0)
        R = {'raw': (X[0], X[1]), 'LOO': (X[0] - med_loo(0), X[1] - med_loo(1)), 'LPO': (X[0] - med_lpo, X[1] - med_lpo)}
        for k, (a, b) in R.items():
            da, db = np.diff(a), np.diff(b); al, rv = aligned[1:], revers[1:]
            def asym(m):
                idx = np.where(m[1:])[0] + 1
                return np.corrcoef(da[idx-1], db[idx])[0,1] - np.corrcoef(db[idx-1], da[idx])[0,1]
            out[k].append(asym(al) - asym(rv))
    return {k: (np.mean(v), np.std(v) / np.sqrt(len(v))) for k, v in out.items()}

# ------------------------------------------------ development-data checks
def dev_checks():
    d = pd.read_pickle('/home/claude/a/raw.pkl'); d = {k: v for k, v in d.items() if k in S8}
    assert max(v.index.max() for v in d.values()) <= pd.Timestamp('2025-12-02 00:00')
    ch = pd.DataFrame({s: d[s]['CH4 (ppm)'] for s in S8})
    res = {}
    # background B_t: daily p10 of network values 12-17h, broadcast to the whole day
    aft = ch[ch.index.hour.isin(range(12, 18))]
    B = aft.stack().groupby(aft.stack().index.get_level_values(0).normalize()).quantile(.10)
    Bt = B.reindex(ch.index.normalize()).values
    E = ch.sub(Bt, axis=0)
    res['share_E_negative'] = float((E < 0).sum().sum() / E.notna().sum().sum())
    res['share_days_without_B'] = float(pd.isna(Bt).mean())
    # H1 design
    a5 = d['AMS 5']; S = a5['AT90 (C)'] - a5['AT20 (C)']; U5 = a5['WS20 (km/h)'] / 3.6
    tr = S.loc['2021':'2023']; Sz = (S - tr.mean()) / tr.std()
    oth = [s for s in S8 if s != 'AMS 5']
    M = E[oth].median(axis=1).where(E[oth].notna().sum(1) >= 5)
    Mx = (ch[oth].median(axis=1)).where(ch[oth].notna().sum(1) >= 5)   # same, without subtracting B_t
    df = pd.DataFrame({'M': M, 'Mx': Mx, 'S': Sz, 'lu': np.log(U5 + 0.5)}).dropna()
    df['g'] = df.index.year * 10000 + df.index.month * 100 + df.index.hour
    df['blk'] = (df.index - df.index[0]).days // 14
    res['H1_n'] = len(df); res['H1_cells'] = df.g.nunique(); res['H1_blocks'] = df.blk.nunique()
    res['H1_hours_lost_to_S_or_Kmin'] = int(ch.index.size - len(df))
    def demean(x): return x - x.groupby(df.g).transform('mean')
    Z = df[['M', 'Mx', 'S', 'lu']].apply(demean)
    def beta(Zs, y, xs):
        X = Zs[xs].values; return np.linalg.lstsq(X, Zs[y].values, rcond=None)[0][0]
    res['H1_beta_with_B'] = beta(Z, 'M', ['S', 'lu']); res['H1_beta_without_B'] = beta(Z, 'Mx', ['S', 'lu'])
    res['H1_beta_total_with_B'] = beta(Z, 'M', ['S'])
    res['corr_daily_B_vs_dailymean_S'] = float(pd.concat([B, Sz.groupby(Sz.index.normalize()).mean()], axis=1).dropna().corr().iloc[0, 1])
    # moving-block bootstrap timing (14-day blocks, cells re-demeaned within each replicate)
    blocks = [g.index for _, g in df.groupby('blk')]; t0 = time.time(); bs = []
    for _ in range(50):
        idx = np.concatenate([blocks[k] for k in rng.integers(0, len(blocks), len(blocks))])
        sub = df.loc[idx]; zz = sub[['M', 'S', 'lu']] - sub.groupby('g')[['M', 'S', 'lu']].transform('mean')
        bs.append(np.linalg.lstsq(zz[['S', 'lu']].values, zz.M.values, rcond=None)[0][0])
    res['bootstrap_sec_per_2000'] = (time.time() - t0) / 50 * 2000
    res['H1_beta_with_B_bootSE_50reps'] = float(np.std(bs))
    # H2 eligibility (aligned AND reversed, |U_par| >= 1 m/s, tau <= 3 h, within 45 deg)
    def brg(a, b):
        la1, lo1 = np.deg2rad(a); la2, lo2 = np.deg2rad(b); dl = lo2 - lo1
        return (np.rad2deg(np.arctan2(np.sin(dl)*np.cos(la2), np.cos(la1)*np.sin(la2)-np.sin(la1)*np.cos(la2)*np.cos(dl))) + 360) % 360
    def dist(a, b):
        la1, lo1 = np.deg2rad(a); la2, lo2 = np.deg2rad(b)
        return 6371*2*np.arcsin(np.sqrt(np.sin((la2-la1)/2)**2+np.cos(la1)*np.cos(la2)*np.sin((lo2-lo1)/2)**2))
    UV = {}
    for s in S8:
        x = d[s]; ws = (x['WS10 (km/h)'] if 'WS10 (km/h)' in x else x['WS20 (km/h)']) / 3.6
        wd = x['WD10 (deg)'] if 'WD10 (deg)' in x else x['WD20 (deg)']
        UV[s] = (-ws*np.sin(np.deg2rad(wd)), -ws*np.cos(np.deg2rad(wd)))
    rows = []
    for i, a in enumerate(S8):
        for b in S8[i+1:]:
            dd = dist(CO[a], CO[b])
            if dd > 30: continue
            phi = brg(CO[a], CO[b]); u = (UV[a][0]+UV[b][0])/2; v = (UV[a][1]+UV[b][1])/2
            # u,v are toward-components; along-path toward j = u sin(phi) + v cos(phi)
            upar = u*np.sin(np.deg2rad(phi)) + v*np.cos(np.deg2rad(phi)); sp = np.hypot(u, v)
            ang_ok = np.abs(upar) >= 0.707 * sp
            tau = dd / (3.6 * np.abs(upar))
            valid = ch[a].diff().notna() & ch[b].diff().notna() & ch.drop(columns=[a, b]).notna().sum(1).ge(4)
            el = valid & ang_ok & (np.abs(upar) >= 1) & (tau <= 3)
            rows.append(dict(pair=f'{a}-{b}', km=round(dd, 1), aligned_h=int((el & (upar > 0)).sum()),
                             reversed_h=int((el & (upar < 0)).sum()),
                             median_tau_h=round(float(tau[el].median()), 2) if el.any() else np.nan,
                             share_tau_lt_0_5=round(float((tau[el] < .5).mean()), 2) if el.any() else np.nan))
    elig = pd.DataFrame(rows)
    # placebo coincidence: correlation of true vs shifted pair-mean wind vector (AMS 1-13)
    u = (UV['AMS 1'][0]+UV['AMS 13'][0])/2; v = (UV['AMS 1'][1]+UV['AMS 13'][1])/2
    pc = {}
    for h in [14*24, 21*24, 28*24, 56*24, 365*24, 730*24]:
        us, vs = np.roll(u.values, h), np.roll(v.values, h); m = ~np.isnan(u.values) & ~np.isnan(us)
        pc[f'{h//24}d'] = round(float(np.corrcoef(np.r_[u.values[m], v.values[m]], np.r_[us[m], vs[m]])[0, 1]), 3)
    # H3 regime occupancy with FIXED 2021-2023 tercile cuts
    cuts = Sz.loc['2021':'2023'].quantile([1/3, 2/3]).values
    reg = pd.DataFrame({'st': np.digitize(Sz, cuts), 'ws': np.digitize(U5, [1, 2.5]),
                        'day': ((Sz.index.hour >= 8) & (Sz.index.hour < 20)).astype(int)}, index=Sz.index)
    reg['r'] = reg.st*6 + reg.ws*2 + reg.day; reg.loc[Sz.isna() | U5.isna(), 'r'] = np.nan
    occ = []
    kit = []
    for s in S8:
        thr = ch[s].loc['2021':'2023'].quantile(.95)
        z = pd.DataFrame({'y': (ch[s] > thr).astype(float).where(ch[s].notna()), 'r': reg.r}).dropna()
        z['yr'] = z.index.year
        z = z[z.yr <= 2024]                       # 2025 is incomplete (ends 2 Dec)
        tab = z.groupby(['yr', 'r']).y.agg(['size', 'mean'])
        occ.append(dict(station=s, min_cell_h=int(tab['size'].min()), cells_lt50=int((tab['size'] < 50).sum()),
                        cells_total=len(tab), cells_missing=int(4*18 - len(tab))))
        for ya, yb in [(2021, 2022), (2022, 2023), (2023, 2024)]:
            A = tab.loc[ya]; Bq = tab.loc[yb]; idx = A.index.union(Bq.index)
            pa = (A['size'] / A['size'].sum()).reindex(idx, fill_value=0); pb = (Bq['size'] / Bq['size'].sum()).reindex(idx, fill_value=0)
            qa = A['mean'].reindex(idx); qb = Bq['mean'].reindex(idx); qa = qa.fillna(qb); qb = qb.fillna(qa)
            comp = float(((pa - pb) * (qa + qb) / 2).sum()); within = float(((pa + pb) * (qa - qb) / 2).sum())
            kit.append(dict(station=s, contrast=f'{ya}-{yb}', diff_pp=round(100*(comp+within), 2),
                            composition_pp=round(100*comp, 2), within_pp=round(100*within, 2)))
    return res, elig, pc, pd.DataFrame(occ), pd.DataFrame(kit)

if __name__ == '__main__':
    print('Residualization bias under no transport (mean D, SE over 40 seeds):', sim_resid_bias())
    res, elig, pc, occ, kit = dev_checks()
    for k, v in res.items(): print(f'{k}: {v}')
    print(elig.to_string(index=False)); print('placebo wind-vector correlation by shift:', pc)
    print(occ.to_string(index=False)); print(kit.to_string(index=False))
    elig.to_csv('h2_eligibility_dev.csv', index=False); kit.to_csv('h3_kitagawa_dev_exploratory.csv', index=False)
    occ.to_csv('h3_cell_occupancy_dev.csv', index=False)
