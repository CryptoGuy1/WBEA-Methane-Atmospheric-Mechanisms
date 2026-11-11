import sys, pathlib, subprocess, numpy as np, pandas as pd, pytest
HERE = pathlib.Path(__file__).resolve().parents[1]; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / "src"))
from wbea import h2, e08
from e12 import generator as G, fast_h2 as F
from e12.setup_network import COORDS, FAM, SEASON_BLOCKS, residual_input

def frozen_loop(X, W, shifts_days):
    """Frozen per-pair D for each shift, exactly as experiments/E08_confirmation/run_e08.py computes it."""
    out = []
    for _, r in FAM.iterrows():
        Ri, Rj = h2.lpo_residual_levels(X, r.i, r.j, G.STATIONS); dri, drj = np.diff(np.r_[np.nan, Ri]), np.diff(np.r_[np.nan, Rj])
        up, cs = h2.pair_wind(W[r.i], W[r.j], r.bearing); al, rv, tau = h2.sets(r.km, up, cs)
        if al.sum() < 100 or rv.sum() < 100: continue
        row = []
        for sh in shifts_days:
            up, cs = h2.pair_wind(W[r.i], W[r.j], r.bearing, int(sh) * 24); al, rv, tau = h2.sets(r.km, up, cs)
            row.append(h2.D_stat(dri, drj, al, rv, h2.weights(tau, al, rv)))
        out.append(row)
    return np.array(out).T                                          # (shifts, pairs)

@pytest.mark.parametrize("scen,kw", [("N3", {}), ("N0", {}), ("P1", dict(amp=0.05, lag=1))])
def test_parity_with_frozen_pipeline(scen, kw):
    d = G.generate(scen, 777, COORDS, pair_wind_fn=h2.pair_wind, pairs=FAM, **kw); X = residual_input(d["ch4"])
    fast = F.evaluate(X, d["winds"], G.STATIONS, FAM, SEASON_BLOCKS, run_alternatives=False)
    K = e08.admissible_shifts(len(X) // 24); shifts = np.r_[0, K] if scen == "N3" else np.r_[0, K[[0, 50, 123, 200, 245]]]
    fr = frozen_loop(X, d["winds"], shifts)
    assert np.allclose(fr[0], fast["pair_D"], atol=1e-9, rtol=0)                     # observed per-pair D
    if scen == "N3":                                                                 # full 246-shift parity of pooled D and p
        pooled, pn, _ = e08.pooled_inverse_null_variance(fr[0], fr[1:])
        assert abs(pooled - fast["D_primary"]) < 1e-9 and e08.finite_shift_p(pooled, pn) == fast["p_primary"]

def test_determinism_and_shift_counts():
    a = G.generate("N0", 5, COORDS); b = G.generate("N0", 5, COORDS)
    pd.testing.assert_frame_equal(a["ch4"], b["ch4"])
    r = F.evaluate(residual_input(a["ch4"]), a["winds"], G.STATIONS, FAM, SEASON_BLOCKS)
    assert r["K_primary"] == 246 and r["K_season"] == 63 and r["K_trunc"] == 94
    assert r["p_primary"] in {k / 247 for k in range(1, 248)} and r["p_season"] in {k / 64 for k in range(1, 65)}

def test_positive_coupling_increases_D_null_does_not():
    n = F.evaluate(residual_input(G.generate("N0", 11, COORDS)["ch4"]), G.generate("N0", 11, COORDS)["winds"], G.STATIONS, FAM, SEASON_BLOCKS, run_alternatives=False)
    d = G.generate("P1", 11, COORDS, pair_wind_fn=h2.pair_wind, pairs=FAM, amp=0.2, lag=1)
    p = F.evaluate(residual_input(d["ch4"]), d["winds"], G.STATIONS, FAM, SEASON_BLOCKS, run_alternatives=False)
    assert p["D_primary"] > n["D_primary"] + 0.05 and p["p_primary"] < 0.05

def test_missingness_edge_case_pair_dropping():
    d = G.generate("N0", 3, COORDS); X = residual_input(d["ch4"]); X.loc[:, "AMS 1"] = np.nan
    r = F.evaluate(X, d["winds"], G.STATIONS, FAM, SEASON_BLOCKS, run_alternatives=False)
    assert r["excluded_stations"] == ["AMS 1"] and r["n_pairs"] < 21 and np.isfinite(r["D_primary"])   # E08 coverage rule

def test_frozen_files_unmodified():
    out = subprocess.run(["git", "diff", "--stat", "protocol-freeze", "--", "src/wbea", "PROTOCOL_E08_DRAFT_v2.md", "config",
                          "experiments/E08_confirmation/run_e08.py", "experiments/E08_confirmation/run_e08_descriptive.py"],
                         cwd=ROOT, capture_output=True, text=True).stdout.strip()
    assert out == ""
    st = subprocess.run(["git", "diff", "--stat", "e08-confirmation", "--", "experiments/E08_confirmation/confirmation_2026"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    assert st == ""
