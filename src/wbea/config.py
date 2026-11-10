import tomllib, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
CFG = tomllib.loads((ROOT / "config" / "project.toml").read_text())
