 Parse a plate generated from a screen into a csv.

This package is for database management stuff. It takes a folder of screening files and creates data-base statements for creating and querying the db.

```sh
python main.py ...
```
This only sets up the respective data-bases for mySQL. One is a meta database with relevant information, the other databases contain the real data.
Sooner or later this has to be converted to cassandra (better sooner).
