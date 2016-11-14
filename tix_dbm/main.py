################################################################################
# Main file for dbm.
#
# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 14/11/16
################################################################################

from __future__ import print_function, absolute_import

import argparse
import sys

from dbm import Controller

__CREATE__ = "create"
__QUERY__ = "query"


def parse_options(args):
    parser = argparse.ArgumentParser(
        description='Create/query the TIX data-base.')
    subparsers = parser.add_subparsers(help='help for subcommand')
    creat_parser = subparsers.add_parser(
        'create', help='Create a database-instance.')
    creat_parser.set_defaults(which=__CREATE__)
    creat_parser.add_argument(
        '-f', type=str, required=True, metavar='result-summary-folder',
        help='folder that contains the screening files (NOT the file), e.g.: '
             '/my/path/screening_data/INFECTX')
    query_parser = subparsers.add_parser(
        'query', help='Query an existing data-base instance.')
    query_parser.set_defaults(which=__QUERY__)
    query_parser.add_argument('--query', help='to do')
    opts = parser.parse_args(args)
    return opts


def main(args):
    opts = parse_options(args)
    if opts.which == __CREATE__:
        Controller().create(opts.f)
    else:
        Controller().query(opts.query)


if __name__ == "__main__":
    main(sys.argv[1:])
