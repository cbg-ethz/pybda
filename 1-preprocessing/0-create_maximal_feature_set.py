#!/usr/bin/env python

import re
import click
import itertools
from functools import reduce


@click.command()
@click.argument("file", type=str)
def run(file):
    """
    Compute screen sets and their feature overlaps on a file computed from
    `rnai-parse featuresets` (features.log).
    """

    sets = _feature_sets(file)
    _max_set(sets)


def _feature_sets(file):
    sets = {}
    with open(file, "r") as fh:
        for line in fh.readlines():
            feature_set = line.strip().split("\t")
            screen, features = feature_set[0].split("#")[1].lower(), \
                               feature_set[1].lower().split(",")
            features = list(filter(lambda x: x.startswith("cell") or
                                        x.startswith("perinuc") or
                                        x.startswith("nucle"),
                              features))
            sets[screen] = sorted(features)
    return sets


def _max_set(sets):
    run = 1
    screens = list(sets.keys())
    max_set = set.intersection(*(set(sets[key]) for key in screens))
    print("Feature_size\tFeatures\tScreens\tScreen_size\tRemoved")
    print(str(len(max_set)) + "\t" +
          ",".join(max_set) + "\t" +
          ",".join(screens) + "\t" +
          str(len(screens)) + "\t" +
          "")
    while len(screens) > 1:
        run += 1
        remove_screen = ""
        for screen in screens:
            curr_screens = screens.copy()
            curr_screens.remove(screen)
            curr_set = set.intersection(
              *(set(sets[key]) for key in curr_screens))
            if len(curr_set) > len(max_set):
                max_set = curr_set
                remove_screen = screen
        if remove_screen not in screens:
            remove_screen = min([(x, len(sets[x])) for x in screens],
                                key=lambda x: x[1])[0]
        if remove_screen in screens:
            screens.remove(remove_screen)
        print(str(len(max_set)) + "\t" +
              ",".join(max_set) + "\t" +
              ",".join(screens) + "\t" +
              str(len(screens)) + "\t" +
              remove_screen)

if __name__ == '__main__':
    run()
