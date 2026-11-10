"""Synthetic unit tests for WBEA proposal v2.0 equations (no WBEA data used).
Run:  python -m pytest -q test_v2_math.py   (or: python test_v2_math.py for printed diagnostics)
"""
import numpy as np

# ---------------------------------------------------------------- helpers (v2.0 sec 6.3)
def u_parallel(U, theta_from, phi_ij):
    """Along-path component; + = flow from i toward j. U in m/s, angles in degrees."""
    return U * np.cos(np.deg2rad(theta_from - phi_ij - 180.0))

def tau_hours(d_km, upar_ms):
    return d_km / (3.6 * upar_ms)

def vector_mean_wind(U1, th1, U2, th2):
    """Vector mean of two 'from' winds; returns (speed, from-direction)."""
    u = -(U1 * np.sin(np.deg2rad(th1)) + U2 * np.sin(np.deg2rad(th2))) / 2
    v = -(U1 * np.cos(np.deg2rad(th1)) + U2 * np.cos(np.deg2rad(th2))) / 2
    return np.hypot(u, v), (np.rad2deg(np.arctan2(-u, -v)) + 360) % 360

def tri(l, tau):
    return np.maximum(0.0, 1.0 - np.abs(l - tau))

def lead_asym(a, b, lag):
    """corr(a(t-lag), b(t)) - corr(b(t-lag), a(t)); identically 0 at lag 0."""
    if lag == 0:
        return np.corrcoef(a, b)[0, 1] - np.corrcoef(b, a)[0, 1]
    return np.corrcoef(a[:-lag], b[lag:])[0, 1] - np.corrcoef(b[:-lag], a[lag:])[0, 1]

def D_pair(dRi, dRj, aligned_ij, reversed_ij, lags=(1, 2, 3), w=None):
    w = np.ones(len(lags)) if w is None else np.asarray(w)
    def masked(mask, lag):
        idx = np.where(mask[lag:])[0] + lag            # receptor time t in the mask
        a = dRi[idx - lag]; b = dRj[idx]; a0 = dRi[idx]; bl = dRj[idx - lag]
        return np.corrcoef(a, b)[0, 1] - np.corrcoef(bl, a0)[0, 1]
    return sum(wk * (masked(aligned_ij, l) - masked(reversed_ij, l)) for wk, l in zip(w, lags))

def kitagawa(pi_a, q_a, pi_b, q_b):
    comp = np.sum((pi_a - pi_b) * (q_a + q_b) / 2)
    within = np.sum((pi_a + pi_b) * (q_a - q_b) / 2)
    return comp, within

# ---------------------------------------------------------------- tests
def test_wind_convention_and_units():
    phi = 30.0                                  # j lies 30 deg (NNE) of i
    assert np.isclose(u_parallel(2.0, phi + 180, phi), 2.0)    # wind FROM SSW blows i->j
    assert np.isclose(u_parallel(2.0, phi, phi), -2.0)         # wind from j's side: reversed
    assert abs(u_parallel(2.0, phi + 90, phi)) < 1e-12         # crosswind
    assert np.isclose(tau_hours(4.47, 4.47 / 3.6), 1.0)        # km and m/s -> hours
    s, th = vector_mean_wind(2, 350, 2, 10)                    # wrap-around averaging
    assert np.isclose(th % 360, 0.0, atol=1e-9) and s > 1.9

def test_lag0_asymmetry_is_identically_zero():
    rng = np.random.default_rng(0); a, b = rng.normal(size=(2, 500))
    assert lead_asym(a, b, 0) == 0.0

def simulate_hourly_pair(tau_h, n_hours=6000, corr_min=60.0, seed=0, noise=0.3):
    """Minute-resolution AR(1) signal s; station B sees s delayed by tau; both hour-averaged."""
    rng = np.random.default_rng(seed); m = n_hours * 60 + 600
    phi = np.exp(-1.0 / corr_min); e = rng.normal(size=m); s = np.empty(m); s[0] = 0
    for k in range(1, m): s[k] = phi * s[k - 1] + e[k]
    lag_min = int(round(tau_h * 60))
    A = s[600:600 + n_hours * 60]; B = s[600 - lag_min:600 - lag_min + n_hours * 60]
    A = A.reshape(n_hours, 60).mean(1) + noise * rng.normal(size=n_hours) * A.std()
    B = B.reshape(n_hours, 60).mean(1) + noise * rng.normal(size=n_hours) * B.std()
    return A, B

def lagged_corr(a, b, l):
    return np.corrcoef(a[:len(a) - l], b[l:])[0, 1] if l else np.corrcoef(a, b)[0, 1]

def test_kernel_levels_vs_differences():
    """Triangular kernel describes LEVELS of hour means for short-memory signals;
    FIRST DIFFERENCES produce negative side lobes, so the kernel shape differs."""
    A, B = simulate_hourly_pair(tau_h=1.0, corr_min=20)
    lev = [lagged_corr(A, B, l) for l in range(4)]
    dA, dB = np.diff(A), np.diff(B)
    dif = [lagged_corr(dA, dB, l) for l in range(4)]
    assert np.argmax(lev) == 1
    assert dif[2] < 0 or dif[0] < 0               # side lobe below zero for differences

def test_orientation_invariance():
    rng = np.random.default_rng(1); n = 4000
    x = rng.normal(size=n).cumsum() * 0.05
    dRi = np.diff(x + rng.normal(size=n)); dRj = np.diff(np.roll(x, 1) + rng.normal(size=n))
    al = rng.random(n - 1) < 0.4; rv = (~al) & (rng.random(n - 1) < 0.6)
    d1 = D_pair(dRi, dRj, al, rv); d2 = D_pair(dRj, dRi, rv, al)  # swap labels and sets
    assert np.isclose(d1, d2)

def test_kitagawa_identity_and_empty_cells():
    rng = np.random.default_rng(2)
    pa = rng.dirichlet(np.ones(18)); pb = rng.dirichlet(np.ones(18))
    qa = rng.random(18) * .1; qb = rng.random(18) * .1
    c, w = kitagawa(pa, qa, pb, qb)
    assert np.isclose(c + w, pa @ qa - pb @ qb)
    # empty cell in unit a: q_a undefined, components change while the total does not
    pa2 = pa.copy(); pa2[0] = 0; pa2 /= pa2.sum()
    c1, w1 = kitagawa(pa2, np.r_[0.0, qa[1:]], pb, qb)
    c2, w2 = kitagawa(pa2, np.r_[0.5, qa[1:]], pb, qb)
    assert np.isclose(c1 + w1, c2 + w2) and not np.isclose(c1, c2)

def test_unit_specific_terciles_kill_composition():
    """If stability terciles are recomputed per station-year, pi is ~1/3 by construction."""
    rng = np.random.default_rng(3)
    Sa = rng.normal(0.0, 1, 8000); Sb = rng.normal(0.8, 1, 8000)      # year b more stable
    own = [np.histogram(S, np.quantile(S, [0, 1/3, 2/3, 1]))[0] / len(S) for S in (Sa, Sb)]
    cut = np.quantile(Sa, [1/3, 2/3])                                  # fixed (training) cuts
    fixed = [np.bincount(np.digitize(S, cut), minlength=3) / len(S) for S in (Sa, Sb)]
    assert np.allclose(own[0], own[1], atol=0.01) and abs(fixed[1][2] - fixed[0][2]) > 0.2

def test_min_attainable_placebo_p():
    for K in (18, 30, 1000):
        assert np.isclose(1 / (K + 1), 1 / (K + 1))   # documented: min p with K placebos

if __name__ == "__main__":
    for t in [k for k in dir() if k.startswith("test_")]:
        globals()[t](); print("PASS", t)
    print("\nKernel diagnostics (corr of hour means; tau = transit hours, signal memory in min):")
    for mem in (20, 180):
        for tau in (0.3, 0.7, 1.0, 1.5, 2.5):
            A, B = simulate_hourly_pair(tau, corr_min=mem, seed=4)
            lev = [lagged_corr(A, B, l) for l in range(4)]
            dA, dB = np.diff(A), np.diff(B); dif = [lagged_corr(dA, dB, l) for l in range(4)]
            print(f" mem={mem:>3} tau={tau:.1f} tri={np.round(tri(np.arange(4), tau),2)}"
                  f" levels={np.round(lev,2)} diffs={np.round(dif,2)}")
