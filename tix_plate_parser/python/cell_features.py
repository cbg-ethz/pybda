# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 22/09/16

import os
import scipy.io as spio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CellFeature:
    def __init__(self, mat):
        self._mat = mat