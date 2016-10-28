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

from plate_parser.plate_experiment_meta import PlateExperimentMeta
from plate_parser.plate_layout import PlateLayoutMeta
from plate_parser import PlateParser


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
    parser.add_argument('-o',
                        type=str,
                        help='output folder, i.e. the folder where the stuff '
                             'is downloaded to and parsed to',
                        required=True,
                        metavar='output-folder')
    opts = parser.parse_args(args)
    return opts.m, opts.e, opts.u, opts.p, opts.b, opts.o


def main(args):
    layout_file, experiment_file, user, password, bee_exe, output_folder = \
        parse_options(args)
    # create plate parser object and parse the single plates
    parser = PlateParser(experiment_file, layout_file,
                         bee_exe, output_folder, user,
                         password)
    parser.parse()

if __name__ == "__main__":
    main(sys.argv[1:])
