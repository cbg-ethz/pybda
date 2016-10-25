# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 25/10/16

import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlateLoader:
    """
    Class for plate downloading

    """

    def __init__(self, bee_loader, download_path, username, pw):
        """

        :param bee_loader:
        :param download_path:
        :param username:
        :param pw:
        """
        self._bee_loader = bee_loader
        self._download_path = download_path
        self._username = username
        self._pw = pw
        self._BEESRC = "BEESOFTSRC"
        if self._BEESRC not in os.environ:
            logger.error("Could not find $BEESOFTSRC environment variable")
            exit(-1)

    def load(self, plate_id):
        logger.log("Downloading: " + plate_id)
        sc = [self._BEESRC,
              "--user", self._username,
              "--password", self._pw,
              "--outputdir", self._download_path,
              "--plateid", plate_id,
              "--datasetid", "HCS_ANALYSIS_CELL_FEATURES_CC_MAT",
              " --files", ".*.mat"]
        ret = subprocess.call(sc)
        if ret != 0:
            logger.warn("\tdownloaded failed with status: " + str(0))
        return ret
