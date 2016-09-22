# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 22/09/16

from __future__ import print_function, absolute_import
import argparse


def parse_options(args):
    parser = argparse.ArgumentParser(description='Parse matlab files of genetic perturbation screens.')
    parser.add_argument('-f', type=str, help='input file', required=True, metavar='input-file')
    parser.add_argument('-s', type=str, help='size of graph', required=True, metavar='size')
    opts = parser.parse_args(args)
    return opts.f, opts.s