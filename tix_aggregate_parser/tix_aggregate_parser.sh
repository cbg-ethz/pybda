#!/usr/bin/env bash

LNK=`greadlink -f $0`
CMD=`basename $0`
CMD=${CMD%.sh}
FLPTH=`dirname $LNK`
PTH="/Users/simondi/PHD/data/data/target_infect_x/aggregates"
CSVS=`find $PTH -name "*csv"`
SCRPT="${FLPTH}/${CMD}.awk"

if [ ! -e $SCRPT ]
then
  echo "There is no script: $SCRIPT"
  exit
fi
echo $CMD

