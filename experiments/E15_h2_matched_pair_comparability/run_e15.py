"""E15 production: analyses A0-A7 (+ A2b, A3y, A5y), decomposition paths, pair diagnostics, weight sensitivity, period environment.
Deterministic. Writes results/*.csv and results/run_log.json. Implements EXPERIMENT_PLAN.md exactly."""
import sys, json, time, platform, subprocess, pathlib, numpy as np, pandas as pd
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import e15
from wbea.wind import composite
from wbea import e08
OUT = HERE / "results"; OUT.mkdir(exist_ok=True); E = HERE.parents[0]; t0 = time.time()
DEV = e15.load_dev(); MED = e15.ref_medians(DEV); PAN = e15.load_2026()
P27 = list(pd.read_csv(E / "E05_directional_coupling/results/h2_pair_statistics.csv").pair)
P21 = list(pd.read_csv(E / "E08_confirmation/confirmation_2026/h2_pairs.csv").pair)
K273 = e08.admissible_shifts(273); S, PT, issues = [], {}, []
def rec(aid, desc, window, universe, pairs_in, reference, s, P):
    if s is None: issues.append(f"{aid}: no eligible pair"); return
    S.append(dict(id=aid, description=desc, window=window, universe=universe, pairs_requested=pairs_in, pairs=s["pairs"], K=s["K"], reference=reference,
                  pooled_D=s["pooled_D"], pooled_null_sd=s["pooled_null_sd"], z=s["z"], p=s["p"], p_floor=s["p_floor"], eff_pairs=s["eff_pairs"],
                  aligned_hours=int(P.n_aligned.sum()), reversed_hours=int(P.n_reversed.sum()))); PT[aid] = P.assign(analysis=aid)

# A0 published development (saved E05) and A1 frozen confirmation (saved E08)
e5 = pd.read_csv(E / "E05_directional_coupling/results/h2_pair_statistics.csv"); n5 = pd.read_csv(E / "E05_directional_coupling/results/h2_null_distribution.csv.gz").values
prec = 1 / n5.std(0) ** 2; w5 = prec / prec.sum(); A0 = float(w5 @ e5.D.values); pn0 = n5 @ w5
S.append(dict(id="A0", description="Published development (saved E05 outputs)", window="2021-01-01 to 2025-12-02", universe="12", pairs_requested=27, pairs=27, K=1000,
              reference="1,000 random whole-day shifts (seeded)", pooled_D=A0, pooled_null_sd=float(pn0.std()), z=float((A0 - pn0.mean()) / pn0.std()),
              p=float((1 + (pn0 >= A0).sum()) / 1001), p_floor=1 / 1001, eff_pairs=float(1 / np.sum(w5 ** 2)), aligned_hours=int(e5.n_aligned.sum()), reversed_hours=int(e5.n_reversed.sum())))
PT["A0"] = pd.DataFrame(dict(pair=e5.pair, km=e5.km, n_aligned=e5.n_aligned, n_reversed=e5.n_reversed, D=e5.D, null_mean=n5.mean(0), null_sd=n5.std(0), weight=w5, contribution=w5 * e5.D, analysis="A0"))
C = E / "E08_confirmation/confirmation_2026"; Do, Nm = np.load(C / "h2_Dobs.npy"), np.load(C / "h2_null_matrix.npy"); A1, pn1, w1 = e08.pooled_inverse_null_variance(Do, Nm)
h1 = pd.read_csv(C / "h2_pairs.csv")
S.append(dict(id="A1", description="Frozen 2026 confirmation (saved E08 outputs)", window="Jan-Sep 2026", universe="11", pairs_requested=21, pairs=21, K=246,
              reference="all 246 whole-day shifts", pooled_D=A1, pooled_null_sd=float(pn1.std()), z=float((A1 - pn1.mean()) / pn1.std()), p=e08.finite_shift_p(A1, pn1),
              p_floor=1 / 247, eff_pairs=float(1 / np.sum(w1 ** 2)), aligned_hours=np.nan, reversed_hours=np.nan))
PT["A1"] = pd.DataFrame(dict(pair=h1.pair, D=Do, null_mean=Nm.mean(0), null_sd=Nm.std(0), weight=w1, contribution=w1 * Do, analysis="A1"))

# full development window (frozen procedure on one contiguous window)
CHf = pd.DataFrame({s: DEV[s]["CH4 (ppm)"] for s in e15.ST12}); Wf = {s: composite(DEV[s]) for s in e15.ST12}; Kf = e08.admissible_shifts(len(CHf) // 24)
for aid, uni, pr, desc in (("A2", e15.ST12, P27, "Full development, frozen reference"), ("A2b", e15.ST11, P21, "Full development, 21 pairs, 11-station universe")):
    s, P, _ = e15.analyse([e15.pair_raw(e15.inputs(CHf, Wf, uni, pr, MED))], Kf, aid)
    rec(aid, desc, "2021-01-01 to 2025-12-02", str(len(uni)), len(pr), f"all {len(Kf)} whole-day shifts", s, P)
# Jan-Sep development: per year and pooled
yr = {(y, u): e15.dev_year_raw(DEV, y, U, pr, MED) for y in e15.DEV_YEARS for u, U, pr in (("12/27", e15.ST12, P27), ("12/21", e15.ST12, P21), ("11/21", e15.ST11, P21))}
for y in e15.DEV_YEARS:
    for tag, key in (("A3y", "12/27"), ("A5y", "11/21")):
        s, P, _ = e15.analyse([yr[(y, key)][0]], K273, f"{tag}_{y}"); rec(f"{tag}_{y}", f"Jan-Sep {y}", f"Jan-Sep {y}", key.split("/")[0], int(key.split("/")[1]), "all 246 whole-day shifts", s, P)
for aid, key, desc in (("A3", "12/27", "Jan-Sep 2021-2025 pooled, 27 pairs"), ("A4", "12/21", "Jan-Sep pooled, 21 shared pairs, AMS 2 in residual universe"),
                       ("A5", "11/21", "Jan-Sep pooled, 21 pairs, 11-station universe")):
    s, P, _ = e15.analyse([yr[(y, key)][0] for y in e15.DEV_YEARS], K273, aid)
    rec(aid, desc, "Jan-Sep 2021-2025 (pooled)", key.split("/")[0], int(key.split("/")[1]), "joint within-year shifts k = 14..259 (exploratory)", s, P)
# 2026: frozen-equivalent recomputation (check), AMS 2 retained in universe (exploratory)
for aid, uni, pr, desc in (("A1r", e15.ST11, P21, "2026 recomputed (check of A1)"), ("A6", e15.ST12, P27, "2026, AMS 2 retained, 27 pairs (exploratory)"),
                           ("A7", e15.ST12, P21, "2026, AMS 2 in residual universe, 21 pairs (exploratory)")):
    s, P, _ = e15.analyse([e15.raw_2026(PAN, uni, pr, MED)[0]], K273, aid); rec(aid, desc, "Jan-Sep 2026", str(len(uni)), len(pr), "all 246 whole-day shifts", s, P)
T = pd.DataFrame(S); T.to_csv(OUT / "comparison_table.csv", index=False); pairs_all = pd.concat(PT.values(), ignore_index=True); pairs_all.to_csv(OUT / "pair_level_all.csv", index=False)
D = T.set_index("id").pooled_D

# decomposition paths (telescoping; exact by construction, order-dependent)
paths = {"path_1": ["A0", "A2", "A3", "A4", "A5", "A1"], "path_2": ["A0", "A2", "A2b", "A5", "A1"]}
lab = {("A0", "A2"): "reference (random 1,000 -> all shifts)", ("A2", "A3"): "window (full -> Jan-Sep pooled)", ("A3", "A4"): "pair set (27 -> 21; AMS 2 in universe)",
       ("A4", "A5"): "residual universe (12 -> 11)", ("A5", "A1"): "period (development Jan-Sep -> 2026), same pairs/universe",
       ("A2", "A2b"): "pairs + universe (27/12 -> 21/11), full window", ("A2b", "A5"): "window (full -> Jan-Sep pooled), 21/11"}
dec = [dict(path=k, step=f"{a} -> {b}", factor=lab[(a, b)], delta=D[b] - D[a]) for k, v in paths.items() for a, b in zip(v[:-1], v[1:])]
pd.DataFrame(dec).to_csv(OUT / "decomposition_paths.csv", index=False)
# shared-pair weights (A5 vs A1), cross-weights, equal weights, leave-one-pair-out
a5 = PT["A5"].set_index("pair"); a1 = PT["A1"].set_index("pair"); sp = a1.index.intersection(a5.index)
shared = pd.DataFrame(dict(D_dev=a5.D[sp], D_2026=a1.D[sp], null_sd_dev=a5.null_sd[sp], null_sd_2026=a1.null_sd[sp], w_dev=a5.weight[sp], w_2026=a1.weight[sp],
                           contrib_dev=a5.contribution[sp], contrib_2026=a1.contribution[sp], n_al_dev=a5.n_aligned[sp], n_rv_dev=a5.n_reversed[sp]))
shared["delta_D"] = shared.D_2026 - shared.D_dev; shared["delta_contrib"] = shared.contrib_2026 - shared.contrib_dev
pr_d, pr_c = 1 / shared.null_sd_dev ** 2, 1 / shared.null_sd_2026 ** 2
shared["loo_dev"] = [(pr_d.drop(p) * shared.D_dev.drop(p)).sum() / pr_d.drop(p).sum() for p in shared.index]
shared["loo_2026"] = [(pr_c.drop(p) * shared.D_2026.drop(p)).sum() / pr_c.drop(p).sum() for p in shared.index]
shared.round(6).to_csv(OUT / "shared_pairs_A5_vs_A1.csv")
ws = dict(own=(D["A5"], D["A1"]), dev_weights=(e15.pool_fixed(shared.D_dev, shared.w_dev), e15.pool_fixed(shared.D_2026, shared.w_dev)),
          weights_2026=(e15.pool_fixed(shared.D_dev, shared.w_2026), e15.pool_fixed(shared.D_2026, shared.w_2026)), equal=(shared.D_dev.mean(), shared.D_2026.mean()))
pd.DataFrame([dict(scheme=k, pooled_dev_JanSep=v[0], pooled_2026=v[1], difference=v[1] - v[0]) for k, v in ws.items()]).to_csv(OUT / "weight_sensitivity.csv", index=False)
# period environment: 21 pairs, 11-station universe
env = []
for lab_, raws, CHs in [(f"Jan-Sep {y}", [yr[(y, '11/21')][0]], [yr[(y, '11/21')][1]]) for y in e15.DEV_YEARS] + [("Jan-Sep 2026", [e15.raw_2026(PAN, e15.ST11, P21, MED)[0]], [e15.raw_2026(PAN, e15.ST11, P21, MED)[1]])]:
    r = raws[0]; elig = np.concatenate([q["al"] | q["rv"] for q in r])
    env.append(dict(window=lab_, aligned_hours=int(sum(q["al"].sum() for q in r)), reversed_hours=int(sum(q["rv"].sum() for q in r)),
                    median_ws_eligible=float(np.nanmedian(np.concatenate([q["ws"][q["al"] | q["rv"]] for q in r]))),
                    sd_residual_change=float(np.nanstd(np.concatenate([q["dri"] for q in r]))), ch4_coverage=float(CHs[0][e15.ST11].notna().mean().mean())))
envd = pd.DataFrame(env); envd["eff_pairs"] = [T.set_index("id").eff_pairs.get(f"A5y_{y}", np.nan) for y in e15.DEV_YEARS] + [T.set_index("id").eff_pairs["A1"]]; envd.to_csv(OUT / "period_environment.csv", index=False)
commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()
(OUT / "run_log.json").write_text(json.dumps(dict(commit=commit, python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__, runtime_s=round(time.time() - t0, 1),
    analyses=len(T), issues=issues, randomness="none"), indent=1))
print(T[["id", "pairs", "K", "pooled_D", "pooled_null_sd", "z", "p", "eff_pairs"]].round(4).to_string(index=False)); print("issues:", issues)
