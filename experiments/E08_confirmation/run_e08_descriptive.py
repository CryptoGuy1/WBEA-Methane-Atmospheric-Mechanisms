"""E08 DESCRIPTIVE outputs (PROTOCOL_E08_DRAFT_v2, section 4). No pass/fail; cannot alter H1-H3 decisions.
Guards: writes only to <out>/descriptive/; reads primary outputs read-only and verifies their SHA-256 are unchanged
after running; calls no decision-rule function; refuses --mode confirm until the protocol freeze.
Usage: python run_e08_descriptive.py --mode dryrun --panel <dir> --primary <primary out dir>"""
import argparse, hashlib, json, pathlib, sys, time, numpy as np, pandas as pd, netCDF4 as nc
ROOT = pathlib.Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "src"))
from wbea.config import CFG
from wbea.io import load_dev, load_era5
from wbea.wind import composite
from wbea.geometry import pair_table, stations as XYfun
from wbea.solar import elevation_deg
from wbea import h2, e08, runmeta

ap = argparse.ArgumentParser(); ap.add_argument("--mode", choices=["dryrun", "confirm"], required=True)
ap.add_argument("--panel", required=True); ap.add_argument("--primary", required=True); A = ap.parse_args()
if A.mode == "confirm":
    FROZEN_COMMIT = e08.assert_frozen(ROOT)          # release guard: protocol-freeze commit, clean tree
PRIM = pathlib.Path(A.primary); OUT = PRIM / "descriptive"; OUT.mkdir(exist_ok=True); T0 = time.time()
def tree_hash(d): return {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(d.iterdir()) if f.is_file()}
H_BEFORE = tree_hash(PRIM)
SEED = 20261190; WIN = {"dryrun": ("2025-01-01 01:00", "2025-10-01 00:00", 2025, [2021, 2022, 2023, 2024]),
                        "confirm": ("2026-01-01 01:00", "2026-10-01 00:00", 2026, [2021, 2022, 2023, 2024, 2025])}[A.mode]
START, END, CYEAR, DEVYEARS = pd.Timestamp(WIN[0]), pd.Timestamp(WIN[1]), WIN[2], WIN[3]
DEV = load_dev(); ST = CFG["stations"]["usable"]; CORE = CFG["stations"]["h1_core_response"]
REF = pd.DataFrame({s: DEV[s]["CH4 (ppm)"] for s in ST}).loc["2021":"2023"]; MED, P95 = REF.median(), REF.quantile(.95)
S_REF = (DEV["AMS 5"]["AT90 (C)"] - DEV["AMS 5"]["AT20 (C)"]).loc["2021":"2023"]; S_MU, S_SD = S_REF.mean(), S_REF.std()
CUTS = S_REF.quantile([1 / 3, 2 / 3]).values; UPPER = S_REF.quantile(2 / 3)
PAN = {d.station.iloc[0]: d.set_index("time_mst_hour_ending") for d in (pd.read_parquet(f) for f in pathlib.Path(A.panel).glob("AMS*.parquet"))}
idx = pd.date_range(START, END, freq="h"); P = {s: PAN[s].reindex(idx) for s in ST}
CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); X = CH - MED
prim = json.loads((PRIM / "e08_results.json").read_text()); EXCL = prim["log"]["excluded_stations"]; STU = [s for s in ST if s not in EXCL]
W = {s: composite(P[s]) for s in STU}; blk = e08.block_ids(idx); nblk = blk.max() + 1; out = {}

# ERA5 for the window, read directly from the raw reanalysis file (meteorology, not a methane outcome)
def era5_window(stations):
    f = pathlib.Path(CFG["data"]["era5_file"])                      # configurable path (release check 2)
    if hashlib.sha256(f.read_bytes()).hexdigest() != CFG["data"]["era5_sha256"]: raise RuntimeError("ERA5 checksum mismatch")
    ds = nc.Dataset(f)
    lat, lon = np.array(ds["latitude"][:]), np.array(ds["longitude"][:]); t = pd.to_datetime(np.array(ds["valid_time"][:]), unit="s") - pd.Timedelta(hours=7)
    keep = (t >= START - pd.Timedelta(hours=1)) & (t <= END); XY = XYfun(); res = {}
    for s in stations:
        i, j = int(np.argmin(abs(lat - XY[s][0]))), int(np.argmin(abs(lon - XY[s][1])))
        d = pd.DataFrame({v: np.array(ds[v][:, i, j])[keep] for v in ("blh", "u100", "v100")}, index=t[keep])
        res[s] = ((d + d.shift(1)) / 2).reindex(idx)                     # hour-ending average (D-02/D-66)
    return res
ERA = era5_window(ST)

# ---------------- 1. H2 per-pair statistics with max-T; verification of weighting and counts
FAM = pair_table(STU, 30.0).reset_index(drop=True); SH = e08.admissible_shifts(len(idx) // 24)
rows, Dobs, Dnull, cnt_check = [], [], [], []
for _, r in FAM.iterrows():
    Ri, Rj = h2.lpo_residual_levels(X[STU], r.i, r.j, STU); dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
    up, cs = h2.pair_wind(W[r.i], W[r.j], r.bearing); al, rv, tau = h2.sets(r.km, up, cs)
    if al.sum() < 100 or rv.sum() < 100: continue
    n_lib = h2.total_sums(dri, drj, al, rv)[:, 0, 0, 0]
    lag1 = np.r_[np.nan, dri[:-1]], np.r_[np.nan, drj[:-1]]
    full = np.isfinite(lag1[0]) & np.isfinite(drj) & np.isfinite(lag1[1]) & np.isfinite(dri)
    cnt_check.append(dict(pair=f"{r.i}->{r.j}", wind_eligible=int((al | rv).sum()), methane_complete_lib=int(n_lib.sum()),
                          methane_complete_direct=int((full & (al | rv)).sum())))
    d = []
    for sh in np.r_[0, SH]:
        u2, c2 = h2.pair_wind(W[r.i], W[r.j], r.bearing, int(sh) * 24); a2, r2, t2 = h2.sets(r.km, u2, c2)
        d.append(h2.D_stat(dri, drj, a2, r2, h2.weights(t2, a2, r2)))
    Dobs.append(d[0]); Dnull.append(d[1:]); rows.append(f"{r.i}->{r.j}")
Dobs, Dnull = np.array(Dobs), np.array(Dnull).T
Z, pfw = e08.maxT_adjust(Dobs, Dnull); pooled, pn, w = e08.pooled_inverse_null_variance(Dobs, Dnull)
prim_null = np.load(PRIM / "h2_null_matrix.npy"); prim_D = np.load(PRIM / "h2_Dobs.npy")
pd.DataFrame({"pair": rows, "D": Dobs, "Z": Z, "p_unadj": [e08.finite_shift_p(Dobs[k], Dnull[:, k]) for k in range(len(rows))],
              "p_maxT_familywise": pfw, "weight": w}).round(5).to_csv(OUT / "h2_pairs_maxT.csv", index=False)
cc = pd.DataFrame(cnt_check); cc.to_csv(OUT / "h2_count_verification.csv", index=False)
out["h2_verification"] = dict(null_matrix_identical_to_primary=bool(np.allclose(prim_null, Dnull, equal_nan=True)),
                              Dobs_identical=bool(np.allclose(prim_D, Dobs)), pooled_recomputed=pooled, pooled_primary=prim["H2"]["pooled_D"],
                              weights_sum_to_1=bool(abs(w.sum() - 1) < 1e-12),
                              weights_equal_inverse_null_variance=bool(np.allclose(w, (1 / Dnull.var(0)) / (1 / Dnull.var(0)).sum())),
                              complete_counts_lib_equals_direct=bool((cc.methane_complete_lib == cc.methane_complete_direct).all()),
                              pairs_familywise_lt_005=int((pfw < 0.05).sum()), K=int(len(SH)))

# ---------------- 2. H1 CR1, basic interval (same seed and draws as primary), ERA5 proxy
core = [s for s in CORE if s in STU]; Y = X[core].median(1).where(X[core].notna().sum(1) >= 5)
S = (P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"]); Sz = (S - S_MU) / S_SD; LU = np.log(composite(P["AMS 5"]).ws + 0.5)
h1 = e08.h1_estimate(Y.to_numpy(), Sz.to_numpy(), Sz.shift(-24).to_numpy(), LU.to_numpy(), idx, 2000, np.random.default_rng(SEED + 1), return_draws=True)
b, d_ = h1["b1_primary"], h1["draws_primary"]
def cr1(Yv, Xv, cell, cl):
    ok = np.isfinite(np.column_stack([Yv, Xv])).all(1); cell, cl = pd.factorize(cell[ok])[0], cl[ok]
    arr = np.column_stack([Yv[ok], Xv[ok]]); n = np.bincount(cell)
    m = np.vstack([np.bincount(cell, arr[:, j], minlength=len(n)) for j in range(arr.shape[1])]).T / n[:, None]; Zm = arr - m[cell]
    Xm, y = Zm[:, 1:], Zm[:, 0]; XtX = np.linalg.inv(Xm.T @ Xm); bb = XtX @ Xm.T @ y; e = y - Xm @ bb
    U = np.column_stack([np.bincount(pd.factorize(cl)[0], Xm[:, k] * e) for k in range(Xm.shape[1])]); G = U.shape[0]
    V = XtX @ (U.T @ U) @ XtX * G / (G - 1) * (len(y) - 1) / (len(y) - Xm.shape[1] - len(n)); return bb[0], np.sqrt(V[0, 0])
cellraw = (idx.year * 10000 + idx.month * 100 + idx.hour).to_numpy()
bc, se = cr1(Y.to_numpy(), np.column_stack([Sz.to_numpy(), LU.to_numpy()]), cellraw, blk)
eref = load_era5()["AMS 5"]["blh"].loc["2021":"2023"]; ezr = -np.log(eref); E5 = (-np.log(ERA["AMS 5"].blh) - ezr.mean()) / ezr.std()
he = e08.h1_estimate(Y.to_numpy(), E5.to_numpy(), E5.shift(-24).to_numpy(), LU.to_numpy(), idx, 1000, np.random.default_rng(SEED + 5))
out["h1_descriptive"] = dict(b1=b, percentile_ci=h1["b1_primary_ci"], primary_ci_reproduced=bool(np.allclose(h1["b1_primary_ci"], prim["H1"]["b1_primary_ci"])),
                             basic_ci=(2 * b - np.percentile(d_, 97.5), 2 * b - np.percentile(d_, 2.5)),
                             cr1_ci=(bc - 1.96 * se, bc + 1.96 * se), cr1_se=se, era5_proxy_b=he["b1_primary"], era5_proxy_ci=he["b1_primary_ci"])

# ---------------- 3. lag-kernel comparison with both simulation references (development-fixed)
obs_c = np.array(prim["H2"]["centroids"], float)
r06 = pd.read_csv(ROOT / "experiments/E06_detectability_kernel/results/review_continuous_centroids.csv")
r09 = pd.read_csv(ROOT / "experiments/E09_elevated_wind/results/r1_centroids_reference_sse.csv").set_index("variant")
refs = {"mask-gated, A = 0.3 (E06 corrections)": r06[(r06.model.str.startswith("original")) & (r06.A == 0.3)][[f"centroid_bin{k}" for k in range(5)]].values[0],
        "continuous source, A = 0.3, 50 replicates (E09-r1)": r09.loc["W0", [f"ref_bin{k}" for k in range(5)]].values.astype(float)}
pd.DataFrame([dict(reference=k, **{f"bin{j}_ref": v[j] for j in range(5)}, **{f"bin{j}_obs": obs_c[j] for j in range(5)},
                   SSE=float(np.nansum((obs_c - v) ** 2))) for k, v in refs.items()]).round(4).to_csv(OUT / "kernel_reference_comparison.csv", index=False)

# ---------------- 4. H3 per-station shares and six-regime sensitivity
def unit_counts(panel, ix, years, stations):
    S_all = pd.concat([DEV["AMS 5"]["AT90 (C)"] - DEV["AMS 5"]["AT20 (C)"], P["AMS 5"]["AT90 (C)"] - P["AMS 5"]["AT20 (C)"]])
    S_all = S_all[~S_all.index.duplicated(keep="last")]; res = {}
    for s in stations:
        e = (panel[s]["CH4 (ppm)"] > P95[s]).astype(float).where(panel[s]["CH4 (ppm)"].notna()); res[s] = {}
        for y in years:
            ii = ix[(ix >= pd.Timestamp(f"{y}-01-01 01:00")) & (ix <= pd.Timestamp(f"{y}-10-01 00:00"))]
            ev, s5, ws = e.reindex(ii).to_numpy(), S_all.reindex(ii).to_numpy(), composite(panel[s].reindex(ii)).ws.to_numpy()
            cell = np.digitize(s5, CUTS) * 6 + np.digitize(ws, CFG["h3"]["wind_classes_ms"]) * 2 + (elevation_deg(ii) <= 0).to_numpy().astype(int)
            ok = np.isfinite(ev) & np.isfinite(s5) & np.isfinite(ws); b_ = ((ii.dayofyear.to_numpy() - 1) // 14)[ok]
            res[s][y] = (np.bincount(b_ * 18 + cell[ok], minlength=360).reshape(20, 18).astype(float),
                         np.bincount(b_ * 18 + cell[ok], ev[ok], minlength=360).reshape(20, 18))
    return res
devC = unit_counts(DEV, DEV["AMS 1"].index, DEVYEARS, STU); conC = unit_counts(P, idx, [CYEAR], STU)
con, sh18, _, _ = e08.h3_run(conC, devC, DEVYEARS, CYEAR, STU, 0, np.random.default_rng(0))
six = [np.array([st * 6 + w_ * 2 + nt for w_ in range(3)]) for nt in (0, 1) for st in range(3)]
_, sh6, s6, _ = e08.h3_run(conC, devC, DEVYEARS, CYEAR, STU, 300, np.random.default_rng(SEED + 6), groups=six)
ps = con[con.estimable].groupby("station").apply(lambda d: e08.projection_share(d.composition, d.total)).rename("share")
ps.round(4).to_csv(OUT / "h3_per_station_shares.csv")
out["h3_descriptive"] = dict(share_18_regimes=sh18, share_primary=prim["H3"]["share"], share_6_regimes=sh6, ci_6_regimes=(s6["ci_lo"], s6["ci_hi"]))

# ---------------- 5. F5 regime distribution (D-50)
REG = ["stable-low-wind", "intermediate", "advective"]; O = np.zeros((nblk, 3)); Hh = np.zeros((nblk, 3)); onsets_all = {}
for s in STU:
    c = CH[s]; gap1 = c.isna() & c.shift(1).notna() & c.shift(-1).notna(); cb = c.where(~gap1, (c.shift(1) + c.shift(-1)) / 2)
    above = cb > P95[s]; below = cb.notna() & ~above; onset = (above & below.shift(1, fill_value=False)).to_numpy(); onsets_all[s] = onset
    wsv = W[s].ws.to_numpy(); st_ = (S >= UPPER).to_numpy(); valid = np.isfinite(S.to_numpy()) & np.isfinite(wsv)
    reg = np.where(~valid, 3, np.where(st_ & (wsv < 1.0), 0, np.where((wsv >= 2.5) & ~st_, 2, 1)))
    for k in range(3):
        O[:, k] += np.bincount(blk[onset & (reg == k)], minlength=nblk); Hh[:, k] += np.bincount(blk[c.notna().to_numpy() & (reg == k)], minlength=nblk)
rng = np.random.default_rng(SEED + 7); bsr = []
for _ in range(1000):
    wv = np.bincount(rng.integers(0, nblk, nblk), minlength=nblk).astype(float); o, h = wv @ O, wv @ Hh; bsr.append((o / o.sum()) / (h / h.sum()))
pd.DataFrame({"regime": REG, "onsets": O.sum(0), "onset_share": O.sum(0) / O.sum(), "hour_share": Hh.sum(0) / Hh.sum(),
              "enrichment": (O.sum(0) / O.sum()) / (Hh.sum(0) / Hh.sum()), "ci_lo": np.percentile(bsr, 2.5, 0),
              "ci_hi": np.percentile(bsr, 97.5, 0)}).round(4).to_csv(OUT / "f5_regime_distribution.csv", index=False)

# ---------------- 6. X4 elevated-wind centroids (W0 vs ERA5 100 m transit on W0-aligned hours)
SlW0, SlW4 = [], []
for _, r in FAM.iterrows():
    Ri, Rj = h2.lpo_residual_levels(X[STU], r.i, r.j, STU); dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
    up, cs = h2.pair_wind(W[r.i], W[r.j], r.bearing); al, rv, tau0 = h2.sets(r.km, up, cs)
    u4 = ((ERA[r.i].u100 + ERA[r.j].u100) / 2).to_numpy(); v4 = ((ERA[r.i].v100 + ERA[r.j].v100) / 2).to_numpy(); ph = np.deg2rad(r.bearing)
    with np.errstate(invalid="ignore", divide="ignore"):
        tau4 = r.km / (3.6 * np.abs(u4 * np.sin(ph) + v4 * np.cos(ph)))
    for tau, store in ((tau0, SlW0), (tau4, SlW4)):
        bn = np.full(len(idx), -1)
        for k in range(5): bn[(tau >= e08.BINS[k]) & (tau < e08.BINS[k + 1])] = k
        store.append(e08.h2_block_sums(dri, drj, np.where(al, bn, -1), blk, nblk))
cW0, _, nW0 = e08.h2_centroids(SlW0); cW4, _, nW4 = e08.h2_centroids(SlW4)
pd.DataFrame({"bin": [f"{e08.BINS[k]}-{e08.BINS[k + 1]} h" for k in range(5)], "centroid_W0": cW0, "n_W0": nW0, "centroid_ERA5_100m": cW4, "n_ERA5_100m": nW4}) \
  .round(4).to_csv(OUT / "x4_centroids.csv", index=False)

# ---------------- 7. E10 episode categories with assessability
CORE10 = [s for s in STU if s not in ("AMS 14", "AMS 18")]
XD = pd.DataFrame({s: DEV[s]["CH4 (ppm)"] for s in ST}); XD = XD - XD.loc["2021":"2023"].median(); DEV_SD = {}
for _, r in FAM.iterrows():                                         # E10: pair-specific LPO residual changes over 2021-2025, all usable stations
    a_, b_ = h2.lpo_residual_levels(XD, r.i, r.j, ST); DEV_SD[(r.i, r.j)] = (np.nanstd(np.diff(a_)), np.nanstd(np.diff(b_)))
A_ = pd.DataFrame({k: CH[k].gt(P95[k]).astype(float).where(CH[k].notna()) for k in CORE10})
Wret = pd.concat([A_.shift(1), A_, A_.shift(-1)]).groupby(level=0).max().reindex(idx); Vn = CH[CORE10].notna()
L = {s: np.zeros(len(idx), bool) for s in STU}; AS = {s: np.zeros(len(idx), bool) for s in STU}
for _, r in FAM.iterrows():
    Ri, Rj = h2.lpo_residual_levels(X[STU], r.i, r.j, STU); za, zb = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
    sa, sb = DEV_SD[(r.i, r.j)]                                    # development-period standardisation, as in E10 (release check 1)
    za, zb = za / sa, zb / sb; up, cs = h2.pair_wind(W[r.i], W[r.j], r.bearing); al, rv, _ = h2.sets(r.km, up, cs)
    for recv, z, flow in ((r.j, za, al), (r.i, zb, rv)):
        zl = np.nanmax(np.vstack([np.r_[np.full(l, np.nan), z[:-l]] for l in (1, 2, 3)]), 0); L[recv] |= flow & (zl >= 1); AS[recv] |= flow
eps = []
for s in STU:
    for t in np.where(onsets_all[s])[0]:
        ks = [k for k in CORE10 if k != s and Vn.iloc[t][k]]; sig = np.nanmean(Wret.iloc[t][ks].values) if ks else np.nan
        lab = "unclassified" if len(ks) < 4 or not np.isfinite(sig) else (("mixed" if L[s][t] else "accumulation-compatible") if sig >= 0.5
                                                                         else ("advection-compatible" if L[s][t] else "isolated"))
        eps.append(dict(station=s, assessable=bool(AS[s][t]), label=lab))
ep = pd.DataFrame(eps); ep["assessability"] = np.where(ep.assessable, "lead assessable", "no assessable pair (not physically isolated)")
tab = ep.groupby("assessability").label.value_counts(normalize=True).unstack(fill_value=0).round(4); tab["n"] = ep.groupby("assessability").size()
tab.to_csv(OUT / "e10_typology_shares_by_assessability.csv")

# ---------------- guard check and write
H_AFTER = tree_hash(PRIM)
assert H_BEFORE == H_AFTER, "primary outputs were modified by the descriptive runner"
out["guard_primary_outputs_unchanged"] = True; out["runtime_s"] = round(time.time() - T0, 1)
(OUT / "descriptive_results.json").write_text(json.dumps(out, indent=1, default=lambda o: o.item() if hasattr(o, "item") else list(o) if hasattr(o, "__iter__") else str(o)))
runmeta.write(OUT, dict(experiment="E08 descriptive (dry run)", seed_base=SEED))
print(json.dumps(out, indent=1, default=lambda o: o.item() if hasattr(o, "item") else list(o) if hasattr(o, "__iter__") else str(o)))
print(pd.read_csv(OUT / "kernel_reference_comparison.csv").to_string(index=False)); print(pd.read_csv(OUT / "f5_regime_distribution.csv").to_string(index=False))
print(pd.read_csv(OUT / "x4_centroids.csv").to_string(index=False)); print(tab.to_string())
