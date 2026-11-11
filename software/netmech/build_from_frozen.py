"""Regenerate src/netmech/h2.py and src/netmech/e08.py from the frozen WBEA modules (run from the repository root
checkout at tag protocol-freeze or later; the copied functions are unchanged)."""
import pathlib
R = pathlib.Path(__file__).resolve().parents[2]; P = pathlib.Path(__file__).resolve().parent / "src/netmech"
HDR = ('"""Copied mechanically from the WBEA project (src/wbea/{0}.py, frozen at tag protocol-freeze) by\n'
       'software/netmech/build_from_frozen.py. Only the configuration import is replaced by explicit defaults. Do not edit by hand."""\n')
h2 = (R / "src/wbea/h2.py").read_text().replace("from .config import CFG\n",
     "DEFAULTS = dict(max_pair_km=30.0, lags=[1, 2, 3], u_min_ms=1.0, max_tau_h=3.0, align_cos=0.707, kmin_other_stations=4)\n")
h2 = h2.replace('H2 = CFG["h2"]; LAGS = H2["lags"]', 'H2 = DEFAULTS; LAGS = H2["lags"]')
(P / "h2.py").write_text(HDR.format("h2") + h2)
(P / "e08.py").write_text(HDR.format("e08") + (R / "src/wbea/e08.py").read_text().replace("from .config import CFG\n", ""))
