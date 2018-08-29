#!/usr/bin/env bash

LNK=`greadlink -f $0`
CMD=`basename $0`
CMD=${CMD%.sh}
FLPTH=`dirname $LNK`
PTH="/Users/simondi/PHD/data/data/target_infect_x/aggregates"
CSVS=`find $PTH -name "*csv"`

for csv in $CSVS
do
  echo "Doing $csv"
  OUTFL="${csv%.csv}_parsed.tsv"
  cut -f1,8,9,12,13,14,15,16,18,27,29 $csv > $OUTFL
done


TSVS=`find $PTH -name "*parsed.tsv"`
OUTF="${PTH}/target_infect_x_library_layouts.tsv"
echo "Outfile: ${OUTF}"
if [ -e $OUTF ]
then
  rm $OUTF
fi
touch $OUTF
C=1
for tsv in $TSVS
do
  if [ $C == 1 ]
  then
    head -n1 $tsv > $OUTF
    C==2
  fi
  IFS=' ' read -ra CLS <<<  `head -n 1 ${tsv} | wc | tr -s " "`
  echo "Column count $tsv: ${CLS[1]}"
  echo `head -n 1 ${tsv}`
  echo ""
  awk "{if (NR != 1) print; }" $tsv >> $OUTF
done


