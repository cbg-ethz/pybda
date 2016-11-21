Tix Preprocessor
================

The tix preprocessor combines several subpackages for parsing tix matlab files into a postgres database:

* read a folder of **previouslyy downloaded plates**. The downloaded features will serve as a template for the column names in every database.
I.e.: if for feature group *cells* 300 features are found and for feature group *voronoi cells* 200 features are found, for every `experiment` two tables are created.
One table for *cells* features and one table for *voronoi cells* features. So tables for *perinuclei*, *bacteria*, etc. are NOT created. Thus it is advisable to have at least 50 plates downloaded.

* for every plate that is being parsed, create respective tables given the previous step. Then download and parse the plate into matrices and insert them into a postgreSQL table.

* create indexes on queryable columns.

The result should be that the plates are listed in roughly 300 tables in the database. The tables have indexes so that we can effectively do queries.

### Run

Run the complete thing with:

```sh
python run_all.py ...
```

Run the database subpackage alone so that the feature_groups and features are printed. These can be used to create the databases per hand.

```sh
python run_dbm.py ...
```


