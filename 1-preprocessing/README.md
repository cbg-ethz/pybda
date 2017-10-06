# Tix preprocessing


Extract the maximal feature subsets from all screens and plot them.
Mentioned files are found in results or so

* `0-create_maximal_feature_sets.py features.log` creates the feature sets created from 
calling `rnai-parse featuresets`/

* `1-plot_featuresets.R feature_sets_max.tsv` creates plots from the files created during the step
above.
 
* `2-extract_plates_from_screens experiment_meta_file.tsv feature_sets_max.tsv 250` prints ths plates with maximal feature sets.