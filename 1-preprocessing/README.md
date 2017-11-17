## Tix feature preprocessing

Check out `pipeline.md`, too.


Mentioned files are found in the `results/1-preprocessing/0-features/current_analysis` folder.
The entry to this part is `featuresets_feature_files.tsv` which been created using `rnai-parse featuresets`.

Create the feature sets created from calling `rnai-parse featuresets` (from terminal):
```bash
  0-create_maximal_feature_sets.py featuresets_feature_files.tsv > feature_sets_max.tsv
```

Create plots (`feature_overlap.eps` and `feature_histogram.eps`) from the files created during the step (from terminal).
```bash
  ./1-plot_featuresets.R
```

Print the plates with maximal feature sets (from terminal):
```bash
  2-extract_plates_from_screens experiment_meta_file.tsv feature_sets_max.tsv 100 > feature_plates_and_screens_100.tsv

  2-extract_plates_from_screens experiment_meta_file.tsv feature_sets_max.tsv 250 > feature_plates_and_screens_250.tsv

  2-extract_plates_from_screens experiment_meta_file.tsv feature_sets_max.tsv 500 > feature_plates_and_screens_500.tsv
```

The alternate file ending with `txt` has been created using `tr '\n' ','` (if this file is available at all).

Parses the file created above (from terminal):
```bash
  3-plate_names.awk feature_plates_and_screens_x.tsv > feature_plate_names_x.tsv
```

Query the database and write result to file (since the API does not work with such a large plate list, from terminal):
```bash
  4-get_file_sets_from_db.sh feature_plate_names_x.tsv  feature_database_query_x.tsv
```

The last file (`feature_database_query.tsv`) can be used with `rnai-query` to get the data from the database (from *leonhard*):
```bash
  5-rnai_query.sh NUM_CELLS
```
This also normalizes the data which are now ready for use.
