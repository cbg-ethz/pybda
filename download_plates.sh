#!/usr/bin/env bash

BEE="/Users/simondi/PROJECTS/target_infect_x_project/src/tix_mario/openBIS/Tools/BeeDataSetDownloader/BeeDataSetDownloader.sh"
SAMPLER="/Users/simondi/PROJECTS/target_infect_x_project/src/tix_util/sample_plates.py"
META="/Users/simondi/PHD/data/data/target_infect_x/experiment_meta_files/experiment_meta_file.tsv"

for i in `python $SAMPLER $META`; do
 $BEE --user "simon.dirmeier@bsse.ethz.ch"   --password "@wesc4213"   --outputdir ~/PHD/data/data/target_infect_x/screening_data   --plateid $i --files ".*.mat" --verbose "6" --newest;
done
