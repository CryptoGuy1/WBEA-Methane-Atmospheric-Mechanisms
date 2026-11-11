# Section 2 figures and tables: reproduction
Descriptive outputs only (no statistical inference). Run from this directory with the repository's development panel (`data/dev/`) and sealed confirmation panel (`sealed/e08_panel/`) present (neither is in git; WBEA data are for authorised use only).
```
pip install -r requirements.txt          # Python 3.12.3
python prepare_data.py                   # needs Natural Earth geojson in /home/claude/gis (see GIS_SOURCES.md) to rebuild clips
python make_fig01.py
python make_fig02.py
python make_tables.py
python validate.py                       # 15 automated checks; non-zero exit on failure
```
Outputs: `manuscript/figures/section2/`, `manuscript/tables/section2/`, processed data and the validation report in `manuscript/data/section2/`.
