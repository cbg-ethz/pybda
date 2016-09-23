# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 22/09/16

import logging
import numpy
import scipy.io as spio
from .cell_features import CellFeature

from plate_parser.plate_file_sets import PlateFileSets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlateParser:
    """
    Class for parsing a single plate containing matlab files for the features.

    """

    def __init__(self, folder, meta):
        """
        Constructor for PlateParser.

        :param folder: folder containing all the plate data
        :param meta: file containing the sirna-entrez mappings
        """
        self._folder = folder
        self._plate_file_sets = PlateFileSets(self._folder)
        self._meta = meta

    def parse_plate_file_sets(self):
        """
        Parse the PlateFileSets (i.e.: all parsed folders).

        """

        # iterate over the file sets and create matrices
        # every fileset represents a plate
        for platefileset in self._plate_file_sets:
            self._parse_plate_file_set(platefileset)

    def _parse_plate_file_set(self, plate_file_set):
        features = {}
        for plate_file in plate_file_set:
            cf = self._parse_file(plate_file)

    def _parse_file(self, plate_file):
        featurename = plate_file.featurename
        file = plate_file.filename
        mat = None
        try:
            matlab_matrix = (spio.loadmat(file))
            matrix = \
                self._alloc(
                    matlab_matrix["handles"][0][0][0][0][0][0][0][0][0][0],
                    file, featurename)
        except ValueError or TypeError:
            logger.warn("Could not parse: %s", file)
        return matrix

    def _alloc(self, arr, file, featurename):
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
        return CellFeature(mat, nrow, m_ncol, file, rowlens, featurename)
