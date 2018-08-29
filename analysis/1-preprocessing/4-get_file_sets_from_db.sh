#!/usr/bin/env bash

if [ $# -ne 2 ]
then
  echo -e "Usage: ./$0 INFILE OUTFILE"
  exit
fi

while read line;
do
  rnai-query query \
    --plate ${line}
    /Users/simondi/PHD/data/data/target_infect_x/database/tix_index.db \
    ${2}
done < $1
