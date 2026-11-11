# E12 Manuscript handoff

**Branch:** https://github.com/CryptoGuy1/WBEA-Methane-Atmospheric-Mechanisms/tree/research/e12-h2-null-calibration. Not merged to `main`.
**Commits:** plan c45f8ef4a5f8a34721d625cab0fb849912f467b6 (pre-registration) · implementation 285e5d7 · pilots/configurations d0231fa · results and reports: see `RESULTS_COMMIT.txt` and the final branch head.
**Frozen material unchanged:** `protocol-freeze` 2b7c79e; `e08-confirmation` 4c011a8; test-verified empty diff.

## Reproduce
`cd experiments/E12_h2_synthetic_null_calibration && make test && make production && make analysis` (Python 3.12, about 40 min, synthetic data only).

## Safe for the main paper
- **Figure:** `figures/e12_null_rejection_rates` (panel a: Q1 calibration; panel b: N2b and N1b).
- **Table:** Q1 rejection rates with Wilson intervals (report section 5.1), and the N2b row with both alternatives (section 5.2).
- **One sentence on power and one on falsification** (report section 8).

## Supplementary information
`figures/e12_null_pvalue_cdf_and_D`; `figures/e12_power`; the full Q3 table including the lag-3 failure; the B1 baseline table; DEVIATIONS D1-D5; the pilot curves (`results/pilot_*.csv`).

## Publication-safe claims
- Under four tested null scenarios the shifted-wind test rejected at 4.6-5.4% (nominal 5%); one (N1a) is formally inconclusive under the pre-registered 0.075 margin.
- Under a constructed seasonal-confounding scenario the whole-period shift rejected at 23.8% (20.3-27.7%); within-season shifts gave 5.2% (3.6-7.5%).
- Injected wind-conditioned coupling with D between 0.07 and 0.20 was always detected; coupling at a 3 h lag was never detected (median D negative).
- An advected shared signal without inter-station methane transport was always detected.
- The wind-reversal contrast suppresses wind-independent lead-lag artefacts that a naive directed-network test flags in 82% of pairs.

## Explicit negative findings
- Q2: sensitive (inflated) under seasonal confounding.
- Q3: no power at a 3 h true lag; D >= 0.21 not testable.
- Q4: rejection does not identify methane transport.
- Q1: overall verdict inconclusive under the pre-registered rule (N1a margin).

## Do not claim
- That the 2026 p-value is exact or assumption-free.
- That E12 validates transport, transit times or emissions.
- That E12 changes or re-tests the registered decision.
- That simulated magnitudes give the probability of the observed D = 0.288.

## Unresolved decisions for the researcher
1. Authorise, or not, a post-confirmation exploratory within-season-shift sensitivity on the 2026 data (report section 6.5).
2. Whether to increase the N1a replicate count in a separately labelled follow-up to resolve the margin (this cannot change the pre-registered classification).
3. Merge the branch to `main` (not done; requires your permission).

## Proposed integration into the EMS paper
- **Methods:** a "Validation of the shifted-wind reference" subsection, with the design summary and the pre-registration and deviations.
- **Results:** a short calibration paragraph with the main figure.
- **Discussion:** seasonal exchangeability as the main limitation of the finite-shift p-value; the advected-signal falsification as the reason for the "compatible with transport" wording; the lag-3 blind spot as a design limitation of short-lag weighting, related to but not explaining the E06 kernel shortfall.
