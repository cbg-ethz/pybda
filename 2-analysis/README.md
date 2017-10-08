## Tix analysis

Check out `pipeline.md`, too.

Does the analysis.


### Clustering

`1-kmeans_spark.py` clusters data generated using `rnai-normalize`. The respective
`1-kmeans_sparl.ipynp` is a trial-and-error script for testing.
 
The input file and output folder should be always the same, for example
 *cells_sample_10_100lines.tsv* as input and some folder *out* as output.
 
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
