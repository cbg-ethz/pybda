#!/usr/bin/env bash


if [ $# -ne 1 ]
then
  echo -e "Usage: ./$0 spark:master"
  exit
fi


for i in 1000 5000 10000;
do
  /cluster/home/simondi/spark/bin/spark-submit  --master $1 --num-executors 10 --executor-cores 1  --total-executor-cores 10 1-kmeans_spark.py -o /cluster/home/simondi/simondi/results/kmeans_final_data -f /cluster/work/bewi/members/simondi/data/tix/query_data/all_optimal_from_file_feature_dbq_250_cells_100.tsv fit -k ${i}
done
