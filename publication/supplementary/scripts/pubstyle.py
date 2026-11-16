"""Shared style and read-only data access for Supplement figures and tables. Style matches main-text Figs. 4-7:
DejaVu Sans, 6-7.5 pt, (a)-style bold panel labels outside the upper-left axes corner, no in-panel titles, 174.5 mm width,
colour-blind-safe palette (grey development, blue 2026/primary, orange accent; cividis/viridis sequential). Results are
read with `git show <commit>:<path>` from the pinned experiment source commit, so nothing is copied or modified."""
import io, json, subprocess, pathlib, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
ROOT = pathlib.Path(__file__).resolve().parents[3]; SUP = ROOT / "publication/supplementary"; FIG = SUP / "figures"; DATA = SUP / "data"
SRC = "17883015a4ed7e998701cf67a77a4a7c1c2754a4"      # research/e15-h2-matched-pair-comparability head (contains E01-E15)
MS = "b61ffbfd35f9cc97626d8f92840e52ac4f7e74ad"       # manuscript/section2-figures-tables head
MM = 1 / 25.4; W = 174.5
C_DEV, C_PRI, C_ACC, C_GRID, C_MUTE = "#4d4d4d", "#2171b5", "#d95f02", "#d9d9d9", "#7f7f7f"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.linewidth": 0.6, "axes.labelsize": 7, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
                     "legend.fontsize": 6.2, "pdf.fonttype": 42, "svg.fonttype": "none", "xtick.major.width": 0.5, "ytick.major.width": 0.5,
                     "xtick.major.size": 2.5, "ytick.major.size": 2.5, "axes.spines.top": False, "axes.spines.right": False})
def git_bytes(path, ref=SRC):
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{path}"], capture_output=True); assert r.returncode == 0, (ref, path); return r.stdout
def csv(path, ref=SRC, **k): return pd.read_csv(io.BytesIO(git_bytes(path, ref)), compression="gzip" if path.endswith(".gz") else None, **k)
def js(path, ref=SRC): return json.loads(git_bytes(path, ref))
def label(ax, s, dx=-0.02, dy=1.02):
    ax.text(dx, dy, f"({s})", transform=ax.transAxes, fontsize=8, fontweight="bold", ha="right", va="bottom")
def save(fig, name):
    for ext in ("pdf", "svg"): fig.savefig(FIG / f"{name}.{ext}", metadata={"Date": None} if ext == "svg" else {"CreationDate": None})
    fig.savefig(FIG / f"{name}.png", dpi=600); plt.close(fig)
def wilson(k, n, z=1.959963984540054):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d; return c - h, c + h
