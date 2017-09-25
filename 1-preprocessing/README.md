# Tix preprocessing

## 0

Extract the maximal feature subsets from all screens and plot them.

* `0-create_maximal_feature_sets.py` creates the feature sets created from 
calling `rnai-parse featuresets`

* `0-plot_featuresets.R` creates plots from the files created during the step
above.

## 1

* `1-plot_normalized_features.R` generates some plots of normalized vs 
unnormalized features after calling `rnai-normalize.py ...`. 