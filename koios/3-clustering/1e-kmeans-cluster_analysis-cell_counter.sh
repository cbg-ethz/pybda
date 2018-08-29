#!/usr/bin/env bash

function usage()
{
    echo -e "\nUSAGE:\n$0 <folder with clusters> <output file>\n"
    exit 0
}

if [ $# -ne 2 ]
then
    usage
fi

find $1 -name "*cluster_*" -exec wc -l {} \; | tr -s " " "," > $2
