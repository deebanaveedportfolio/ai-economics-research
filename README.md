# AI exposure and early-career employment
Exploratory, AI-assisted research portfolio. Not an Anthropic publication.

## Reproduce
Create a Python environment and install requirements.txt. The supplied aggregate panel permits inspection without distributing licensed person-level CPS records. For raw-data reproduction create inputs/ and obtain IPUMS CPS extract (Basic Monthly 2019–2026, DDI and fixed-width data), Census 2018 occupation crosswalk, O*NET 31.0 MySQL archive, Anthropic job_exposure.csv and task_penetration.csv, and hotel_booking.csv. Use filenames specified in scripts. Obtain source data under their respective terms; do not publish raw IPUMS records. Run validate.py, study.py, event.py, then analyze.py. The latter includes hotel analysis and exploratory task matching not used in the main model. Scripts assume the supplied extract layout and exact archive filenames.

Outputs: monthly validation, age-occupation aggregates, mapping, panel, results, event and figures. The raw-input workflow has not been rerun after path portability edits. The supplied estimates are exploratory, not causal. See paper for coverage and proxy limitations.
