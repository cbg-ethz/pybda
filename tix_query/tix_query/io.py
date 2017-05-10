# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 08.05.17


import sys


class IO:
    def __init__(self, filename=None):
        self._filename = filename

    def __enter__(self, fh=None):
        if self._filename:
            self._fh = open(self._filename, 'w')
        else:
            self._fh = sys.stdout
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._fh is not sys.stdout:
            self._fh.close()

    def print(self, line):
        self._fh.write(line)

