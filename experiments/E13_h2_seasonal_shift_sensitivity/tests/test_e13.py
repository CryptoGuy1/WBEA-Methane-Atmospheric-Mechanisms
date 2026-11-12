import sys, pathlib, subprocess, numpy as np, pandas as pd, pytest
HERE = pathlib.Path(__file__).resolve().parents[1]; ROOT = HERE.parents[1]; sys.path.insert(0, str(HERE))
import e13
from e13 import circ_sums, D_from_sums, moment_matrix
from wbea import h2

def test_block_boundaries_and_dates():
    for blocks, ends in ((e13.C1, ["2026-04-01 00:00", "2026-07-01 00:00", "2026-10-01 00:00"]), (e13.C2, ["2026-05-01 00:00", "2026-10-01 00:00"])):
        assert blocks[0][0] == 0 and blocks[-1][1] == 6552 and all(blocks[k][1] == blocks[k + 1][0] for k in range(len(blocks) - 1))
        assert [str(e13.IDX[b - 1]) for _, b in blocks] == [e + ":00" for e in ends]          # hour-ending block ends
    assert [b - a for a, b in e13.C1] == [2160, 2184, 2208] and [b - a for a, b in e13.C2] == [2880, 3672]
    assert len(e13.C1_K) == 63 and len(e13.C2_K) == 93 and e13.C1_K.max() == 76 and e13.C2_K.max() == 106

def test_within_block_shift_matches_reference_roll_including_wraparound():
    rng = np.random.default_rng(1); a = rng.normal(size=6552); b = rng.normal(size=6552); a[rng.random(6552) < 0.05] = np.nan
    M = moment_matrix(a, b); m = rng.random(6552) < 0.3                        # genuine moment matrix: columns 0, 6, ... are counts
    for blocks in (e13.C1, e13.C2):
        for k in (14, 45, 76):
            ref = (M * e13.roll_within_blocks(m, blocks, k)[:, None]).sum(0)
            fast = sum(circ_sums(M[a:b], m[a:b], [24 * k])[0] for a, b in blocks)
            assert np.allclose(ref, fast, atol=1e-8)
    r = e13.roll_within_blocks(np.arange(6552), e13.C1, 14)                       # wraparound stays inside each block
    for a, b in e13.C1: assert set(r[a:b]) == set(range(a, b)) and r[a] == b - 14 * 24

def test_weights_invariant_under_within_block_roll():
    rng = np.random.default_rng(2); al = rng.random(6552) < 0.2; rv = (~al) & (rng.random(6552) < 0.2); tau = rng.uniform(0, 3, 6552)
    w0 = h2.weights(tau, al, rv)
    for k in (14, 50):
        R = lambda x: e13.roll_within_blocks(x, e13.C1, k)
        assert np.allclose(w0, h2.weights(R(tau), R(al), R(rv)))

@pytest.fixture(scope="module")
def data():
    if not (ROOT / "sealed/e08_panel").exists(): pytest.skip("sealed confirmation panel not present")
    inp = e13.load_inputs(); return inp, e13.pair_data(inp)

def test_reproduces_frozen_e08_h2(data):
    inp, pdl = data; assert inp["excluded"] == ["AMS 2"] and len(pdl) == 21
    frozen = pd.read_csv(ROOT / "experiments/E08_confirmation/confirmation_2026/h2_pairs.csv").set_index("pair")
    Dm = e13.D_whole(pdl, np.arange(14, 260)); s, _, _ = e13.summarise("R0", Dm)
    assert np.allclose(Dm[0], frozen.loc[[p["pair"] for p in pdl], "D"].values, atol=1e-5)          # CSV stored at 5 dp
    assert abs(s["pooled_D"] - 0.2879317084641316) < 1e-12 and s["p"] == 1 / 247 and s["K"] == 246

def test_observed_identical_across_configurations_and_deterministic(data):
    _, pdl = data; a = e13.D_blocks(pdl, e13.C1, e13.C1_K); b = e13.D_blocks(pdl, e13.C1, e13.C1_K)
    assert np.array_equal(a, b) and np.allclose(a[0], e13.D_whole(pdl, np.arange(14, 20))[0])

def test_e08_and_e12_unmodified():
    run = lambda *a: subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    assert run("diff", "--stat", "protocol-freeze", "--", "src/wbea", "PROTOCOL_E08_DRAFT_v2.md", "config", "experiments/E08_confirmation/run_e08.py") == ""
    assert run("diff", "--stat", "e08-confirmation", "--", "experiments/E08_confirmation/confirmation_2026") == ""
    assert run("diff", "--stat", "0ebdff79e625c760ae3ad56ddfb153c14637e1bf", "--", "experiments/E12_h2_synthetic_null_calibration") == ""
