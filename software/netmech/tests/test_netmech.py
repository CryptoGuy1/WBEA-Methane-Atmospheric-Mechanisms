import pathlib, sys, numpy as np, pandas as pd, pytest
HERE = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE / "src")); sys.path.insert(0, str(HERE / "examples"))
from netmech import e08, h2
from netmech.synthetic import make_network
import demo

def test_decision_rules():
    assert len(e08.admissible_shifts(273)) == 246
    assert e08.finite_shift_p(1.0, np.zeros(246)) == 1 / 247
    assert e08.h1_decision((0.04, 0.05), 0.048, 0.0, (-0.005, 0.003))["confirmed"]
    assert e08.centroid_rule([0.25, 0.73, 0.39, 1.11, 1.51], [5000] * 5, [1] * 5, (0.8, 1.6))["met"]
    assert not e08.centroid_rule([0.39, 0.25, 1.11, 0.73, 1.51], [5000] * 5, [1] * 5, (0.8, 1.6))["met"]

def test_synthetic_recovery_and_null():
    net = make_network(seed=0); out = demo.run(net, nboot=100)
    assert abs(out["h1_b1"] - net["truth"]["beta_s"]) < 0.02          # stability association recovered
    assert out["h2_pooled_D"] > 0 and out["h2_p"] < 0.05                 # advection detected
    null = demo.run(make_network(seed=0, advect_amp=0.0), nboot=50)
    assert abs(null["h2_pooled_D"]) < abs(out["h2_pooled_D"]) / 2       # no advection: much weaker contrast

def test_identical_to_frozen_wbea_modules():
    root = HERE.parents[1] / "src"
    if not (root / "wbea" / "h2.py").exists(): pytest.skip("WBEA project source not present")
    sys.path.insert(0, str(root)); from wbea import h2 as w_h2, e08 as w_e08
    rng = np.random.default_rng(9); a, b = rng.normal(size=(2, 3000)).cumsum(1) * 0.01
    al = rng.random(3000) < 0.3; rv = (~al) & (rng.random(3000) < 0.4); tau = rng.uniform(0, 3, 3000)
    w = h2.weights(tau, al, rv); assert np.allclose(w, w_h2.weights(tau, al, rv))
    assert h2.D_stat(np.diff(a, prepend=np.nan), np.diff(b, prepend=np.nan), al, rv, w) == \
           w_h2.D_stat(np.diff(a, prepend=np.nan), np.diff(b, prepend=np.nan), al, rv, w)
    null = rng.normal(size=(246, 4)); obs = rng.normal(size=4)
    assert np.allclose(e08.maxT_adjust(obs, null)[1], w_e08.maxT_adjust(obs, null)[1])
