#!/usr/bin/env bash

if [ $# -ne 1 ]
then
  echo -e "Usage: ./$0 NUM_CELLS"
  exit
fi

bsub -o ~/bsub/query_optimal_${1}.log -e ~/bsub/query_optimal_${1}.err -q normal.120h -M 200000 -n1 -R "rusage[mem=200000]" rnai-query query --db ~/simondi/data/tix/database/tix_index.db --from-file /cluster/home/simondi/PROJECTS/tix-util/results/1-preprocessing/0-features/feature_database_query.tsv --sample ${1}  ~/simondi/data/tix/query_data/all_optimal_set_${1}.tsv
