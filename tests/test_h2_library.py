"""The shared H2 library must reproduce the archived E05 statistics exactly."""
import pathlib, sys, numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from wbea.config import CFG
from wbea.io import load_dev
from wbea.wind import composite
from wbea.geometry import pair_table
from wbea import h2

def test_reproduces_e05():
    P = load_dev(); ST = CFG["stations"]["usable"]
    CH = pd.DataFrame({s: P[s]["CH4 (ppm)"] for s in ST}); X = CH - CH.loc["2021":"2023"].median()
    W = {s: composite(P[s]) for s in ST}; fam = pair_table(ST, 30.0).reset_index(drop=True)
    e05 = pd.read_csv(ROOT / "experiments/E05_directional_coupling/results/h2_pair_statistics.csv").set_index("pair")
    for k in (0, 5, 20):
        r = fam.iloc[k]; Ri, Rj = h2.lpo_residual_levels(X, r.i, r.j, ST)
        dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
        upar, cosang = h2.pair_wind(W[r.i], W[r.j], r.bearing); al, rv, tau = h2.sets(r.km, upar, cosang)
        D = h2.D_stat(dri, drj, al, rv, h2.weights(tau, al, rv))
        assert abs(D - e05.loc[f"{r.i}->{r.j}", "D"]) < 1e-4
