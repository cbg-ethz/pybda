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
    Class for parsing a folder of plates containing matlab files for the
    features.

    """

    def __init__(self, folder, meta):
        """
        Constructor for PlateParser.

        :param folder: folder containing all the plate data
        :param meta: file containing the sirna-entrez mappings
        """

        self._folder = folder
        # parse the folder into a map of (classifier-plate) pairs
        self._plate_file_sets = PlateFileSets(self._folder)
        self._meta = meta

    def parse_plate_file_sets(self):
        """
        Parse the PlateFileSets (i.e.: all parsed folders) into tsvs.

        """

        # iterate over the file sets and create matrices
        # every platefileset represents a plate
        # so every platefileset is a single file
        for platefileset in self._plate_file_sets:
            self._parse_plate_file_set(platefileset)

    def _parse_plate_file_set(self, plate_file_set):
        # feature map: there is a chance that different features
        # have a different set of cells
        features = {}
        # TODO: here
        print(plate_file_set.classifier, " ", len(plate_file_set))
        for plate_file in plate_file_set:
            cf = self._parse_file(plate_file)
            if cf is None:
                continue
            print("\t", plate_file, " ", cf.max_cells)
            # this is not good
            #self._add(features, cf)

    def _parse_file(self, plate_file):
        """
        Parse a matlab bianry as np.array

        :param plate_file: the matlab file
        :return: returns a 2D np.array
        """
        featurename = plate_file.featurename
        file = plate_file.filename
        matrix = None
        try:
            matlab_matrix = (spio.loadmat(file))
            matrix = \
                self._alloc(
                    matlab_matrix["handles"][0][0][0][0][0][0][0][0][0][0],
                    file, featurename)
        except ValueError or TypeError or AssertionError:
            logger.warn("Could not parse: %s", file)
        return matrix

    def _add(self, features, cf):
        """
        Add a cell feature to a feature map

        :param features: the feature map
        :param cf: the cell feature object
        """
        max_cells = str(cf.max_cells)
        if max_cells not in features:
            features[max_cells] = []
        features[max_cells].append(cf)

    def _alloc(self, arr, file, featurename):
        try:
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
        except AssertionError:
            logger.warn("Could not alloc feature %s of %s", featurename, file)
        return None


