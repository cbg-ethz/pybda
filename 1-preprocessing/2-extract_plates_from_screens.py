#!/usr/bin/env python

import logging
import re
import click

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
    reg = re.compile("(.*-\w+)\d.*")
    with open(plate_mapping, "r") as fh:
        for l in fh.readlines():
            if l.startswith("PLATENAME"):
                continue
            plate = l.strip().split("\t")[0].lower()
            tokens = plate.split("/")
            try:
                screen = tokens[1] + "-" + reg.match(tokens[3]).group(1)
                if screen not in mapping:
                    mapping[screen] = set()
                mapping[screen].add(plate)
            except AttributeError as e:
                logger.error("Missed {}".format(plate))
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


def _get_screens(feature_sets, size):
    feature_sets_filtered = filter(
      lambda x: x[FEATURE_SIZE] >= size, feature_sets)
    feature_set_best = max(feature_sets_filtered,
                           key=lambda x: x[SCREEN_SIZE])
    screens = feature_set_best[SCREENS].split(",")
    return screens


def plates(plate_mapping_file, feature_set_file, size):
    # screen -> plate mapping
    mapping = _read_mapping(plate_mapping_file)
    # feature set list consisting of feature sets, max size, etc.
    feature_sets = _read_feature_sets(feature_set_file)
    # the screen ids that fit the size criteria
    screens = _get_screens(feature_sets, size)
    # get the respective plates
    plate_set = set()
    for screen in screens:
        if screen not in mapping:
            logger.warning("Coudt not find screen {}".format(screen))
        else:
            plate_set |= set(mapping[screen])
    for plate in sorted(list(plate_set)):
        print(plate)


if __name__ == '__main__':
    run()
