# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 27/10/16

import logging
import numpy
import scipy.io as spio

from ._plate_cell_features import PlateCellFeature

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_matlab(file):
    """
    Load a matlab file as np array

    :param file: matlab file name
    :return: returns an numpy.array
    """
    matlab_matrix = spio.loadmat(file)
    return matlab_matrix["handles"][0][0][0][0][0][0][0][0][0][0]


def parse_file(plate_file):
    """
    Parse a matlab binary as np.array

    :param plate_file: the matlab file
    :return: returns a 2D np.array
    """
    featurename = plate_file.featurename
    file = plate_file.filename
    if file is None:
        logger.warn("Could not parse: %s", file)
        return None
    matrix = None
    try:
        matrix = \
            _alloc(
                load_matlab(file),
                file, featurename)
    except ValueError or TypeError or AssertionError:
        logger.warn("Could not parse: %s", file)
    return matrix


def _alloc(arr, file, featurename):
    """
    Create a Cell feature object from a matlab binary.

    :param arr: the matrix object
    :param file: the filename of the matlab binary
    :param featurename: the name of the feature
    :return: return a plate cell feature
    """
    featurename = str(featurename)
    if featurename.endswith(".mat"):
        featurename = featurename.replace(".mat", "")
    try:
        # number of images on the plate (usually 9 * 384)
        nrow = len(arr)
        # number of cells per image
        rowlens = [len(x) for x in arr]
        # maximum number of cells
        m_ncol = max(rowlens)
        # initialize empty matrix of NaNs
        mat = numpy.full(shape=(nrow, m_ncol),
                         fill_value=numpy.nan,
                         dtype="float64")
        # fill matrix
        for i in range(len(arr)):
            row = arr[i]
            for j in range(len(row)):
                mat[i][j] = row[j]
        return PlateCellFeature(mat, nrow, m_ncol,
                                file, rowlens, featurename)
    except AssertionError:
        logger.warn("Could not alloc feature %s of %s", featurename, file)
    return None
