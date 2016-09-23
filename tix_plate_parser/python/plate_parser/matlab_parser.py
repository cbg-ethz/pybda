# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 22/09/16

import logging

import numpy
import scipy.io as spio
from cell_features import CellFeature

from plate_parser.file_sets import FileSets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatlabParser:
    """
    Class for parsing a single plate containing matlab files for the features.

    """
    def __init__(self, folder, meta):
        self._folder = folder
        self._file_sets = FileSets(self._folder)
        self._meta = meta

    def parse(self):
        feat = {}
        # for f in self._file_sets:
        #     self.parse_file(feat, f)

    def parse_file(self, feat, f):
        try:
            mat = self.alloc((spio.loadmat(f))["handles"][0][0][0][0][0][0][0][0][0][0], f)
            k = 2
            # le = str(len(mat))
            # if le not in feat:
            #     feat[le] = []
            # feat[le].append(CellFeature(mat))
        except ValueError or TypeError as e:
            logger.warn("Could not open %s: %s", f, e)

    def alloc(self, arr, f):
        # number of images on the plate (usually 9 * 384)
        nrow = len(arr)
        # number of cells per image
        rowlens = [len(x) for x in arr]
        # maximum number of cells
        m_ncol = max(rowlens)
        # initialize empty matrix of NaNs
        mat = numpy.empty(shape=(nrow, m_ncol), dtype="float64") * numpy.nan
        # fill matrix
        for i in range(len(arr)):
            row = arr[i]
            for j in range(len(row)):
                mat[i][j] = row[j]
        return CellFeature(mat, nrow, m_ncol, f, rowlens)

