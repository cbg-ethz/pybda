#!/bin/bash

modls=("pca" "ica"  "kpca" "fa" "iso" "spec")
for m in ${modls[@]}
do
  python ./tix_analyse_pandas.py --model $m
done
