"""E15 tests: pair sets and orientation, windows, residual universe, pooling formulas, fixed weights, empty pair sets,
missing data, shift-reference consistency (single window = frozen), determinism."""
import sys, json, pathlib, numpy as np, pandas as pd, pytest
HERE = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE))
import e15
from wbea import e08, h2
E = HERE.parents[0]

@pytest.fixture(scope="module")
def DEV(): return e15.load_dev()
@pytest.fixture(scope="module")
def MED(DEV): return e15.ref_medians(DEV)
P27 = list(pd.read_csv(E / "E05_directional_coupling/results/h2_pair_statistics.csv").pair)
P21 = list(pd.read_csv(E / "E08_confirmation/confirmation_2026/h2_pairs.csv").pair)

def test_pair_sets_and_orientation():
    assert len(P27) == 27 and len(P21) == 21 and set(P21) <= set(P27)
    assert all("AMS 2" in p.split("->") for p in set(P27) - set(P21)) and len(set(P27) - set(P21)) == 6
    from wbea.geometry import pair_table
    f11 = pair_table(e15.ST11, 30); assert set(f11.i + "->" + f11.j) == set(P21)          # same orientation under the 11-station universe

def test_windows(DEV, MED):
    raw, CH = e15.dev_year_raw(DEV, 2024, e15.ST11, P21, MED); assert len(CH) == 6552 and len(raw[0]["dri"]) == 6552

def test_universe_changes_residuals(DEV, MED):
    r12, _ = e15.dev_year_raw(DEV, 2023, e15.ST12, P21, MED); r11, _ = e15.dev_year_raw(DEV, 2023, e15.ST11, P21, MED)
    d = [np.nanmax(np.abs(a["dri"] - b["dri"])) for a, b in zip(r12, r11)]; assert max(d) > 0          # AMS 2 enters every LPO median

def test_single_window_equals_frozen(DEV, MED):
    raw, _ = e15.dev_year_raw(DEV, 2025, e15.ST12, P27, MED); s, _, _ = e15.analyse([raw], e08.admissible_shifts(273), "t")
    ref = json.loads((E / "E08_confirmation/dryrun_2025/e08_results.json").read_text())["H2"]["pooled_D"]; assert abs(s["pooled_D"] - ref) < 1e-10

def test_pooling_formula(DEV, MED):
    raw, _ = e15.dev_year_raw(DEV, 2022, e15.ST11, P21, MED); s, P, pn = e15.analyse([raw], e08.admissible_shifts(273), "t")
    prec = 1 / P.null_sd ** 2; assert abs(s["pooled_D"] - float((prec * P.D).sum() / prec.sum())) < 1e-12
    assert abs(P.weight.sum() - 1) < 1e-12 and abs(P.contribution.sum() - s["pooled_D"]) < 1e-12

def test_fixed_weights():
    assert e15.pool_fixed([1.0, 3.0], [1, 1]) == 2.0 and e15.pool_fixed([1.0, 3.0], [3, 1]) == 1.5

def test_empty_pair_set(DEV, MED):
    raw, _ = e15.dev_year_raw(DEV, 2022, e15.ST11, P21[:2], MED)
    for q in raw: q["al"][:] = False
    s, P, pn = e15.analyse([raw], e08.admissible_shifts(273), "t"); assert s is None and P.empty

def test_missing_not_imputed(DEV, MED):
    raw, CH = e15.dev_year_raw(DEV, 2021, e15.ST11, P21, MED); assert CH.isna().sum().sum() > 0 and np.isnan(raw[0]["dri"]).sum() > 0

def test_pooled_two_windows_is_sum_of_parts(DEV, MED):
    a, _ = e15.dev_year_raw(DEV, 2021, e15.ST11, P21[:1], MED); b, _ = e15.dev_year_raw(DEV, 2022, e15.ST11, P21[:1], MED)
    from e12.fast_h2 import circ_sums
    sh = np.r_[0, 14] * 24; S = circ_sums(a[0]["M"], a[0]["al"], sh) + circ_sums(b[0]["M"], b[0]["al"], sh)
    assert np.allclose(S[0, ::6], [a[0]["M"][a[0]["al"], k].sum() + b[0]["M"][b[0]["al"], k].sum() for k in range(0, 36, 6)])

def test_deterministic(DEV, MED):
    r, _ = e15.dev_year_raw(DEV, 2023, e15.ST11, P21, MED); s1, _, _ = e15.analyse([r], e08.admissible_shifts(273), "t")
    s2, _, _ = e15.analyse([r], e08.admissible_shifts(273), "t"); assert s1 == s2
