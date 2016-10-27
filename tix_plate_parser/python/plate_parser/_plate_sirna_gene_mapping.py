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
            logger.error("No meta file: " + str(plate_file_set.classifier))
            self._err = 1
        self._mapping = []
        self._load(plate_file_set)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._mapping[item]
        return None

    def _load(self, plate_file_set):
        cf = load_matlab(plate_file_set.mapping.filename)
        if cf is None:
            logger.error("Could not parse meta: " + str(
                plate_file_set.classifier))
            self._err = 1
        self._mapping = [None] * len(cf)
        pat = re.compile(".*\_w(\\w\\d+)\_s\d\_z\d.*tif")
        for i, e in enumerate(cf):
            mat = pat.match(e[0])
            if mat is None:
                logger.error(
                    "Could not parse meta: " + str(plate_file_set.classifier))
                self._err = 1
                continue
            self._mapping[i] = mat.group(1).upper()
