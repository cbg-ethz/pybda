#!/usr/bin/env bash

sparkcluster start --memory-per-executor 15000 --memory-per-core 15000 --walltime 200:00 --cores-per-executor 1 30 &
