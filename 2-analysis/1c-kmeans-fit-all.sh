#!/usr/bin/env bash


if [ $# -ne 1 ]
then
  echo -e "Usage: ./$0 spark:master"
  exit
fi


for i in {16..30};
do
  /cluster/home/simondi/spark/bin/spark-submit  --master $1 --num-executors 10 --executor-cores 1  --total-executor-cores 10 1-kmeans_spark.py -o /cluster/home/simondi/simondi/results/kmeans_all_no_vac_100 -f /cluster/work/bewi/members/simondi/data/tix/query_data/all_no_vac_100_cells.tsv  fit -k ${i}
done
