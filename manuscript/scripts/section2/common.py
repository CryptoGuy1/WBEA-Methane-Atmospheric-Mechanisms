"""Shared paths, style and loaders for Section 2 figures and tables (descriptive only; no inference)."""
import sys, pathlib, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = pathlib.Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT / "src"))
FIG = ROOT / "manuscript/figures/section2"; TAB = ROOT / "manuscript/tables/section2"; DATA = ROOT / "manuscript/data/section2"
GIS = DATA / "gis"
STUDY = ["AMS 1", "AMS 2", "AMS 5", "AMS 6", "AMS 7", "AMS 9", "AMS 11", "AMS 13", "AMS 14", "AMS 18", "AMS 23", "AMS 30"]
EXCLUDED = ["AMS 2"]                                   # pre-specified CH4 completeness rule (< 50% valid hours, Jan-Sep 2026)
PAIRS_CSV = ROOT / "experiments/E08_confirmation/confirmation_2026/h2_pairs.csv"        # frozen eligible pairs
E08_RESULTS = ROOT / "experiments/E08_confirmation/confirmation_2026/e08_results.json"
MM = 1 / 25.4
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.labelsize": 7, "axes.titlesize": 7.5,
                     "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.5, "axes.linewidth": 0.5,
                     "xtick.major.width": 0.5, "ytick.major.width": 0.5, "pdf.fonttype": 42, "ps.fonttype": 42,
                     "svg.fonttype": "none", "savefig.dpi": 600, "figure.dpi": 150})
def save(fig, stem):
    for ext in ("pdf", "svg"):
        fig.savefig(FIG / f"{stem}.{ext}", bbox_inches="tight", pad_inches=0.02, metadata={"Date": None} if ext == "svg" else {"CreationDate": None})
    fig.savefig(FIG / f"{stem}_600dpi.png", dpi=600, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
