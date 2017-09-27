# TargetInfectX data analysis

This document describes the steps taken for the data analysis of the *TargetInfectX* project.

## Parsing

We first downloaded the complete data-set using the `BeeDataDownloader`. Subsequently we do some preprocessing using our in-house python tool `rnaitutilities`.

First we check for the correct number of downloads:

```python 
  rnai-parse checkdownload /cluster/home/simondi/PROJECTS/config_leonhard.yml
```

This should give some files that are **not** downloaded. These are indeed **empty on the openBIS instance**.

Afterwards we parse the files using:

```python
  rnai-parse parse /cluster/home/simondi/PROJECTS/config_leonhard.yml
```

Having parsed all files, we can check fif everything went as expected by creating a download report:

```python
  rnai-parse report /cluster/home/simondi/PROJECTS/config_leonhard.yml
```

Furthermore, to see which feature-sets make most sense to take, we can compute pairwise Jaccard indexes between the feature sets using:

```python
  rnai-parse featuresets /cluster/home/simondi/PROJECTS/config_leonhard.yml
```

We can have a look at the feature sets using scripts in `1-preprocessing`, 
such as:

```bash
  0-create_maximal_feature_sets.R ...
  0-plot_featuresets.R ...
```
which will create plots and data for which features/screens we should use best.
**NOTE**: I manually modified the output from `rnai-parse featuresets` to 
load it into `R`.

For this analysis we decided to use different combinates the following 
plates:

* all quiagen plates (different features)
* all bartonella plates (has invasomes)
* brucella-qu-g1-h28[123]-13 (missing online)
* salmonella-dp-g1-dz{01-57}-2e (missing online)


## Preprocessing

Next the parsed data's meta information are stored in a indexed data-based in
order to quickly retrieve plate information.
  
```bash
  rnai-query insert 
   --db /cluster/home/simondi/simondi/data/tix/database/tix_index.db 
   /cluster/home/simondi/simondi/data/tix/screening_data
``` 

From this we can readily query data to receive a final data-set:

```bash
  rnai-query query 
   --db ../database/tix_index.db 
   /cluster/home/simondi/simondi/data/tix/query_data/all.tsv
```
   
We created data-sets using the following queries:

* all data, no filtering,
* no quiagen libraries,
* some others.

Having the data, we still need to normalize it, which we do using Spark:

```bash
  rnai-normalize /cluster/home/simondi/simondi/data/tix/query_data/all.tsv
```

You can check the distributions of the normalized data with:

```bash
  1-plot_normalized_features.R
```

This computes the `z-score` over all plates.

## Analysis

The first step of the analysis is clustering of single cells using

```bash
    1-kmeans_spark.py 
```

The input file and output folder should be always the same, for example
 *cells_sample_10_100lines.tsv* as input and some folder *out* as output.
 
First run the script using `fit` on a couple of different cluster centers`k`s, 
then plot the results to determine how many cluster centers you need and 
finally transform the data with the respective `k`.

The job has been submitted locally using:
 
```bash
  spark-submit --master "local[*]" --driver-memory 3G --executor-memory 6G 1-kmeans_spark.py 
```

The job has been submitted on Leonhard using:


```bash

```