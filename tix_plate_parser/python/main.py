# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 22/09/16

from __future__ import print_function, absolute_import

import argparse
import sys

from plate_parser.plate_parser import PlateParser


def parse_options(args):
    parser = argparse.ArgumentParser(description='Parse matlab files of genetic perturbation screens.')
    parser.add_argument('-f',
                        type=str,
                        help='input folder, e.g. BRUCELLA-AU-CV3/VZ001-2H',
                        required=True,
                        metavar='input-folder')
    parser.add_argument('-m',
                        type=str,
                        help='meta file, e.g. target_infect_x_library_layouts_beautified.tsv',
                        required=True,
                        metavar='meta-file')
    opts = parser.parse_args(args)
    return opts.f, opts.m


def main(args):
    fold, meta = parse_options(args)
    parser = PlateParser(fold, meta)
    parser.parse_plate_file_sets()


if __name__ == "__main__":
    main(sys.argv[1:])
