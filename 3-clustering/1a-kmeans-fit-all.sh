#!/usr/bin/env bash


if [ $# -ne 1 ]
then
  echo -e "Usage: ./$0 spark:master"
  exit
fi


for # 10000 7500; # 2 3 4 6 7 8 9 ; #1500 2500 5000 10000 7500; #5 10 15 20 25 30 35 40 50 100 150 200 250 500 1000;
do
  #/cluster/home/simondi/spark/bin/spark-submit  --master $1 --num-executors 10 --executor-cores 1  --total-executor-cores 10 2-kmeans-spark.py -o /cluster/home/simondi/simondi/results/kmeans_test/ -f /cluster/work/bewi/members/simondi/results/kmeans_test/test fit -k ${i}
  /cluster/home/simondi/spark/bin/spark-submit  --master $1 \
   --num-executors 10 --executor-cores 1  --total-executor-cores 10 \
   2-kmeans-spark.py \
   -o /cluster/home/simondi/simondi/results/kmeans_fa \
   -f /cluster/work/bewi/members/simondi/results/kmeans_fa/all_optimal_from_file_feature_dbq_250_cells_100 \
   fit -k ${i}
done
