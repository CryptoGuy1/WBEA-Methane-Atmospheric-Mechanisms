import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8, "figure.dpi": 150,
                     "savefig.dpi": 300, "font.family": "DejaVu Sans", "axes.spines.top": False,
                     "axes.spines.right": False})
def save(fig, path_noext):
    for ext in ("png", "svg", "pdf"):
        fig.savefig(f"{path_noext}.{ext}", bbox_inches="tight")
    plt.close(fig)
