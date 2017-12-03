#!/usr/bin/env bash


if [ $# -ne 1 ]
then
  echo -e "Usage: ./$0 spark:master"
  exit
fi


/cluster/home/simondi/spark/bin/spark-submit  --master $1  --num-executors 10 --executor-cores 1 --total-executor-cores 10 1-factor_analysis-spark.py -o /cluster/home/simondi/simondi/results/kmeans_test/test -f /cluster/work/bewi/members/simondi/data/tix/query_data/all_test.tsv
#/cluster/home/simondi/spark/bin/spark-submit  --master $1  --num-executors 10 --executor-cores 1 --total-executor-cores 10 01-fa_spark.py -o /cluster/home/simondi/simondi/results/kmeans_fa/all_optimal_from_file_feature_dbq_250_cells_100 -f /cluster/work/bewi/members/simondi/data/tix/query_data/all_optimal_from_file_feature_dbq_250_cells_100.tsv
