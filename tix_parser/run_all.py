# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 22/09/16


from __future__ import print_function, absolute_import

import argparse
import sys
import logging

from tix_parser import Controller
from tix_parser import Config


def parse_options(args):
    parser = argparse.ArgumentParser(
        description='Parse matlab files of genetic perturbation screens.')
    parser.add_argument('-c',
                        type=str,
                        help='tix config file',
                        required=True,
                        metavar='config')
    opts = parser.parse_args(args)
    return opts.c


def main(args):
    c = Config(parse_options(args))
    logging.basicConfig(level=logging.INFO,
                        format='[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')
    # create plate parser object and parse the single plates
    Controller(c).parse()


if __name__ == "__main__":
    main(sys.argv[1:])
