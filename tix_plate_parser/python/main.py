################################################################################
# Main file for plate_parser. Takes a folder of matlab files as input and
# converts every plate to a file in vsc format, where every line is ONE
# single cell.
#
# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 22/09/16
################################################################################

from __future__ import print_function, absolute_import

import argparse
import sys

from plate_parser.experiment_meta import ExperimentMeta
from plate_parser.plate_layout import LayoutMeta
from plate_parser.plate_loader import PlateLoader
from plate_parser.plate_parser import PlateParser


def parse_options(args):
    parser = argparse.ArgumentParser(
        description='Parse matlab files of genetic perturbation screens.')
    parser.add_argument('-m',
                        type=str,
                        help='tix layout meta file, e.g. '
                             'target_infect_x_library_layouts_beautified.tsv',
                        required=True,
                        metavar='layout-meta-file')
    parser.add_argument('-e',
                        type=str,
                        help='experiment meta file, e.g. '
                             'experiment_meta_file.tsv',
                        required=True,
                        metavar='experiment-meta-file')
    parser.add_argument('-u',
                        type=str,
                        help='open-bis user name',
                        required=True,
                        metavar='user-name')
    parser.add_argument('-p',
                        type=str,
                        help='open-bis password',
                        required=True,
                        metavar='password')
    parser.add_argument('-b',
                        type=str,
                        help='bee-executable, e.g. BeeDataSetDownloader.sh',
                        required=True,
                        metavar='bee-exe')
    opts = parser.parse_args(args)
    return opts.m, opts.e, opts.u, opts.p, opts.b.


def main(args):
    fold, meta, exm = parse_options(args)
    expmeta = ExperimentMeta(exm, ".*\/\w+\-\w[P|U]\-[G|K]\d+\/.*".lower())
    downloader = PlateLoader()
    #layout = LayoutMeta(meta)
    # create plate parser object and parse the single plates
    parser = PlateParser(fold, expmeta, None)
    parser.parse()


if __name__ == "__main__":
    main(sys.argv[1:])
