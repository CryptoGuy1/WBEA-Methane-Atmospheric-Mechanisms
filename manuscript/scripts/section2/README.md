# Section 2 figures and tables: reproduction
Descriptive outputs only (no statistical inference). Requires the development panel (`data/dev/`) and sealed confirmation panel (`sealed/e08_panel/`), neither in git (WBEA data are for authorised use only). Python 3.12.3; `pip install -r requirements.txt`.

Run order (from this directory):
```
python prepare_data.py            # daily availability tables, frozen pairs, Natural Earth clips
python make_fig01.py              # Fig. 1 (three map components, 174.5 mm)
python make_fig02_combined.py     # Fig. 2 (combined availability, 174.5 mm)
python make_tables.py             # Tables 1-2 (LaTeX)
cd ../../latex_check && pdflatex manuscript_check.tex && pdflatex manuscript_check.tex && cd -   # CAS check (needs cas-dc.cls in latex_check/)
python validate.py                # 24 automated checks; reads latex_check/manuscript_check.aux for float placement
```
Archived versions: `make_fig01_v1.py`, `make_fig01_v2.py`, `make_fig02_v1.py`, `make_fig02_individual.py` (each writes to its own `archive_*` folder).
