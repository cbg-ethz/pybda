<h1 align="center"> tix utility </h1>

Collection of utiliy scripts and stuff for the TIX data.

#### Aggregate parser

This only takes the aggregate files from the tix wiki (now in ``/Users/simondi/PHD/data/data/target_infect_x/plate_layout_meta_files``)
and parses them

#### Notebooks

Collections of notebooks for the TIX data-analysis (this is not yet needed).

#### DBM (1)

This creates data-base instances for mySQL. Running ```tix_dbm``` will create
one meta data-table and several screening data-tables with the real data.

#### Plate parser (2)

The ``plate parser`` takes a list of files and parses them info the data-base (this should be done in succession to the DBM).
Probably a combination of both makes both sense.

## Author

* Simon Dirmeier <a href="mailto:simon.dirmeier@gmx.de">simon.dirmeier@gmx.de</a>
