"""E08 runner (PROTOCOL_E08_DRAFT_v2). Modes:
  dryrun  : panel = splitter output for 2025-01-01 01:00..2025-10-01 00:00 (development data); H3 contrasts 2025 vs 2021-2024
  confirm : panel = sealed 2026 splitter output (NOT authorised yet);                          H3 contrasts 2026 vs 2021-2025
All reference quantities come from the 2021-2023 development panel. Methods are identical in both modes.
Usage: python run_e08.py --mode dryrun --panel <dir> --out <dir>"""
import argparse, json, pathlib, sys, time, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "src"))
from wbea.config import CFG
from wbea.io import load_dev
from wbea.wind import composite
from wbea.geometry import pair_table
from wbea.solar import elevation_deg
from wbea import h2, e08, runmeta

ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["dryrun", "confirm"], required=True)
ap.add_argument("--panel", required=True); ap.add_argument("--out", required=True); ap.add_argument("--nboot_h1", type=int, default=2000)
ap.add_argument("--nboot_h3", type=int, default=1000); ap.add_argument("--nboot_centroid", type=int, default=1000)
A = ap.parse_args(); OUT = pathlib.Path(A.out); OUT.mkdir(parents=True, exist_ok=True); T0 = time.time()
SEED = 20261190; WIN = {"dryrun": ("2025-01-01 01:00", "2025-10-01 00:00", 2025, [2021, 2022, 2023, 2024]),
                        "confirm": ("2026-01-01 01:00", "2026-10-01 00:00", 2026, [2021, 2022, 2023, 2024, 2025])}[A.mode]
START, END, CYEAR, DEVYEARS = pd.Timestamp(WIN[0]), pd.Timestamp(WIN[1]), WIN[2], WIN[3]
if A.mode == "confirm":
    raise SystemExit("confirm mode is not authorised before the protocol-freeze tag")
DEV = load_dev(); ST = CFG["stations"]["usable"]; CORE = CFG["stations"]["h1_core_response"]
REF = pd.DataFrame({s: DEV[s]["CH4 (ppm)"] for s in ST}).loc["2021":"2023"]
MED, P95 = REF.median(), REF.quantile(.95)
S_REF = (DEV["AMS 5"]["AT90 (C)"] - DEV["AMS 5"]["AT20 (C)"]).loc["2021":"2023"]; S_MU, S_SD = S_REF.mean(), S_REF.std()
CUTS = S_REF.quantile([1 / 3, 2 / 3]).values
PAN = {f.stem: pd.read_parquet(f).set_index("time_mst_hour_ending") for f in pathlib.Path(A.panel).glob("AMS*.parquet")}
PAN = {d.station.iloc[0]: d for d in PAN.values()}
idx = pd.date_range(START, END, freq="h"); assert all(PAN[s].index.min() >= START and PAN[s].index.max() <= END for s in PAN)
P = {s: PAN[s].reindex(idx) for s in ST}
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST})
log = {"mode": A.mode, "window": [str(START), str(END)], "hours": len(idx)}

# ---------------- contingencies: station coverage
cov = CH.notna().mean(); EXCL = [s for s in ST if cov[s] < 0.5]; STU = [s for s in ST if s not in EXCL]
log["station_coverage"] = cov.round(4).to_dict(); log["excluded_stations"] = EXCL

# ---------------- H1
core = [s for s in CORE if s in STU]; X = CH[STU] - MED[STU]
Y = X[core].median(1).where(X[core].notna().sum(1) >= 5)
S = (P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"]); Sz = (S - S_MU) / S_SD
LU = np.log(composite(P["AMS 5"]).ws + 0.5)
h1 = e08.h1_estimate(Y.to_numpy(), Sz.to_numpy(), Sz.shift(-24).to_numpy(), LU.to_numpy(), idx, A.nboot_h1, np.random.default_rng(SEED + 1))
h1_eval = (Sz.notna().mean() >= 0.7) and (h1["n_primary"] >= 3000) and (len(core) >= 6)
h1["S_coverage"] = float(Sz.notna().mean()); h1["core_stations"] = core; h1["evaluable"] = bool(h1_eval)
h1["decision"] = e08.h1_decision(h1["b1_primary_ci"], h1["b1_joint"], h1["b_nc"], h1["b_nc_ci"]) if h1_eval else {"confirmed": None}

# ---------------- H2
W = {s: composite(P[s]) for s in STU}; FAM = pair_table(STU, CFG["h2"]["max_pair_km"]).reset_index(drop=True)
ndays = len(idx) // 24; SH = e08.admissible_shifts(ndays); blk = e08.block_ids(idx); nblk = blk.max() + 1
pairs, dropped = [], []
for _, r in FAM.iterrows():
    Ri, Rj = h2.lpo_residual_levels(X, r.i, r.j, STU); dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
    up, cs = h2.pair_wind(W[r.i], W[r.j], r.bearing); al, rv, tau = h2.sets(r.km, up, cs)
    if al.sum() < 100 or rv.sum() < 100:
        dropped.append(f"{r.i}->{r.j}"); continue
    used = h2.total_sums(dri, drj, al, rv)[:, 0, 0, 0]                      # complete-methane hours at lag 1, per set
    pairs.append(dict(pair=f"{r.i}->{r.j}", r=r, dri=dri, drj=drj, al=al, rv=rv, tau=tau, wind_eligible=int((al | rv).sum()),
                      methane_complete_aligned=int(used[0]), methane_complete_reversed=int(used[1])))
h2out = {"pairs_used": len(pairs), "pairs_dropped": dropped, "K": int(len(SH)), "min_p": 1 / (len(SH) + 1), "evaluable": len(pairs) >= 10}
if h2out["evaluable"]:
    Dobs = np.empty(len(pairs)); Dnull = np.empty((len(SH), len(pairs))); Dpm = {+1: np.empty(len(pairs)), -1: np.empty(len(pairs))}
    for p, q in enumerate(pairs):
        r = q["r"]
        for k, sh in enumerate(np.r_[0, SH]):
            up, cs = h2.pair_wind(W[r.i], W[r.j], r.bearing, int(sh) * 24); al, rv, tau = h2.sets(r.km, up, cs)
            D = h2.D_stat(q["dri"], q["drj"], al, rv, h2.weights(tau, al, rv))
            if k == 0: Dobs[p] = D
            else: Dnull[k - 1, p] = D
        for h in (+1, -1):
            up, cs = h2.pair_wind(W[r.i], W[r.j], r.bearing, h); al, rv, tau = h2.sets(r.km, up, cs)
            Dpm[h][p] = h2.D_stat(q["dri"], q["drj"], al, rv, h2.weights(tau, al, rv))
    pooled, pn, wts = e08.pooled_inverse_null_variance(Dobs, Dnull); prec = 1 / Dnull.var(0)
    pm = {h: float((prec * Dpm[h]).sum() / prec.sum()) for h in (+1, -1)}
    # centroid
    Sl = []
    for q in pairs:
        b = np.full(len(idx), -1)
        for k in range(len(e08.BINS) - 1): b[(q["tau"] >= e08.BINS[k]) & (q["tau"] < e08.BINS[k + 1])] = k
        Sl.append(e08.h2_block_sums(q["dri"], q["drj"], np.where(q["al"], b, -1), blk, nblk))
    c, possum, nbin = e08.h2_centroids(Sl)
    est = np.where((nbin >= 500) & (possum > 0) & np.isfinite(c))[0]
    rng = np.random.default_rng(SEED + 2); diffs = []
    for _ in range(A.nboot_centroid):
        w = np.bincount(rng.integers(0, nblk, nblk), minlength=nblk).astype(float)
        cb = e08.h2_centroids(Sl, w)[0]; diffs.append(cb[est[-1]] - cb[est[0]] if len(est) else np.nan)
    dci = (float(np.nanpercentile(diffs, 2.5)), float(np.nanpercentile(diffs, 97.5)))
    crule = e08.centroid_rule(c, nbin, possum, dci)
    off = np.minimum(SH, ndays - SH); terc = pd.qcut(off, 3, labels=["short", "medium", "long"])
    h2out.update(pooled_D=pooled, p=e08.finite_shift_p(pooled, pn), pooled_D_wind_plus1h=pm[+1], pooled_D_wind_minus1h=pm[-1],
                 centroids=[float(x) for x in c], centroid_n=[int(x) for x in nbin], centroid_diff_ci=dci, centroid_rule=crule,
                 null_by_offset_tercile=pd.Series(pn).groupby(np.asarray(terc)).agg(["mean", "std"]).round(4).to_dict(),
                 wind_eligible_hours_total=int(sum(q["wind_eligible"] for q in pairs)),
                 methane_complete_hours_total=int(sum(q["methane_complete_aligned"] + q["methane_complete_reversed"] for q in pairs)))
    h2out["criteria"] = dict(i_p_lt_005=h2out["p"] < 0.05, ii_positive_under_pm1h=pm[+1] > 0 and pm[-1] > 0, iii_centroid=crule["met"])
    h2out["confirmed"] = bool(all(h2out["criteria"].values())) if crule["evaluable"] else None
    np.save(OUT / "h2_null_matrix.npy", Dnull); np.save(OUT / "h2_Dobs.npy", Dobs)
    pd.DataFrame([dict(pair=q["pair"], D=Dobs[p], null_sd=float(Dnull[:, p].std()), weight=float(wts[p]), p_unadj=e08.finite_shift_p(Dobs[p], Dnull[:, p]),
                       wind_eligible_hours=q["wind_eligible"], methane_complete_aligned=q["methane_complete_aligned"],
                       methane_complete_reversed=q["methane_complete_reversed"]) for p, q in enumerate(pairs)]).round(5).to_csv(OUT / "h2_pairs.csv", index=False)

# ---------------- H3
def unit_counts(panel, years_index, years_list, thr, stations):
    """counts[station][year] = (H[block,18], X[block,18]) for the Jan-Sep window of each year."""
    out = {}
    for s in stations:
        d = panel[s]; e = (d["CH4 (ppm)"] > thr[s]).astype(float).where(d["CH4 (ppm)"].notna())
        Sx = d.get("AT90 (C)") if s == "AMS 5" else None
        out[s] = {}
        for y in years_list:
            m = (years_index >= pd.Timestamp(f"{y}-01-01 01:00")) & (years_index <= pd.Timestamp(f"{y}-10-01 00:00"))
            ii = years_index[m]; ev = e.reindex(ii).to_numpy()
            s5 = S_ALL.reindex(ii).to_numpy(); ws = composite(panel[s].reindex(ii)).ws.to_numpy()
            st = np.digitize(s5, CUTS); wc = np.digitize(ws, CFG["h3"]["wind_classes_ms"]); nt = (elevation_deg(ii) <= 0).to_numpy().astype(int)
            cell = st * 6 + wc * 2 + nt; ok = np.isfinite(ev) & np.isfinite(s5) & np.isfinite(ws)
            b = ((ii.dayofyear.to_numpy() - 1) // 14)[ok]; nb_ = 20
            H = np.bincount(b * 18 + cell[ok], minlength=nb_ * 18).reshape(nb_, 18)
            Xc = np.bincount(b * 18 + cell[ok], ev[ok], minlength=nb_ * 18).reshape(nb_, 18)
            out[s][y] = (H.astype(float), Xc)
    return out
S_ALL = pd.concat([(DEV["AMS 5"]["AT90 (C)"] - DEV["AMS 5"]["AT20 (C)"]), (P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"])])
S_ALL = S_ALL[~S_ALL.index.duplicated(keep="last")]
devC = unit_counts(DEV, DEV["AMS 1"].index, DEVYEARS, P95, STU); conC = unit_counts(P, idx, [CYEAR], P95, STU)
contr, share3, summ, _ = e08.h3_run(conC, devC, DEVYEARS, CYEAR, STU, A.nboot_h3, np.random.default_rng(SEED + 3))
contr.round(6).to_csv(OUT / "h3_contrasts.csv", index=False)
h3 = {"contrasts_planned": len(contr), "contrasts_estimable": int(contr.estimable.sum()), "share": share3}; h3.update(summ)
h3["evaluable"] = bool(summ["evaluable"] and h3["contrasts_estimable"] >= 30)
h3["confirmed"] = bool(summ["ci_lo"] > 0 or summ["ci_hi"] < 0) if h3["evaluable"] else None

res = dict(log=log, H1=h1, H2={k: v for k, v in h2out.items()}, H3=h3, runtime_s=round(time.time() - T0, 1))
(OUT / "e08_results.json").write_text(json.dumps(res, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
runmeta.write(OUT, dict(experiment=f"E08 runner ({A.mode})", seed=SEED, panel=str(A.panel)))
print(json.dumps(dict(H1=dict(b1=h1["b1_primary"], ci=h1["b1_primary_ci"], b_nc=h1["b_nc"], b_nc_ci=h1["b_nc_ci"], decision=h1["decision"]),
                      H2=dict(pooled_D=h2out.get("pooled_D"), p=h2out.get("p"), pm1h=(h2out.get("pooled_D_wind_plus1h"), h2out.get("pooled_D_wind_minus1h")),
                              centroids=h2out.get("centroids"), rule=h2out.get("centroid_rule"), confirmed=h2out.get("confirmed"),
                              dropped=dropped, wind_eligible=h2out.get("wind_eligible_hours_total"), methane_complete=h2out.get("methane_complete_hours_total"),
                              null_by_offset=h2out.get("null_by_offset_tercile")),
                      H3=h3, excluded=EXCL, runtime=res["runtime_s"]), indent=1, default=str))
