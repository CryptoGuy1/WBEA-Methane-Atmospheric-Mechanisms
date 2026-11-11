"""End-to-end demonstration on a synthetic network with known mechanisms (runs in about a minute).
Usage: python examples/demo.py"""
import numpy as np, pandas as pd
from netmech import e08, h2
from netmech.geometry import pair_table, Wind
from netmech.synthetic import make_network

def run(net, nboot=200, seed=1):
    idx, st = net["index"], list(net["stations"])
    CH = pd.DataFrame({s: net["stations"][s]["ch4_ppm"] for s in st}); X = CH - CH.median()
    # H1: stability association with year x month x hour cells and a next-day negative control
    Y = X.median(1).where(X.notna().sum(1) >= 4); S = net["stability"]
    LU = np.log(net["stations"][st[0]]["ws_ms"] + 0.5)
    h1 = e08.h1_estimate(Y.to_numpy(), S.to_numpy(), S.shift(-24).to_numpy(), LU.to_numpy(), idx, nboot, np.random.default_rng(seed))
    d1 = e08.h1_decision(h1["b1_primary_ci"], h1["b1_joint"], h1["b_nc"], h1["b_nc_ci"])
    # H2: directional coupling with all admissible whole-day wind shifts
    W = {s: Wind(net["stations"][s]["ws_ms"], net["stations"][s]["wd_from_deg"]) for s in st}
    fam = pair_table(net["coords"], 30.0); shifts = e08.admissible_shifts(len(idx) // 24); Dobs, Dnull = [], []
    for _, r in fam.iterrows():
        Ri, Rj = h2.lpo_residual_levels(X, r.i, r.j, st); dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
        d = []
        for sh in np.r_[0, shifts]:
            up, cs = h2.pair_wind(W[r.i], W[r.j], r.bearing, int(sh) * 24); al, rv, tau = h2.sets(r.km, up, cs)
            d.append(h2.D_stat(dri, drj, al, rv, h2.weights(tau, al, rv)))
        Dobs.append(d[0]); Dnull.append(d[1:])
    Dobs, Dnull = np.array(Dobs), np.array(Dnull).T
    pooled, pn, w = e08.pooled_inverse_null_variance(Dobs, Dnull)
    Z, pfw = e08.maxT_adjust(Dobs, Dnull)
    return dict(h1_b1=h1["b1_primary"], h1_ci=h1["b1_primary_ci"], h1_b_nc=h1["b_nc"], h1_decision=d1,
                h2_pooled_D=pooled, h2_p=e08.finite_shift_p(pooled, pn), h2_K=len(shifts), h2_pairs=len(fam),
                h2_pairs_familywise=int((pfw < 0.05).sum()))

if __name__ == "__main__":
    net = make_network(seed=0)
    out = run(net)
    print("truth:", net["truth"]); [print(f"{k}: {v}") for k, v in out.items()]
    null = run(make_network(seed=0, advect_amp=0.0))
    print("no-advection control: pooled D", round(null["h2_pooled_D"], 4), "p", round(null["h2_p"], 4))
