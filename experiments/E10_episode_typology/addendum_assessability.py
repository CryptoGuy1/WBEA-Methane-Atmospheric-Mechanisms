"""E10 descriptive addendum (researcher decision, 2026-11-10): split episodes by whether an upstream lead was
assessable (an eligible aligned pair existed at onset). L = 0 without an assessable pair is not evidence that a
lead was absent. Uses saved e10_episodes.csv only; no re-classification."""
import pathlib, pandas as pd, numpy as np
R = pathlib.Path(__file__).resolve().parent / "results"
ep = pd.read_csv(R / "e10_episodes.csv")
ep["assessability"] = np.where(ep.lead_assessable, "lead assessable", "no assessable pair")
t = ep.groupby("assessability").label.value_counts().unstack(fill_value=0)
t["n"] = t.sum(1); share = t.drop(columns="n").div(t.n, axis=0).round(4); share["n"] = t.n
share.to_csv(R / "addendum_assessability_split.csv")
med = ep.groupby("assessability")[["blh", "S_z", "duration_h", "peak_excess"]].median().round(3)
med.to_csv(R / "addendum_assessability_medians.csv")
st = ep.groupby("station").lead_assessable.mean().round(3); st.to_csv(R / "addendum_assessability_by_station.csv")
print(share.to_string()); print(med.to_string())
