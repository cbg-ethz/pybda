#!/usr/bin/env bash

if [ $# -ne 2 ]
then
  echo -e "Usage: ./$0 INFILE OUTFILE"
  exit
fi

while read line;
do
  rnai-query print --db /Users/simondi/PHD/data/data/target_infect_x/database/tix_index.db --plate ${line} ${2}
done < $1