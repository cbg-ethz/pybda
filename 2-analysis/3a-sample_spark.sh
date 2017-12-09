#!/usr/bin/env bash

if [ $# -ne 3 ]
then
  echo -e "Usage: $0 spark:master kmeans_transformed_folder gene1,gene2,gene3"
  exit
fi

/cluster/home/simondi/spark/bin/spark-submit  --master $1 --num-executors 10 --executor-cores 1  --total-executor-cores 10 3-sample_spark.py -f $2 -g $3
