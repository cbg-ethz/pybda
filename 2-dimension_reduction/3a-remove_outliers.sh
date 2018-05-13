#!/usr/bin/env bash


if [ $# -ne 1 ]
then
  echo -e "Usage: ./$0 spark:master"
  exit
fi

/cluster/home/simondi/spark/bin/spark-submit  \
  --master $1  --num-executors 10 --executor-cores 1 \
  --total-executor-cores 10 \
  3-remove_outliers.py \
  -f /cluster/home/simondi/simondi/data/tix/2-analysis/fa-all_optimal_from_file_feature_dbq_250_cells_100 \
  -o /cluster/home/simondi/simondi/data/tix/2-analysis/outlier_detection-all_optimal_from_file_feature_dbq_250_cells_100
