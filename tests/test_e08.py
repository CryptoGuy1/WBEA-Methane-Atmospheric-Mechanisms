"""Unit tests for E08 decision rules (PROTOCOL_E08_DRAFT_v2) and the splitter. Synthetic inputs only, except one
test that compares splitter output with the development panel on a short 2025 window (skipped if raw files absent)."""
import pathlib, sys, hashlib, numpy as np, pandas as pd, pytest, openpyxl
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "src" / "build"))
from wbea import e08
import build_e08_panel as sp

# ---------------- finite-shift inference
def test_admissible_shift_count_for_273_days():
    s = e08.admissible_shifts(273); assert len(s) == 246 and s[0] == 14 and s[-1] == 259

def test_finite_shift_p():
    null = np.arange(246) / 1000
    assert e08.finite_shift_p(1.0, null) == 1 / 247
    assert e08.finite_shift_p(0.0, null) == 1.0                     # ties count (>=)
    assert e08.finite_shift_p(0.1, null) == (1 + (null >= 0.1).sum()) / 247

# ---------------- H1 rule
@pytest.mark.parametrize("ci,b1,bnc,ncci,exp", [
    ((0.04, 0.05), 0.048, 0.000, (-0.005, 0.003), True),            # development-like
    ((-0.01, 0.05), 0.048, 0.000, (-0.005, 0.003), False),          # primary CI includes 0
    ((0.04, 0.05), 0.048, 0.030, (0.020, 0.040), False),            # NC CI excludes 0 and |b_nc| >= 0.5 b1
    ((0.04, 0.05), 0.048, 0.010, (0.005, 0.015), True),             # NC significant but small
    ((0.04, 0.05), 0.048, 0.030, (-0.010, 0.070), True),            # large but CI includes 0: not flagged (not proof of no confounding)
    ((0.04, 0.05), 0.048, 0.024, (0.010, 0.040), False)])           # exactly 50%: flagged
def test_h1_rule(ci, b1, bnc, ncci, exp):
    assert e08.h1_decision(ci, b1, bnc, ncci)["confirmed"] is exp

# ---------------- H2 centroid rule
N5, PS5 = [5000] * 5, [1] * 5
def test_centroid_strictly_increasing():
    r = e08.centroid_rule([0.25, 0.39, 0.73, 1.11, 1.51], N5, PS5, (0.8, 1.6)); assert r["met"] and r["rho"] == pytest.approx(1.0)

def test_centroid_one_adjacent_inversion_allowed():
    r = e08.centroid_rule([0.25, 0.73, 0.39, 1.11, 1.51], N5, PS5, (0.8, 1.6)); assert r["rho"] == pytest.approx(0.9) and r["met"]

def test_centroid_two_inversions_fail():
    r = e08.centroid_rule([0.39, 0.25, 1.11, 0.73, 1.51], N5, PS5, (0.8, 1.6)); assert r["rho"] == pytest.approx(0.8) and not r["met"]

def test_centroid_tie_handling():
    r = e08.centroid_rule([0.2, 0.4, 0.4, 1.0, 1.5], N5, PS5, (0.8, 1.6)); assert 0.9 <= r["rho"] < 1.0
    r2 = e08.centroid_rule([0.4, 0.4, 0.4, 0.4, 1.5], N5, PS5, (0.8, 1.6)); assert not r2["met"]

def test_centroid_four_bins_thresholds():
    n = [5000, 5000, 5000, 5000, 100]                               # last bin not estimable
    assert e08.centroid_rule([0.2, 0.4, 0.7, 1.1, 9.9], n, PS5, (0.5, 1.0))["met"]
    r = e08.centroid_rule([0.2, 0.7, 0.4, 1.1, 9.9], n, PS5, (0.5, 1.0)); assert r["rho"] == pytest.approx(0.8) and r["met"]

def test_centroid_not_evaluable():
    assert not e08.centroid_rule([np.nan, 0.4, 0.7, 1.1, 1.5], N5, PS5, (0.5, 1.0))["evaluable"]       # first bin missing
    assert not e08.centroid_rule([0.2, 0.4, 0.7, 1.1, 1.5], [5000, 5000, 5000, 10, 10], PS5, (0.5, 1.0))["evaluable"]
    assert not e08.centroid_rule([0.2, 0.4, 0.7, 1.1, 1.5], N5, [1, 1, 0, 0, 1], (0.5, 1.0))["evaluable"]

def test_centroid_difference_ci_must_exclude_zero():
    assert not e08.centroid_rule([0.25, 0.39, 0.73, 1.11, 1.51], N5, PS5, (-0.1, 1.6))["met"]

# ---------------- H3
def test_kitagawa_identity_and_empty_group():
    rng = np.random.default_rng(0); ha, hb = rng.integers(60, 200, 18).astype(float), rng.integers(60, 200, 18).astype(float)
    xa, xb = ha * rng.random(18) * .1, hb * rng.random(18) * .1; g = [np.array([k]) for k in range(18)]
    c, w, t, ok = e08.kitagawa_groups(ha, xa, hb, xb, g); assert ok and c + w == pytest.approx(t)
    hb2 = hb.copy(); hb2[3] = 0; assert e08.kitagawa_groups(ha, xa, hb2, xb, g)[3] is False

def test_merge_groups_rules():
    dense = np.full(18, 100.0); g = e08.merge_groups(dense, dense); assert len(g) == 18
    sparse = dense.copy(); sparse[0] = 10                           # cell (unstable, <1, day)
    g = e08.merge_groups(sparse, dense); assert any(set(x) == {0, 2, 4} for x in g) and len(g) == 16
    allsparse = np.full(18, 5.0); g = e08.merge_groups(allsparse, allsparse); assert len(g) == 2

def test_h3_nonestimable_replicates():
    s = np.r_[np.random.default_rng(1).normal(0.02, 0.03, 900), np.full(100, np.nan)]
    ok = np.r_[np.ones(900, bool), np.zeros(100, bool)]; r = e08.h3_bootstrap_summary(s, ok); assert r["evaluable"] and r["nonestimable_fraction"] == pytest.approx(0.10)
    ok2 = np.r_[np.ones(850, bool), np.zeros(150, bool)]; assert not e08.h3_bootstrap_summary(s, ok2)["evaluable"]

def test_projection_share():
    assert e08.projection_share([1, 1], [2, 2]) == pytest.approx(0.5)

# ---------------- splitter (synthetic fixtures)
def make_book(path, times, values, station="AMS 99", extra_after=None):
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Data"
    for k in range(6): ws.append([f"header {k}"])
    ws.append(["Station", station]); ws.append(["yyyy-MM-dd HH:mm", "CH4 (ppm)", ""])
    for t, v in zip(times, values): ws.append([t.strftime("%Y-%m-%d %H:%M"), v, ""])
    for t, v in (extra_after or []): ws.append([t.strftime("%Y-%m-%d %H:%M"), v, ""])
    ws.append(["Average", 1.0]); wb.save(path)

def test_splitter_boundaries_tokens_and_no_read_past_end(tmp_path):
    t = pd.date_range("2025-01-01 00:00", "2025-01-01 10:00", freq="h"); v = ["2.0", "Z", "2.1", ".", "2.2", "C", "2.3", "2.4", "2.5", "2.6", "2.7"]
    f = tmp_path / "b.xlsx"; make_book(f, t, v, extra_after=[(pd.Timestamp("2025-01-01 03:00"), "9.9")])   # out-of-order row AFTER end
    st, df = sp.split_workbook(f, pd.Timestamp("2025-01-01 01:00"), pd.Timestamp("2025-01-01 05:00"))
    assert st == "AMS 99" and list(df.time_mst_hour_ending) == list(pd.date_range("2025-01-01 01:00", "2025-01-01 05:00", freq="h"))
    assert list(df["CH4 (ppm)__token"]) == ["Z", "", ".", "", "C"]

def test_splitter_checksum_and_order_errors(tmp_path):
    t = pd.date_range("2025-01-01 00:00", periods=5, freq="h"); f = tmp_path / "b.xlsx"; make_book(f, t, ["2"] * 5)
    with pytest.raises(sp.SplitError): sp.split_workbook(f, t[0], t[-1], expected_sha="0" * 64)
    assert len(sp.split_workbook(f, t[0], t[-1], expected_sha=sp.sha256(f))[1]) == 5
    g = tmp_path / "c.xlsx"; make_book(g, [t[0], t[2], t[1], t[3]], ["2"] * 4)
    with pytest.raises(sp.SplitError): sp.split_workbook(g, t[0], t[-1])

def test_splitter_matches_dev_panel_on_2025_window():
    man = pd.read_csv(ROOT / "manifests" / "station_exports_2021_2026_manifest.csv").set_index("station")
    name = pathlib.Path(man.loc["AMS 1", "file"]).name
    raw = [p for r in ("/home/claude/raw_station", "/home/claude/raw_ext") for p in pathlib.Path(r).rglob(name)]
    if not raw: pytest.skip("raw exports not present")
    st, df = sp.split_workbook(raw[0], pd.Timestamp("2025-03-01 01:00"), pd.Timestamp("2025-03-03 00:00"), man.loc["AMS 1", "sha256"])
    dev = pd.read_parquet(ROOT / "data" / "dev" / "AMS1.parquet").set_index("time_mst_hour_ending").loc["2025-03-01 01:00":"2025-03-03 00:00"]
    assert st == "AMS 1" and len(df) == 48
    np.testing.assert_array_equal(df["CH4 (ppm)"].to_numpy(), dev["CH4 (ppm)"].to_numpy())
    assert list(df["CH4 (ppm)__token"]) == list(dev["CH4 (ppm)__token"])

# ---------------- added: max-T, pooled weighting, H3 with 4 and 5 development years, runner guards
def test_maxT_and_pooled_weights():
    rng = np.random.default_rng(3); null = rng.normal(0, [0.05, 0.1, 0.2], (246, 3)); obs = np.array([1.0, 0.0, 0.0])
    Z, p = e08.maxT_adjust(obs, null); assert p[0] == 1 / 247 and p[1] > 0.05 and Z[0] > Z[1]
    pooled, pn, w = e08.pooled_inverse_null_variance(obs, null)
    assert w.sum() == pytest.approx(1) and np.allclose(w, (1 / null.var(0)) / (1 / null.var(0)).sum())
    assert pooled == pytest.approx((w * obs).sum()) and pn.shape == (246,)

def _synthetic_counts(stations, years, rng, nb=20, empty=None):
    out = {}
    for s in stations:
        out[s] = {}
        for y in years:
            H = rng.integers(5, 15, (nb, 18)).astype(float); X = np.floor(H * rng.random((nb, 18)) * 0.2)
            if empty == (s, y): H[:, 7] = 0; X[:, 7] = 0
            out[s][y] = (H, X)
    return out

@pytest.mark.parametrize("devyears", [[2021, 2022, 2023, 2024], [2021, 2022, 2023, 2024, 2025]])
def test_h3_run_four_and_five_development_years(devyears):
    rng = np.random.default_rng(4); st = ["A", "B", "C"]
    con = _synthetic_counts(st, [2026], rng); dev = _synthetic_counts(st, devyears, rng)
    df, share, summ, bs = e08.h3_run(con, dev, devyears, 2026, st, 50, np.random.default_rng(5))
    assert len(df) == len(st) * len(devyears) and df.estimable.all()
    assert np.allclose(df.composition + df.within, df.total) and np.isfinite(share) and summ["evaluable"] and len(bs) == 50

def test_h3_run_empty_regime_and_six_groups():
    rng = np.random.default_rng(6); st = ["A", "B"]
    con = _synthetic_counts(st, [2026], rng); dev = _synthetic_counts(st, [2021, 2022, 2023, 2024], rng, empty=("A", 2022))
    six = [np.array([s_ * 6 + w * 2 + nt for w in range(3)]) for nt in (0, 1) for s_ in range(3)]
    df, _, _, _ = e08.h3_run(con, dev, [2021, 2022, 2023, 2024], 2026, st, 0, np.random.default_rng(0), groups=six)
    assert df.estimable.all() and (df.n_groups == 6).all()          # cell 7 empty but pooled inside a six-regime group
    one = [np.array([k]) for k in range(18)]
    df2, _, _, _ = e08.h3_run(con, dev, [2021, 2022, 2023, 2024], 2026, st, 0, np.random.default_rng(0), groups=one)
    assert not df2.set_index(["station", "dev_year"]).loc[("A", 2022), "estimable"]

def test_confirm_mode_guarded_and_descriptive_has_no_decisions():
    for script in ("run_e08.py", "run_e08_descriptive.py"):
        src = (ROOT / "experiments/E08_confirmation" / script).read_text()
        assert 'if A.mode == "confirm":\n    FROZEN_COMMIT = e08.assert_frozen(ROOT)' in src
    src = (ROOT / "experiments/E08_confirmation/run_e08_descriptive.py").read_text()
    assert "h1_decision" not in src and "centroid_rule" not in src and "H_BEFORE == H_AFTER" in src

def test_assert_frozen_release_guard(tmp_path):
    import subprocess
    g = lambda *a: subprocess.run(["git", *a], cwd=tmp_path, capture_output=True, text=True, check=True)
    g("init", "-q"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
    (tmp_path / "a.txt").write_text("1"); g("add", "a.txt"); g("commit", "-qm", "c1")
    with pytest.raises(SystemExit): e08.assert_frozen(tmp_path)                  # no tag
    g("tag", "protocol-freeze"); assert len(e08.assert_frozen(tmp_path)) == 40     # tagged, clean
    (tmp_path / "a.txt").write_text("2")
    with pytest.raises(SystemExit): e08.assert_frozen(tmp_path)                  # dirty
    g("commit", "-qam", "c2")
    with pytest.raises(SystemExit): e08.assert_frozen(tmp_path)                  # HEAD moved past tag
