#!/usr/bin/env python
from functools import reduce

import click

FEATURE_SIZE = "feature_size"
SCREEN_SIZE = "screen_size"
SCREENS = "screens"


@click.command()
@click.argument("plate-mapping", type=str)
@click.argument("feature-sets", type=str)
@click.argument("size", type=int)
def run(plate_mapping, feature_sets, size):
    """
    Print the plates for specific screeps for a given feature set size.\n
    PLATE-MAPPING is a file that maps plates to their screens (experiment_meta_file.tsv).
    FEATURE-SETS is the result from `0-create_maximal_feature_sets.py` (feature_sets_max.tsv).
    SIZE is the number of features for all screens.
    """

    plates(plate_mapping, feature_sets, size)


def _read_mapping(plate_mapping):
    mapping = {}
    with open(plate_mapping, "r") as fh:
        for l in fh.readlines():
            if l.startswith("PLATENAME"):
                continue
            plate = l.strip().split("\t")[0].lower()
            screen = plate.split("/")[2]
            if screen not in mapping:
                mapping[screen] = set()
            mapping[screen].add(plate)
    return mapping


def _read_feature_sets(feature_sets):
    fs = []
    with open(feature_sets, "r") as fh:
        for l in fh.readlines():
            if l.startswith("Feature_size"):
                continue
            tokens = l.strip().split("\t")
            fs.append(
              {
                  FEATURE_SIZE: int(tokens[0]),
                  SCREEN_SIZE: int(tokens[3]),
                  SCREENS: tokens[2]
              }
            )

    return fs


def plates(plate_mapping, feature_sets, size):
    mapping = _read_mapping(plate_mapping)
    feature_sets = _read_feature_sets(feature_sets)
    sets = max(
      filter(lambda x: x[FEATURE_SIZE] >= size, feature_sets),
      key=lambda x: x[SCREEN_SIZE]
    )
    screens = sets[SCREENS].split(",")
    print(sets)


if __name__ == '__main__':
    run()
