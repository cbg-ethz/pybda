#!/usr/bin/env bash


if [[ uname == "Linux" ]];
then
   FL=$(readlink -f $0)
else
   FL=$(greadlink -f $0)
fi

DIR=$(dirname ${FL})

cd $DIR
cd ..

snakemake --dag -s biospark.snake --configfile biospark-local.config > "fig/snakeflow.dot"
python "${DIR}/parse_dag.py"  "fig/snakeflow.dot" > "fig/snakeflow.tsv"

dot -Tpdf "fig/snakeflow.tsv" -o "fig/snakeflow.pdf"
dot -Tsvg "fig/snakeflow.tsv" -o "fig/snakeflow.svg"