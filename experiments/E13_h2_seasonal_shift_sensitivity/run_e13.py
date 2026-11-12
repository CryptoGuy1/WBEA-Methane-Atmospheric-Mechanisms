"""E13 runner (POST-CONFIRMATION EXPLORATORY). Deterministic; no random numbers."""
import json, pathlib, numpy as np, pandas as pd, e13
from wbea import e08
HERE = pathlib.Path(__file__).resolve().parent; RES = HERE / "results"
inp = e13.load_inputs(); pdl = e13.pair_data(inp); pairs = [p["pair"] for p in pdl]
def classify(p): return "remains unusual" if p <= 0.05 else ("not unusual" if p > 0.10 else "borderline")
rows, sur = [], {}
Dw = e13.D_whole(pdl, np.arange(14, 260)); s0, pn0, w0 = e13.summarise("R0 frozen whole-period (reproduction)", Dw); rows.append(s0); sur["R0"] = pn0
for name, blocks, K in (("C1", e13.C1, e13.C1_K), ("C2", e13.C2, e13.C2_K)):
    Dm = e13.D_blocks(pdl, blocks, K)
    s, pn, w = e13.summarise(f"{name}-w (season null, own weights)", Dm); rows.append(s); sur[f"{name}-w"] = pn
    s, pn, _ = e13.summarise(f"{name}-f (season null, frozen weights)", Dm, weights=w0); rows.append(s); sur[f"{name}-f"] = pn
    pp = pd.DataFrame({"pair": pairs, "D": Dm[0], "null_mean": Dm[1:].mean(0), "null_sd": Dm[1:].std(0),
                       "p_pair": [e08.finite_shift_p(Dm[0, k], Dm[1:, k]) for k in range(len(pairs))], "weight_own": w, "weight_frozen": w0})
    pp.to_csv(RES / f"e13_pairs_{name}.csv", index=False)
S = pd.DataFrame(rows); S["classification"] = [None] + [classify(p) for p in S.p[1:]]
# C4: per-season statistics, each quarter analysed separately
c4 = []
for q, (a, b) in zip(["Jan-Mar", "Apr-Jun", "Jul-Sep"], e13.C1):
    sub = e13.pair_data(inp, slice(a, b)); L = (b - a) // 24; K = np.arange(14, L - 14 + 1)
    cov = inp["X"].iloc[a:b].notna().mean()
    row = dict(season=q, days=L, pairs=len(sub), min_station_coverage=float(cov.min()), mean_station_coverage=float(cov.mean()))
    if len(sub) >= 10:
        Dm = e13.D_whole(sub, K); s, pn, _ = e13.summarise(q, Dm); row.update({k: v for k, v in s.items() if k != "configuration"}); sur[f"C4 {q}"] = pn
        row["classification"] = classify(s["p"])
    else: row["classification"] = "not evaluable (< 10 pairs)"
    c4.append(row)
C4 = pd.DataFrame(c4)
S.to_csv(RES / "e13_summary.csv", index=False); C4.to_csv(RES / "e13_per_season.csv", index=False)
for k, v in sur.items(): pd.Series(v, name="pooled_D_surrogate").to_csv(RES / f"e13_surrogates_{k.replace(' ', '_')}.csv", index=False)
c1, c2 = S.set_index("configuration").loc["C1-w (season null, own weights)", "classification"], S.set_index("configuration").loc["C2-w (season null, own weights)", "classification"]
overall = "strengthens" if (c1 == "remains unusual" and c2 == "remains unusual") else ("materially challenges" if c1 == "not unusual" else "qualifies")
out = dict(label="POST-CONFIRMATION EXPLORATORY", excluded_stations=inp["excluded"], pairs=pairs, summary=S.to_dict("records"),
           per_season=C4.to_dict("records"), overall_rule_outcome=overall, station_coverage=inp["coverage"].round(4).to_dict())
(RES / "e13_results.json").write_text(json.dumps(out, indent=1, default=float))
pd.set_option("display.width", 250)
print(S[["configuration", "pairs", "K", "p_floor", "pooled_D", "p", "n_surrogates_ge_obs", "null_mean", "null_sd", "null_q95", "null_q99", "null_max", "z", "classification"]].round(4).to_string(index=False))
print(C4.round(4).to_string(index=False)); print("OVERALL (pre-registered rule):", overall)
