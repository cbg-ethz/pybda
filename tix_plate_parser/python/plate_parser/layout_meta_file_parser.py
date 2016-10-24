# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24/10/16

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LayoutMetaFileLoader:
    """
    Class that loads the layout meta files from an open-bis instance

    """

    def __init__(self, file):
        """
        Constructor for the meta file loader from an open-bis instance.

        :param file: the experiment meta file
        """
        self._meta_file = file
