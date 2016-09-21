# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'

from __future__ import print_function, absolute_import
import sys
import argparse


def parse_options(args):
    parser = argparse.ArgumentParser(description='Beautify a parsed aggregate file from the TIX data.')
    parser.add_argument('-f', type=str, help='input file', required=True, metavar='input-file')
    opts = parser.parse_args(args)
    return opts.f


def parse_table(fl):
    with open(fl) as f:
        for line in f.readlines():
            print(line)


def main(args):
    fl = parse_options(args[1:])
    parse_table(fl)

if __name__ == "__main__":
    main(sys.argv)
