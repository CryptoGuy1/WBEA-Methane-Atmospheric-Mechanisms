# E06 Synthetic injection, detectability and the H2 kernel-shape criterion

**Status:** exploratory (development data). **H2 criterion 3 as pre-registered (D-35): FAILED** (part (ii)). Part (i) met. A post hoc exploratory diagnostic attributes the failure to the reference design, not to the physics; it is not a confirmed explanation.

## Design (D-35)
Real leave-pair-out residual CH4 levels, real missingness, wind shifted by 182 days so that real directional coupling is decorrelated. Idealised advected signals (minute-resolution AR(1), memory 20 or 180 min) delivered to the upstream station and, delayed by tau = d/(3.6|U_par|) and attenuated by 0.8, to the downstream station; hour-averaged; amplitude A = injected first-difference SD / SD(dR_i). Detection: D above the pair's E05 null 95th percentile. 27 pairs x 4 amplitudes x 2 memories x 8 replicates = 1,728 runs. Reference kernels at A = 3 (signal-dominated), 3 replicates per memory. Seed 20261116.

## Results
**Calibration.** At A = 0 no replicate exceeded the threshold (0/432 for each memory) and mean D was -0.005. The E05 per-pair thresholds are conservative for this background, so detection rates below are lower bounds.

**Detectability (pooled over pairs).**
| A | memory 20 min | memory 180 min |
|---|---|---|
| 0.1 | 12% | 12% |
| 0.2 | 44% | 52% |
| 0.4 | 89% | 94% |
Mean injected D at A = 0.4 is 0.17-0.18, against the observed pooled D of 0.128 (E05). Detectability is governed by each pair's null spread, not by distance alone. The closest pairs (AMS 1-9, 1-13) have wide nulls and need A of about 0.4. AMS 5-9 and 2-11 detect A = 0.2 in every replicate. **AMS 1-5 and 5-9 were essentially null in E05 although injected signals at A = 0.2-0.4 are detectable there**, so their nulls are informative rather than a lack of power. AMS 9-23 and 1-23 have low power.

**Kernel shape (aligned hours, 27 pairs pooled).**
| tau bin | observed centroid (h) | range over years | simulated range (A = 3) |
|---|---|---|---|
| 0-0.5 h | 0.25 | 0.21-0.28 | 0.17-0.30 |
| 0.5-1.0 h | 0.39 | 0.27-0.44 | 0.58-0.98 |
| 1.0-1.5 h | 0.73 | 0.49-1.14 | 1.00-1.16 |
| 1.5-2.0 h | 1.11 | 0.47-1.54 | 1.65-1.98 |
| 2.0-3.0 h | 1.51 | 0.77-2.06 | 1.70-2.22 |
(i) The observed centroid increases monotonically with predicted transit (Spearman 1.0): **met**. (ii) It lies inside the simulated range in 1 of 5 bins (required 4): **not met**. Observed lags are shorter than the signal-dominated reference predicts.

## Exploratory diagnostic (post hoc; `exploratory_kernel_diagnostic.py`)
| Simulation | Centroids by bin | SSE vs observed |
|---|---|---|
| A = 0.3, memory 180, 10 m-wind transit (k = 1) | 0.18, 0.34, 0.78, 1.29, 1.30 | **0.086** |
| A = 0.3, memory 20, k = 1 | 0.13, 0.52, 1.02, 1.98, 1.70 | 0.907 |
| A = 3, memory 180, k = 1.25 / 1.5 / 2.0 | - | 0.106 / 0.238 / 0.980 |
| A = 0.3, memory 180, k = 1.25 / 1.5 / 2.0 | - | 0.383 / 0.723 / 1.598 |

At an amplitude matching the observed coupling (A = 0.3) and a slowly varying signal (180 min), simulation with transit times from the 10 m wind reproduces the observed centroids closely. Faster effective transport (k > 1) fits worse at this amplitude. The most likely reason for the failed criterion is that the A = 3 reference was much cleaner than the data. At realistic signal-to-noise, synchronous background covariance and noise pull centroids toward short lags. The results are also consistent with slowly varying, hour-scale concentration fluctuations rather than brief puffs. **This is a post hoc explanation from development data and must be tested independently (D-36).**

## Interpretation
Direction-dependent coupling (E05) is real in this network and its lag structure orders correctly with predicted transit time. The pre-registered quantitative match to a signal-dominated reference failed. [Amended at the integrated review, 2026-11-10: after the continuous-source correction, realistic signal-to-noise explains the short-transit bins only; for tau above about 1.5 h observed lags remain about 25-30% shorter than 10 m-wind transport implies. Original sentence, preserved: "At realistic signal-to-noise the lags are consistent with transport at the 10 m wind speed."] The manuscript must report the failure, the diagnostic and the revised E08 test.

## Limitations
- Injected signals are idealised (frozen-turbulence, single path, fixed attenuation, no dispersion broadening).
- Detection thresholds are borrowed from the E05 real-data null (conservative here).
- A = 0.3 was chosen by matching the observed pooled D, so the diagnostic is calibrated on the same data it explains.

## Figures
Main Figure 7 (`figure07_kernel_shape`, pre-registered A = 3 comparison). Supplementary S2 (`figureS2_detectability`).

## Review corrections (2026-11-10, D-38; `review_corrections.py`, `results/review_*`)
Original results above are unchanged. Two corrections requested at the E06 scientific review:

**1. Wind-conditioned injection.** The original model switches the injected signal on only in the detector's eligible hours. A continuous-source model was added: one AR(1) signal exists at all hours, the station upstream along the pair axis receives it, and the other receives 0.8 x |cos| x the signal delayed by tau (wind speed floored at 0.5 m/s, tau capped at 6 h).

| Detection rate | memory 180, A = 0.2 | memory 180, A = 0.4 | memory 20, A = 0.2 | memory 20, A = 0.4 |
|---|---|---|---|---|
| Original (mask-gated) | 52% | 92% | 43% | 88% |
| Continuous source | 45% | 83% | 23% | 74% |

| Lag centroid (h) by tau bin | 0-0.5 | 0.5-1 | 1-1.5 | 1.5-2 | 2-3 | SSE vs observed |
|---|---|---|---|---|---|---|
| Observed | 0.25 | 0.39 | 0.73 | 1.11 | 1.51 | - |
| Original model, A = 0.3 | 0.17 | 0.34 | 0.81 | 1.30 | 1.27 | 0.108 |
| Continuous source, A = 0.3 | 0.18 | 0.37 | 0.86 | 1.44 | 2.08 | 0.453 |
| Continuous source, A = 3 | 0.39 | 0.72 | 1.33 | 1.76 | 2.50 | 1.896 |

Findings: (a) Mask-gating made the synthetic signal easier to detect and inflated the original detection rates, especially for short-memory signals. The continuous-source rates are the more conservative estimates of detectability. (b) **Unexpected:** the close fit of the post hoc SNR diagnostic depended partly on the gating, which truncates long lags. With a continuous source at realistic amplitude, simulated centroids match the observed ones up to tau of about 1.5 h but exceed them at longer transit (1.44 vs 1.11 h; 2.08 vs 1.51 h). Observed lags for the longer pairs are shorter than 10 m-wind transport implies, by roughly 25-30%. Faster transport above 10 m, plume dispersion and the hourly sampling all remain candidate explanations; the data here cannot separate them. The SNR explanation accounts for the short-transit bins only.

**2. Zero-injection calibration.** The original "0/864" at A = 0 re-evaluated one background (the 182-day wind shift) many times. It is **relabelled a single-background sanity check**, not a false-positive rate. Calibration over 40 distinct no-transport backgrounds (new whole-day wind shifts) gives 42 false detections in 1,080 pair tests, **3.9%** (binomial CI 2.8-5.2%, too narrow because tests within a background are dependent). 23 of 40 backgrounds produced at least one detection; the worst background gave 11%. The E05 thresholds are approximately calibrated at the nominal 5%.
