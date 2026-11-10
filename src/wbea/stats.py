import numpy as np, pandas as pd

def block_ids(index, block_days=14):
    return ((index - index[0]).days // block_days).to_numpy()

def block_bootstrap_indices(blocks, n_boot, rng):
    """Non-overlapping block resampling. Same draws can be reused across stations/pairs (joint bootstrap)."""
    ub = np.unique(blocks); pos = {b: np.where(blocks == b)[0] for b in ub}
    for _ in range(n_boot):
        yield np.concatenate([pos[b] for b in rng.choice(ub, len(ub))])

def pct_ci(x, alpha=0.05):
    x = np.asarray(x)[np.isfinite(x)]
    return np.percentile(x, [100 * alpha / 2, 100 * (1 - alpha / 2)])
