#!/usr/bin/env python

import re
import click
import itertools
from functools import reduce

@click.command()
@click.argument("file", type=str)
def run(file):
    sets = _feature_sets(file)
    max_set = _max_set(sets)


def _feature_sets(file):
    sets = {}
    with open(file, "r") as fh:
        for line in fh.readlines():
            feature_set = line.strip().split("\t")
            screen, features = feature_set[0].split("#")[1].lower(), \
                               feature_set[1].lower().split(",")
            sets[screen] = sorted(features)
    return sets


def _max_set(sets):
    screens = list(sets.keys())
    max_set = set.intersection(*(set(sets[key]) for key in screens))
    print(",".join(screens) + "\t" + ",".join(max_set))
    while len(screens) > 1:
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
        print(",".join(screens) + "\t" + str(len(max_set)) + "\t" + ",".join(max_set))


if __name__ == '__main__':
    run()
