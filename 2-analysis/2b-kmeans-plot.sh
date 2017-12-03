#!/usr/bin/env bash


if [ $# -ne 1 ]
then
  echo -e "Usage: ./$0 spark:master"
  exit
fi

/cluster/home/simondi/spark/bin/spark-submit  --master $1 --num-executors 10 --executor-cores 1  --total-executor-cores 10 2-kmeans-spark.py -o /cluster/home/simondi/simondi/results/kmeans_test/ -f /cluster/work/bewi/members/simondi/results/kmeans_test/test plot
#/cluster/home/simondi/spark/bin/spark-submit  --master $1 --num-executors 10 --executor-cores 1  --total-executor-cores 10 1-kmeans_spark.py -o /cluster/home/simondi/simondi/results/kmeans_final_data -f /cluster/work/bewi/members/simondi/data/tix/query_data/all_optimal_from_file_feature_dbq_250_cells_100.tsv plot
