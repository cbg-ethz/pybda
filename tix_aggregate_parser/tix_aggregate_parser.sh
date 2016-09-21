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

for csv in $CSVS
do
  echo "Doing $csv"
  OUTFL="${csv%.csv}_parsed.tsv"
  cut -f1,8,9,12,13,14,15,16,18,27,29 $csv > $OUTFL
done


TSVS=`find $PTH -name "*tsv"`
OUTF="${PTH}/target_infect_x_library_layouts.tsv"
echo "Outfile: ${OUTF}"
touch $OUTF
for tsv in $TSVS
do
  IFS=' ' read -ra CLS <<<  `head -n 1 ${tsv} | wc | tr -s " "`
  echo "Column count $tsv: ${CLS[1]}"
  echo `head -n 1 ${tsv}`
  echo ""
  cat $tsv >> $OUTF
done


