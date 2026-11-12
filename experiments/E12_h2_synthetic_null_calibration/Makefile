# E12 reproduction (run from this directory; repository root must be two levels up)
test:
	cd ../.. && python3 -m pytest -q experiments/E12_h2_synthetic_null_calibration/tests
pilots:
	python3 pilot_p1_amplitudes.py && python3 pilot_p1t_amplitudes.py
production:
	rm -f results/raw_*.csv results/production_log.txt && ./run_all.sh
analysis:
	python3 analyze_e12.py
all: test production analysis
