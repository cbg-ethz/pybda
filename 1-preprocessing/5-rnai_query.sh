#!/usr/bin/env bash

if [ $# -ne 2 ]
then
  echo -e "Usage: $0 NUM_CELLS FEATURE_DB_FILE"
  exit
fi

reg=".+/(.+).tsv"
[[ $2 =~ $reg ]]
filename="${BASH_REMATCH[1]}"

bsub -o "/cluster/home/simondi/bsub/query_optimal_${1}_${filename}.log" \
     -e "/cluster/home/simondi/bsub/query_optimal_${1}_${filename}.err" \
     -q normal.120h -M 100000 -n1 -R "rusage[mem=100000]" \
     rnai-query compose  --from-file "${2}" --sample "${1}" \
     /cluster/work/bewi/members/simondi/data/tix/database/tix_index.db \
     "/cluster/home/simondi/simondi/data/tix/query_data/all_optimal_from_file_${filename}_cells_${1}.tsv"
