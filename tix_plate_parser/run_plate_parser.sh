#!/usr/bin/env bash

if [[ $# -ne 1 ]];
then
	echo -e "usage:\t$0 <open-bis password for simon dirmeier>"
	exit
fi


LINK=$(greadlink -f $0)
DIR=$(dirname ${LINK})

PATH_PREFIX="/Users/simondi/PHD/data/data/target_infect_x"
SRC_PREFIX="/Users/simondi/PROJECTS/target_infect_x_project"

if [[ $DIR == /home/simondi/tix_util* ]];
then
	PATH_PREFIX="/links/groups/beerenwinkel/simon/data/target_infect_x"
	SRC_PREFIX="/home/simondi/PROJECTS/target_infect_x_project"
fi

EXE="${DIR}/python/main.py"
META="${PATH_PREFIX}/plate_layout_meta_files/target_infect_x_library_layouts_beautified.tsv"
EXPER="${PATH_PREFIX}/experiment_meta_files/experiment_meta_file.tsv"
USER="simon.dirmeier@bsse.ethz.ch"
PASS=$0
DOWNLOADER="${SRC_PREFIX}/tix_mario/openBIS/Tools/BeeDataSetDownloader/BeeDataSetDownloader.sh"
OUTPUT="${PATH_PREFIX}/screening_data/"

if [[ ! -e $EXE ]];
then
	echo "Executable not found!"
	echo $EXE
	exit
fi
if [[ ! -e $META ]];
then
	echo "Meta files have not been found!"
	echo $META
	exit
fi
if [[ ! -e $EXPER ]];
then
	echo "Experiment files have not been found!"
	echo $EXPER
	exit
fi
if [[ ! -e $DOWNLOADER ]];
then
	echo "Downloader has not been found!"
	echo $DOWNLOADER
	exit
fi
if [[ ! -d $OUTPUT ]]; 
then
  echo "Some directory does not exist!"
  echo $OUTPUT
  exit
fi

python $EXE -m $META -e $EXPER -u $USER -p $1 -b $DOWNLOADER -o $OUTPUT