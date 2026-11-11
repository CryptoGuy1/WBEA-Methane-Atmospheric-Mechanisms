import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT / "src"))
from wbea.geometry import stations, pair_table
from wbea import h2
from .generator import STATIONS, N
COORDS = {s: c for s, c in stations().items() if s in STATIONS}
FAM = pair_table(STATIONS, 30.0).reset_index(drop=True)
SEASON_BLOCKS = [(0, 2160), (2160, 4344), (4344, N)]          # Jan-Mar 90 d, Apr-Jun 91 d, Jul-Sep 92 d
def residual_input(ch4):
    return ch4 - ch4.median()                                  # station reference median (as E08 subtracts 2021-2023 medians)
