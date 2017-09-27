# Tix preprocessing


## 1

`1-kmeans_spark.py` clusters data generated using `rnai-normalize`.
 
The input file and output folder should be always the same, for example
 *cells_sample_10_100lines.tsv* as input and some folder *out* as output.
 
First run the script using `fit` on a couple of different cluster centers`k`s, 
then plot the results to determine how many cluster centers you need and 
finally transform the data with the respective `k`.

The job has been submitted locally using
 
```bash
  spark-submit --master "local[*]" --driver-memory 3G --executor-memory 6G 1-kmeans_spark.py 
```