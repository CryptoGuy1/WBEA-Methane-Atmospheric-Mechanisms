#!/bin/bash
# Production run (EXPERIMENT_PLAN.md section 6 + DEVIATIONS D3/D4). Logs to results/production_log.txt
set -e; cd "$(dirname "$0")"; L=results/production_log.txt; echo "start $(date -u +%FT%TZ)" >> $L
for s in N0 N1a N2a N3 N2b; do python3 run_e12.py --scenario $s --reps 500 --out results/raw_$s.csv; echo "$s done $(date -u +%FT%TZ)" >> $L; done
python3 run_e12.py --scenario N1b --reps 200 --out results/raw_N1b.csv; echo "N1b done $(date -u +%FT%TZ)" >> $L
for s in P1_t007 P1_t013 P1_ceiling P1_L2 P1_L3 P1T_t013 P1T_ceiling; do python3 run_e12.py --scenario $s --reps 200 --out results/raw_$s.csv; echo "$s done $(date -u +%FT%TZ)" >> $L; done
echo "end $(date -u +%FT%TZ)" >> $L
