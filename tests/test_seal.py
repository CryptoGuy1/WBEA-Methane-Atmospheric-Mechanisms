"""Seal tests: development code must not reach the confirmation period."""
import pathlib, re, sys, pandas as pd, pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from wbea.io import load_dev, CUT

ALLOWED_RAW_READERS = {"src/build/build_dev_panel.py", "src/build/build_e08_panel.py"}   # designated readers only          # one-time builder; stops at cutoff
RAW_PATTERNS = re.compile(r"(\.xlsx|/mnt/user-data/uploads|raw_station|FinalData_export|sealed/)")

def test_dev_panel_ends_at_cutoff():
    P = load_dev()
    assert max(d.index.max() for d in P.values()) == CUT

def test_no_development_script_reads_raw_exports():
    bad = []
    for f in list((ROOT / "src").rglob("*.py")) + list((ROOT / "experiments").rglob("*.py")):
        rel = f.relative_to(ROOT).as_posix()
        if rel in ALLOWED_RAW_READERS or rel.startswith("experiments/R1_readiness") or rel.startswith("experiments/E08") \
                or rel.startswith("experiments/E13_h2_seasonal_shift_sensitivity"):   # researcher-authorised post-confirmation reader (E13)
            continue                                                 # R1 archived as run; E08 is the only consumer
        if RAW_PATTERNS.search(f.read_text()):
            bad.append(rel)
    assert not bad, f"scripts touching raw/sealed data: {bad}"

def test_checksum_guard(tmp_path, monkeypatch):
    import wbea.io as io
    monkeypatch.setattr(io, "_checksums", lambda: {"AMS1.parquet": "0" * 64})
    with pytest.raises(RuntimeError):
        io.load_dev(["AMS 1"])
