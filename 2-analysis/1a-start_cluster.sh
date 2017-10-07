#!/usr/bin/env bash

sparkcluster start --memory-per-executor 15000 --memory-per-core 10000 --walltime 24:00 --cores-per-executor 1 10
