#!/usr/bin/env bash

./3-get_platesnames.awk $1 | tr "\n" ","
