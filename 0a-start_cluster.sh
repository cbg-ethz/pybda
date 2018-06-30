#!/usr/bin/env bash

sparkcluster start --memory-per-executor 500000 --memory-per-core 50000 --walltime 200:00 --cores-per-executor 10 2 &
