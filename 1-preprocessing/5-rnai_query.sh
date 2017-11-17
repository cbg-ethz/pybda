#!/usr/bin/env bash

if [ $# -ne 1 ]
then
  echo -e "Usage: ./$0 NUM_CELLS FEATURE_DB_FILE"
  exit
fi

echo -o "~/bsub/query_optimal_${1}_${2}.log" -e "~/bsub/query_optimal_${1}_${2}.err" \
  -q normal.120h -M 100000 -n1 -R "rusage[mem=100000]"
  rnai-query query \
  --db "/cluster/home/simondi/simondi/data/tix/database/tix_index.db" \
  --from-file "/cluster/home/simondi/PROJECTS/tix-util/results/1-preprocessing/0-features/${2}.tsv" \
  --sample "${1}" \
   "/cluster/home/simondi/simondi/data/tix/query_data/all_optimal_from_file_${2}_cells_${1}.tsv"
