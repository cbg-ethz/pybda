# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'

from __future__ import print_function, absolute_import
import sys
import argparse
import re


def parse_options(args):
    parser = argparse.ArgumentParser(description='Beautify a parsed aggregate file from the TIX data.')
    parser.add_argument('-f', type=str, help='input file', required=True, metavar='input-file')
    opts = parser.parse_args(args)
    return opts.f


def parse_table(fl):
    print("barcode\tpathogen\tgeneset\treplicate\tlibrary\trow\tcol\twell\twelltype\tgenesymbol\tsirna")
    with open(fl) as f:
        f.readline()
        for line in f.readlines():
            toks = line.strip().lower().split("\t")
            barcode = toks[0]
            pathogen = re.sub("-.+$", "", toks[2])
            geneset = toks[3]
            rep, library, row, col = toks[4:8]
            well = row + str(col)
            welltype, gene,sirna = toks[8:11]
            print("\t".join([barcode, pathogen, geneset, rep, library, row, col, well, welltype, gene, sirna]))


def main(args):
    fl = parse_options(args[1:])
    parse_table(fl)

if __name__ == "__main__":
    main(sys.argv)
