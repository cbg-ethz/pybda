# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 27/10/16

import logging
import re

from .utility import load_matlab

logging.basicConfig(level=logging.INFO, filemode="w")
logger = logging.getLogger(__name__)


class PlateSirnaGeneMapping:
    """
    Class that stores plate sirna-gene mappings.

    """

    def __init__(self, plate_file_set):
        if plate_file_set.mapping is not None:
            self._mapping = []
            self._pattern = re.compile(".*\_w(\\w\\d+)\_s\d\_z\d.*")
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
        cf = load_matlab(plate_file_set.mapping.filename)
        if cf is None:
            return
        # create mapping array of same length
        self._mapping = [None] * len(cf)
        # pattern for every line: we are instested in a char, followed by 2
        # numbers
        for i, e in enumerate(cf):
            self._load_entry(i, self._pattern.match(e[0]))

    def _load_entry(self, i, mat):
        """
        Load a single line/image from the well mapping

        """

        if mat is None:
            return
        self._mapping[i] = mat.group(1).lower()
