"""E14 tests: calendar windows, shift enumeration, parity with the frozen dry run, swap construction, no imputation,
determinism, and no sealed-data access."""
import sys, json, pathlib, numpy as np, pandas as pd, pytest
HERE = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE))
import e14
from wbea.io import load_dev
from wbea import e08

@pytest.fixture(scope="module")
def DEV(): return load_dev()

def test_windows_align_on_calendar(DEV):
    for y in e14.YEARS:
        w = e14.window(DEV["AMS 1"][["CH4 (ppm)"]], y); assert len(w) == 6552 and (w.index == e14.TEMPLATE).all()
    src = DEV["AMS 1"].loc[pd.Timestamp("2024-03-01 01:00"), "CH4 (ppm)"]                 # first hour of 1 March 2024
    pos = int(np.where(e14.TEMPLATE == pd.Timestamp("2023-03-01 01:00"))[0][0])           # same calendar slot (29 Feb dropped)
    got = e14.window(DEV["AMS 1"][["CH4 (ppm)"]], 2024)["CH4 (ppm)"].iloc[pos]
    assert got == src or (np.isnan(got) and np.isnan(src))

def test_shift_enumeration_matches_frozen():
    assert np.array_equal(e14.K_WHOLE, e08.admissible_shifts(273, 14)) and len(e14.K_WHOLE) == 246

def test_parity_with_frozen_dryrun(DEV):
    rec, _ = e14.run_one(DEV, 2025, 2025, seasonal=False)
    ref = json.loads((HERE.parents[0] / "E08_confirmation/dryrun_2025/e08_results.json").read_text())["H2"]
    assert abs(rec["D"] - ref["pooled_D"]) < 1e-10 and rec["pairs"] == ref["pairs_used"] and rec["K"] == ref["K"] and rec["p"] == ref["p"]

def test_swap_uses_other_year_wind_and_own_year_methane(DEV):
    from wbea.wind import composite
    inp = e14.build_inputs(DEV, 2022, 2024); s = inp["STU"][0]
    assert inp["W"][s].equals(e14.window(composite(DEV[s]), 2024))
    med = pd.DataFrame({t: DEV[t]["CH4 (ppm)"] for t in inp["STU"]}).loc["2021":"2023"].median()
    np.testing.assert_allclose(inp["X"][s].values, e14.window(DEV[s][["CH4 (ppm)"]], 2022)["CH4 (ppm)"].values - med[s])

def test_no_imputation(DEV):
    inp = e14.build_inputs(DEV, 2023, 2021)
    for s in inp["STU"]: assert inp["X"][s].isna().sum() == e14.window(DEV[s][["CH4 (ppm)"]], 2023)["CH4 (ppm)"].isna().sum()

def test_deterministic(DEV):
    a, _ = e14.run_one(DEV, 2021, 2023, seasonal=False); b, _ = e14.run_one(DEV, 2021, 2023, seasonal=False); assert a == b

def test_confirmation_network_excludes_ams2(DEV):
    assert "AMS 2" not in e14.build_inputs(DEV, 2023, 2022, "confirmation_network")["STU"]

def test_no_sealed_access():
    for f in HERE.glob("*.py"): assert "sealed" not in f.read_text()
