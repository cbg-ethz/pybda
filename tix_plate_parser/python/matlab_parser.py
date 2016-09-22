# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 22/09/16

import os
import scipy.io as spio
import logging
import numpy
from cell_features import CellFeature

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatlabParser:
    def __init__(self, folder, meta):
        self._folder = folder
        self._files = self.find_files(self._folder)
        self._outfile = self._folder + "/matrix.tsv"
        self._meta = meta

    @staticmethod
    def find_files(folder):
        for d, s, f in os.walk(folder):
            for basename in f:
                yield os.path.join(d, basename)

    def parse(self):
        feat = {}
        for f in self._files:
            self.parse_file(feat, f)

    def parse_file(self, feat, f):
        try:
            mat = self.alloc((spio.loadmat(f))["handles"][0][0][0][0][0][0][0][0][0][0])
            # le = str(len(mat))
            # if le not in feat:
            #     feat[le] = []
            # feat[le].append(CellFeature(mat))
        except ValueError or TypeError as e:
            logger.warn("Could not open %s: %s", f, e)

    def alloc(self, arr):
        nrow = len(arr)
        ncol = max((len(x) for x in arr))
        mat = numpy.array
