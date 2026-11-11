"""POST-CONFIRMATION EXPLORATORY (v1, 2026-11-10). Reads saved E08 outputs only; changes nothing in
experiments/E08_confirmation/. Documents the weight concentration of the registered H3 pooled projection estimator
s = sum(c t) / sum(t^2). The registered estimate (0.011, CI -0.020 to 0.043) is NOT replaced by anything here."""
import pathlib, json, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]; OUT = pathlib.Path(__file__).resolve().parent / "results"; OUT.mkdir(exist_ok=True)
c = pd.read_csv(ROOT / "experiments/E08_confirmation/confirmation_2026/h3_contrasts.csv"); c = c[c.estimable]
c["t2"] = c.total ** 2; c["ct"] = c.composition * c.total
st = c.groupby("station").agg(sum_t2=("t2", "sum"), sum_ct=("ct", "sum"), contrasts=("t2", "size"))
st["denominator_share"] = st.sum_t2 / st.sum_t2.sum(); st["station_share"] = st.sum_ct / st.sum_t2
st.sort_values("denominator_share", ascending=False).round(5).to_csv(OUT / "h3_2026_denominator_by_station.csv")
ex = c[c.station != "AMS 18"]
dev = pd.read_csv(ROOT / "experiments/PRE_E08/results/h3_jan_sep_contrasts.csv"); dev["t2"] = dev.total ** 2
dshare = dev.groupby("station").t2.sum() / dev.t2.sum()
res = dict(label="POST-CONFIRMATION EXPLORATORY; not a substitute for the registered H3 estimate",
           registered_share=float((c.ct.sum()) / c.t2.sum()), AMS18_denominator_share_2026=float(st.loc["AMS 18", "denominator_share"]),
           AMS18_mean_abs_total_pp=float(100 * c[c.station == "AMS 18"].total.abs().mean()), others_mean_abs_total_pp=float(100 * ex.total.abs().mean()),
           share_excluding_AMS18_point=float(ex.ct.sum() / ex.t2.sum()), contrasts_excluding_AMS18=int(len(ex)),
           AMS18_denominator_share_development_JanSep=float(dshare.get("AMS 18", np.nan)),
           station_averaged_share_point=float(st.station_share.mean()))
(OUT / "h3_weight_concentration.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))
print(st.sort_values("denominator_share", ascending=False).round(4).to_string())
