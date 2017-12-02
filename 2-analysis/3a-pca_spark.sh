#!/usr/bin/env bash

if [ $# -ne 2 ]
then
  echo -e "Usage: ./$0 spark:master kmeans_transformed-folder"
  exit
fi

/cluster/home/simondi/spark/bin/spark-submit  --master $1 --num-executors 10 --executor-cores 1  --total-executor-cores 10 2-pca_spark.py -f ${2}
