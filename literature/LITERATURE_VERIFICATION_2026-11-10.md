# Targeted literature verification for the EMS manuscript (2026-11-10)
Full matrix and classification: Claude Doc "EMS Preparation: Literature Verification, Software Package and H1 Diagnostic".
Scope: five targeted web searches plus the nine reference papers. NOT a systematic review; a database search (Scopus/WoS) is required before any priority claim.

## Verified items (from search results)
- Lauvaux T. et al. (2016) JGR Atmospheres 121:5213-5236, doi:10.1002/2015JD024473 - tower-network inversion (INFLUX).
- Balashov N.V. et al. (2020) ACP 20:4545-4559, doi:10.5194/acp-20-4545-2020 - urban CH4, 9 towers, background heterogeneity.
- Miles N.L. et al. (2017) Elementa 5:27, doi:10.1525/elementa.127 - INFLUX enhancements.
- Lopez-Coto I. et al. (NIST NEC testbed, PMC5695685) - network design with WRF-STILT footprints (STILT: Lin et al. 2003, as cited).
- Henry R.C. (2008) Atmospheric Environment 42:358-363 - nonparametric trajectory analysis.
- PSCF: Ashbaugh 1985; Malm 1986 (as cited in Kim et al. 2016, Environ Sci Pollut Res 23:16946).
- Station-network cross-correlation/Granger: Mathematics (MDPI) 2025, 13(15):2468 (northern Thailand PM2.5); arXiv 1911.11508 (UK PM2.5 Granger network); Seong (2021) IEEE Access, doi:10.1109/ACCESS.2021.3080828 (transfer-entropy network).
- Facility continuous monitoring: Daniels, Jia & Hammerling (DLQ framework; ChemRxiv, journal version to verify); MDLQ model, arXiv 2506.03395; Day et al. (2024) Sensors 24(8):2419.
- Surrogate tests: time-shifted surrogates for Granger significance, Entropy 2023, 25:1070; circular-shift practice and caveats (neuroscience; spatial statistics torus shift).

## Classification (summary)
Established: lagged/Granger station dependence; circular/time-shift surrogates; max-T; block bootstrap; wind-conditioned single-receptor methods; Kitagawa; negative-control concept.
Adaptations: whole-day shifts of the wind (conditioning) series; injection-based detectability on real residuals; negative control as next-day stability.
Plausibly distinct (pending systematic search): aligned-minus-reversed lead-lag contrast conditioned on wind reversal with leave-pair-out residuals and transit kernels, used as a confirmatory test.
