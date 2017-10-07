## Tix preprocessing

Check out `pipeline.md`, too.

Extract the maximal feature subsets from all screens and plot them.
Mentioned files are found in the `results` folder.


The entry to this part is `features.log` which been created using `rnai-parse featuresets`.
Some manual processing has been to, e.g., to create the file `feature_overlap.tsv` (see `result` folder).

Create the feature sets created from calling `rnai-parse featuresets` 
```bash
  0-create_maximal_feature_sets.py features.log >  feature_sets_max.tsv
```

Create plots (`feature_overlap.eps` and `feature_histogram.eps`) from the files created during the step
```bash
  Rscript 1-plot_featuresets.R
```
 
Print ths plates with maximal feature sets:
```bash
  2-extract_plates_from_screens experiment_meta_file.tsv feature_sets_max.tsv 250 > feature_plates_and_screens.tsv
```
The alternate file ending with `txt` has been created using `tr '\n' ','`.

Parses the file created above:
```bash
  3-plate_names.awk feature_plates_and_screens.tsv > feature_plate_names.tsv
```

Query the database and write result to file (since the API does not work with such a large plate list)
```bash
  4-get_file_sets_from_db.sh feature_plate_names.tsv feature_database_query.tsv
```