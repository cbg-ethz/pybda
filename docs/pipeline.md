# TargetInfectX data analysis

This document describes the steps taken for the data analysis of the *TargetInfectX* project.

## Parsing

We first downloaded the complete data-set using the `BeeDataDownloader`.
Subsequently we do some preprocessing using our in-house python tool `rnaitutilities`.

First we check for the correct number of downloads:

```bash
  rnai-parse checkdownload /cluster/home/simondi/PROJECTS/config_leonhard.yml
```

This should give some files that are **not** downloaded. These are indeed **empty on the openBIS instance**.

Afterwards we parse the files using:

```bash
  rnai-parse parse /cluster/home/simondi/PROJECTS/config_leonhard.yml
```

Having parsed all files, we can check fif everything went as expected by creating a download report:

```bash
  rnai-parse report /cluster/home/simondi/PROJECTS/config_leonhard.yml
```

Furthermore, to see which feature-sets make most sense to take, we can compute pairwise Jaccard indexes between the feature sets using:

```bash
  rnai-parse featuresets /cluster/home/simondi/PROJECTS/config_leonhard.yml
```

## Preprocessing

Next the parsed data's meta information are stored in a indexed data-based in
order to quickly retrieve plate information. The mentioned files are found in the 
`results/1-preprocessing/0-features/current_analysis` folder. 
The entry to this part is `featuresets_feature_files.tsv` which been created using `rnai-parse featuresets`.
 
First we created a index for the complete data-set using `sqlite`.  
```bash
  rnai-query insert 
             --db /cluster/home/simondi/simondi/data/tix/database/tix_index.db 
             /cluster/home/simondi/simondi/data/tix/screening_data
``` 

Then create the feature sets created from calling `rnai-parse featuresets` (from terminal):
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

Parse the file created above (from terminal):
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

**This creates the data also normalizes them which are now ready for use.**

## Analysis

### Clustering

`1-kmeans_spark.py` clusters data generated using `rnai-query`. The respective
`1-kmeans_spark.ipynp` is a trial-and-error script for testing.
The input file and output folder should be always the same, for example *cells_sample_10_100lines.tsv* as input and some folder *out* as output.
 
First run the script using `fit` on a couple of different cluster centers`k`s, 
then plot the results to determine how many cluster centers you need and 
finally transform the data with the respective `k`.

The clustering can be done like this locally:
```bash
  for i in {2..15};
  do
    spark-submit --master "local[*]" --driver-memory 3G --executor-memory 6G 
                 1-kmeans_spark.py 
                 -o ~/Desktop/test_ba 
                 -f ../cells_sample_10_normalized_cut_100.tsv 
                 fit -k ${i}
  done
               
 spark-submit --master "local[*]" --driver-memory 3G --executor-memory 6G 
              1-kmeans_spark.py 
              -o ~/Desktop/test_ba 
              -f ../cells_sample_10_normalized_cut_100.tsv 
              plot
               
  spark-submit --master "local[*]" --driver-memory 3G --executor-memory 6G 
               1-kmeans_spark.py 
               -o ~/Desktop/test_ba 
               -f ../cells_sample_10_normalized_cut_100.tsv 
               transform -k BEST_K_FROM_PLOT
```

**Note that mpi and java needs to be loaded on every shell session.** The job is submitted on a grid using:
```bash
  module load jdk/8u92
  module load openmpi/2.1.0
  
  ./1a-start_cluster.sh
  ./1b-launch_cluster.sh
  
  # get master
  sparkcluster info
   
  ./1c-kmeans-fit.py spark:master K
  ./1d-kmeans-plot.py spark:master
  ./1e-kmeans-transform.py spark:master K
  ./1f-kmeans-statistics.py spark:master K
```
