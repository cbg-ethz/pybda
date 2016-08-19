#!/usr/bin/env bash

if [ $# -ne 2 ]
then
  echo -e "Usage: ./$0 spark:master K"
  exit
fi

/cluster/home/simondi/spark/bin/spark-submit  --master $1 --num-executors 10 --executor-cores 1  --total-executor-cores 10 2-kmeans-spark.py -o /cluster/home/simondi/simondi/results/kmeans_fa -f /cluster/work/bewi/members/simondi/results/kmeans_fa/all_optimal_from_file_feature_dbq_250_cells_100 transform -k ${2}
