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

snakemake --dag -s koios/koios.snake --configfile koios-usecase.config > "fig/snakeflow.dot"
python "${DIR}/parse_dag.py"  "fig/snakeflow.dot" > "fig/snakeflow.tsv"

dot -Tpdf "_fig/snakeflow.tsv" -o "_fig/snakeflow.pdf"
dot -Tsvg "_fig/snakeflow.tsv" -o "_fig/snakeflow.svg"
cp "_fig/snakeflow.svg" "docs/source/_static/"

