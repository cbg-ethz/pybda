# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 27/10/16

import logging
import re

from ._utility import load_matlab

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlateSirnaGeneMapping:
    """
    Class that stores plate sirna-gene mappings.

    """

    def __init__(self, plate_file_set):
        self._err = 0
        if plate_file_set.mapping is None:
            self._set_error(plate_file_set)
        self._mapping = []
        self._pattern = re.compile(".*\_w(\\w\\d+)\_s\d\_z\d.*tif")
        self._load(plate_file_set)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._mapping[item]
        return None

    def __len__(self):
        return len(self._mapping)

    def _load(self, plate_file_set):
        """
        Load the sirna-gene mapping file

        :param plate_file_set: plate file set object
        """

        # read the plate file
        cf = load_matlab(plate_file_set.mapping.filename)
        if cf is None:
            self._set_error(plate_file_set)
            return
        # create mapping array of same length
        self._mapping = [None] * len(cf)
        # pattern for every line: we are instested in a char, followed by 2
        # numbers

        for i, e in enumerate(cf):
            self._load_entry(plate_file_set, i, self._pattern.match(e[0]))

    def _load_entry(self, plate_file_set, i, mat):
        """
        Load a single line/image from the well mapping

        """

        if mat is None:
            self._set_error(plate_file_set)
            return
        self._mapping[i] = mat.group(1).upper()

    def _set_error(self, plate_file_set):
        logger.error(
            "Could not parse meta: " + str(plate_file_set.classifier))
        self._err = 1
