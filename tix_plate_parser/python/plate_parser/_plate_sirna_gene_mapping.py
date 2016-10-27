# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 27/10/16

import logging
import scipy.io as spio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlateSirnaGeneMapping:
    """
    Class that stores plate sirna-gene mappings.

    """

    def __init__(self, plate_file_set):
        if plate_file_set.mapping is None:
            logger.error("No meta file: " + str(plate_file_set.classifier))
            exit(-1)
        self._mapping = {}
        self._load(plate_file_set)

    def _load(self, plate_file_set):
        cf = self._load_matlab(plate_file_set.mapping.filename)
        if cf is None:
            logger.error("Could not parse meta file: " +
                         str(plate_file_set.classifier))
            exit(-1)

    @staticmethod
    def _load_matlab(file):
        matlab_matrix = (spio.loadmat(file))
        return matlab_matrix["handles"][0][0][0][0][0][0][0][0][0][0]
