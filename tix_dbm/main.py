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
__PRINT__ = "print"


def parse_options(args):
    parser = argparse.ArgumentParser(
        description='Create/query the TIX data-base.')
    subparsers = parser.add_subparsers(
        help='choose whether to create a database or query from it',
        dest='{create, query}')
    subparsers.required = True
    create_parser = subparsers.add_parser(
        'create', help='Create database instances.')
    create_parser.set_defaults(which=__CREATE__)
    create_parser.add_argument(
        '-f', type=str, required=True, metavar='result-summary-folder',
        help='folder that contains the screening files (NOT the file), e.g.: '
             '/my/path/screening_data/INFECTX')
    create_parser.add_argument('-u', type=str,
                               help='user name for database connection',
                               required=True, metavar='username')
    create_parser.add_argument('-p', type=str,
                               help='password for database connection',
                               required=True, metavar='password')
    create_group = create_parser.add_mutually_exclusive_group(required=True)
    create_group.add_argument('--mysql', help='use a mySQL database',
                              action='store_true')
    create_group.add_argument('--cassandra', help='use a Cassandra database',
                              action='store_true')

    query_parser = subparsers.add_parser(
        'print', help='Print the create statements for the data-bases.')
    query_parser.set_defaults(which=__PRINT__)
    query_parser.add_argument(
        '-f', type=str, required=True, metavar='result-summary-folder',
        help='folder that contains the screening files (NOT the file), e.g.: '
             '/my/path/screening_data/INFECTX')
    create_group_2 = query_parser.add_mutually_exclusive_group(required=True)
    create_group_2.add_argument(
        '--mysql', help='print statements for a mySQL database',
        action='store_true')
    create_group_2.add_argument(
        '--cassandra', help='print statements for a Cassandra database',
        action='store_true')

    opts = parser.parse_args(args)
    return opts


def main(args):
    opts = parse_options(args)
    if opts.which == __CREATE__:
        Controller(opts.u, opts.p, opts.cassandra).create(opts.f)
    else:
        Controller(use_cassandra=opts.cassandra).print(opts.f)


if __name__ == "__main__":
    main(sys.argv[1:])
