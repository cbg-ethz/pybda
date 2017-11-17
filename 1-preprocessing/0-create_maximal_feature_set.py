#!/usr/bin/env python

import click
import logging

logging.basicConfig(
  format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

logger = logging.getLogger(__name__)


@click.command()
@click.argument("file", type=str)
@click.argument("outfile", type=str)
def run(file, outfile):
    """
    Compute screen sets and their feature overlaps on a file computed from the
    FILE generatated from `rnai-parse featuresets` and write to OUTFILE.
    """

    _max_set(_feature_sets(file), outfile)


def _feature_sets(file):
    sets = {}
    not_matched = set()
    with open(file, "r") as fh:
        for line in fh.readlines():
            feature_set = line.rstrip().split("\t")
            try:
                plate, features = feature_set[0].split("#")[1].lower(), \
                                  feature_set[1].lower().split(",")
                features = list(
                  filter(lambda x: x.startswith("cell") or
                                   x.startswith("perinuc") or
                                   x.startswith("nucle"), features))
                sets[plate] = sorted(features)
            except IndexError:
                not_matched.add(feature_set[0])
    if len(not_matched):
        logger.warning("Could not match the following files:\n\t {}"
                       .format("\n\t".join(sorted(list(not_matched)))))

    return sets


def _max_set(sets, out):
    run = 1
    plates = list(sets.keys())
    max_set = set.intersection(*(set(sets[key]) for key in plates))
    with open(out, "w") as of:
        of.write("Feature_size\tFeatures\tScreens\tScreen_size\tRemoved\n")
        of.write(str(len(max_set)) + "\t" +
              ",".join(max_set) + "\t" +
              ",".join(plates) + "\t" +
              str(len(plates)) + "\t" +
              "\n")
        while len(plates) > 1:
            run += 1
            remove_screen = ""
            for screen in plates:
                curr_screens = plates.copy()
                curr_screens.remove(screen)
                curr_set = set.intersection(
                  *(set(sets[key]) for key in curr_screens))
                if len(curr_set) > len(max_set):
                    max_set = curr_set
                    remove_screen = screen
            if remove_screen not in plates:
                remove_screen = min([(x, len(sets[x])) for x in plates],
                                    key=lambda x: x[1])[0]
            if remove_screen in plates:
                plates.remove(remove_screen)
                of.write(str(len(max_set)) + "\t" +
                  ",".join(max_set) + "\t" +
                  ",".join(plates) + "\t" +
                  str(len(plates)) + "\t" +
                  remove_screen + "\n")


if __name__ == '__main__':
    run()
