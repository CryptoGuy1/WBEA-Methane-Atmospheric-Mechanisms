"""E12 analysis: rejection rates, Wilson intervals, Monte Carlo SEs, pre-registered classifications (EXPERIMENT_PLAN.md
section 7), p-value and D summaries, baseline summaries, figures. Reads results/raw_*.csv only."""
import json, pathlib, sys, numpy as np, pandas as pd
from scipy.stats import norm
HERE = pathlib.Path(__file__).resolve().parent; RES = HERE / "results"; FIG = HERE / "figures"; FIG.mkdir(exist_ok=True)
sys.path.insert(0, str(HERE.parents[1] / "src"))
from wbea.plotstyle import plt, save
ALPHA = 0.05; Q1 = ["N0", "N1a", "N2a", "N3"]; Q2 = ["N2b"]; Q4 = ["N1b"]
P = ["P1_t007", "P1_t013", "P1_ceiling", "P1_L2", "P1_L3", "P1T_t013", "P1T_ceiling"]
METHODS = {"primary": "p_primary", "within-season shift": "p_season", "truncated shift": "p_trunc"}

def wilson(k, n, z=norm.ppf(0.975)):
    if n == 0: return np.nan, np.nan
    p = k / n; d = 1 + z ** 2 / n; c = (p + z ** 2 / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / d
    return c - h, c + h

def null_class(L, U):
    if L <= ALPHA <= U and U <= 0.075: return "calibrated"
    if U < ALPHA: return "conservative"
    if L > ALPHA: return "inflated"
    return "inconclusive"

def power_class(L, U):
    return "adequate power" if L >= 0.80 else ("limited power" if U < 0.80 else "inconclusive")

df = pd.concat([pd.read_csv(f) for f in sorted(RES.glob("raw_*.csv"))], ignore_index=True)
rows = []
for scen, g in df.groupby("scenario"):
    ev = g[g.evaluable == True]
    for mname, col in METHODS.items():
        if col not in ev: continue
        k = int((ev[col] < ALPHA).sum()); n = len(ev); L, U = wilson(k, n); r = k / n if n else np.nan
        role = "Q1 null calibration" if scen in Q1 else "Q2 seasonal confounding" if scen in Q2 else "Q4 falsification" if scen in Q4 else "Q3 power"
        cls = (null_class(L, U) if role.startswith(("Q1", "Q2")) else power_class(L, U) if role.startswith("Q3") else "no verdict (by design)")
        dcol = {"primary": "D_primary", "within-season shift": "D_season", "truncated shift": "D_trunc"}[mname]
        rows.append(dict(scenario=scen, role=role, method=mname, n=n, not_evaluable=int((g.evaluable != True).sum()), rejections=k, rate=r,
                         wilson_lo=L, wilson_hi=U, mcse=np.sqrt(r * (1 - r) / n) if n else np.nan, classification=cls,
                         p_q05=ev[col].quantile(.05), p_q50=ev[col].quantile(.5), p_q95=ev[col].quantile(.95),
                         D_q05=ev[dcol].quantile(.05), D_q50=ev[dcol].median(), D_q95=ev[dcol].quantile(.95),
                         mean_pairs=ev.n_pairs.mean(), B1_mean_abs_A=ev.B1_mean_abs_A.mean(), B1_share_pairs_naive_sig=ev.B1_share_pairs_naive_sig.mean(),
                         runtime_mean_s=g.runtime_s.mean(), seeds=f"{int(g.seed.min())}-{int(g.seed.max())}", amp=g.amp.iloc[0], lag=g.lag.iloc[0]))
S = pd.DataFrame(rows); S.to_csv(RES / "summary_by_scenario_method.csv", index=False)

prim = S[S.method == "primary"].set_index("scenario")
q1 = [prim.loc[s, "classification"] for s in Q1 if s in prim.index]
q1_verdict = ("calibrated" if q1 and all(c in ("calibrated", "conservative") for c in q1) else "miscalibrated" if "inflated" in q1 else "inconclusive")
q2c = prim.loc["N2b", "classification"] if "N2b" in prim.index else "not run"
q2_verdict = {"calibrated": "robust to the tested seasonal confounding", "conservative": "robust to the tested seasonal confounding",
              "inflated": "sensitive", "inconclusive": "inconclusive"}.get(q2c, q2c)
verdicts = dict(Q1_null_calibration=q1_verdict, Q1_by_scenario={s: prim.loc[s, "classification"] for s in Q1 if s in prim.index},
                Q2_seasonal_confounding=q2_verdict, Q2_alternatives={m: S[(S.scenario == "N2b") & (S.method == m)].classification.iloc[0]
                                                                     for m in METHODS if not S[(S.scenario == "N2b") & (S.method == m)].empty},
                Q3_power={s: prim.loc[s, "classification"] for s in P if s in prim.index},
                Q3_power_at_D_ge_0_21="inconclusive: not testable with the tested coupling models (DEVIATIONS D4)",
                Q4_falsification_rejection_rate=float(prim.loc["N1b", "rate"]) if "N1b" in prim.index else None,
                total_replicates=int(len(df)), total_not_evaluable=int((df.evaluable != True).sum()))
(RES / "verdicts.json").write_text(json.dumps(verdicts, indent=1, default=str))

# ---------- figures
order = Q1 + Q2 + Q4; cols = {"primary": "k", "within-season shift": "C0", "truncated shift": "C1"}
labels = {"N0": "N0\nbaseline", "N1a": "N1a\ncommon driver", "N2a": "N2a\nseasonal drift", "N3": "N3\nautocorr.+gaps",
          "N2b": "N2b\nseasonal confound.", "N1b": "N1b\nadvected driver"}
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.1), gridspec_kw={"width_ratios": [2, 1]})
for ax, grp, ylim, ttl in ((axs[0], Q1, (0, 0.12), "a  Q1 calibration nulls"), (axs[1], Q2 + Q4, (0, 1.05), "b  Q2 confounding and Q4 falsification")):
    for j, m in enumerate(METHODS):
        d = S[(S.method == m) & S.scenario.isin(grp)].set_index("scenario").reindex(grp); x = np.arange(len(grp)) + (j - 1) * 0.22
        ax.errorbar(x, d.rate, yerr=[(d.rate - d.wilson_lo).clip(lower=0), (d.wilson_hi - d.rate).clip(lower=0)], fmt="o", ms=4, c=cols[m], capsize=2, label=m)
    ax.axhline(0.05, c="C3", lw=0.8, ls="--"); ax.set_ylim(*ylim); ax.set_xticks(range(len(grp)), [labels[g] for g in grp], fontsize=7)
    ax.set_title(ttl, fontsize=8)
axs[0].axhline(0.075, c="0.6", lw=0.6, ls=":"); axs[0].set_ylabel("Rejection rate at alpha = 0.05 (Wilson 95% CI)"); axs[0].legend(fontsize=6.5, frameon=False, loc="upper left")
fig.text(0.01, -0.04, "Dashed: nominal 0.05; dotted: pre-registered calibration upper bound 0.075. N1b violates the shift test's null by construction.", fontsize=6.3)
save(fig, FIG / "e12_null_rejection_rates")

fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
for s, c in zip(Q1 + Q2, ["k", "C0", "C1", "C2", "C3"]):
    p = np.sort(df[(df.scenario == s) & (df.evaluable == True)].p_primary.values); ax[0].step(p, np.arange(1, len(p) + 1) / len(p), where="post", c=c, label=s, lw=1)
ax[0].plot([0, 1], [0, 1], ":", c="0.5"); ax[0].set_xlabel("primary p-value"); ax[0].set_ylabel("empirical CDF"); ax[0].legend(fontsize=6, frameon=False)
ax[0].set_title("a  p-value CDFs under the nulls (uniform = diagonal)", fontsize=7.5)
for s, c in zip(Q1 + Q2 + Q4, ["k", "C0", "C1", "C2", "C3", "C4"]):
    ax[1].hist(df[(df.scenario == s) & (df.evaluable == True)].D_primary, bins=40, histtype="step", color=c, label=s, density=True)
ax[1].axvline(0.2879, c="C3", ls="--", lw=0.8); ax[1].set_xlabel("pooled D (primary)"); ax[1].legend(fontsize=6, frameon=False)
ax[1].set_title("b  Pooled D under nulls; dashed = registered 2026 value", fontsize=7.5)
save(fig, FIG / "e12_null_pvalue_cdf_and_D")

fig, ax = plt.subplots(figsize=(6.2, 3.0))
for fam, mk in (("P1_", "o"), ("P1T_", "s")):
    d = S[(S.method == "primary") & S.scenario.str.startswith(fam) & ~S.scenario.str.contains("_L")]
    ax.errorbar(d.D_q50, d.rate, yerr=[(d.rate - d.wilson_lo).clip(lower=0), (d.wilson_hi - d.rate).clip(lower=0)], fmt=mk, ms=4, capsize=2, label=fam.rstrip("_") + " (lag 1)" if fam == "P1_" else "P1T (transit lag)")
for s, mk in (("P1_L2", "^"), ("P1_L3", "v")):
    d = S[(S.method == "primary") & (S.scenario == s)]
    if len(d): ax.errorbar(d.D_q50, d.rate, yerr=[(d.rate - d.wilson_lo).clip(lower=0), (d.wilson_hi - d.rate).clip(lower=0)], fmt=mk, ms=4, capsize=2, label=s)
ax.axvspan(0.13, 0.29, color="0.93", zorder=0, label="observed H2 range 0.13-0.29"); ax.axhline(0.8, c="0.5", ls=":", lw=0.8)
ax.set_xlabel("median pooled D of the configuration"); ax.set_ylabel("power (primary test, alpha = 0.05)"); ax.legend(fontsize=6, frameon=False)
ax.set_title("Detection power (Wilson 95% CI)", fontsize=8)
save(fig, FIG / "e12_power")
print(S[S.method == "primary"][["scenario", "n", "rejections", "rate", "wilson_lo", "wilson_hi", "classification", "D_q50", "p_q50"]].round(4).to_string(index=False))
print(S[S.method != "primary"][["scenario", "method", "n", "rejections", "rate", "wilson_lo", "wilson_hi", "classification"]].round(4).to_string(index=False))
print(json.dumps(verdicts, indent=1, default=str))
