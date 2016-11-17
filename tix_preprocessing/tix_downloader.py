################################################################################
# Main file for downloader.
#
# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 14/11/16
################################################################################

import fileinput


if __name__ == "__main__":
    for line in fileinput.input():
        print(line)
