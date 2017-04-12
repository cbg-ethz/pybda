# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 16/11/16

import subprocess


class PlateDownloader:
    """
    Class for plate downloading.

    """

    def __init__(self, bee_loader, output_path, username, pw):
        """
        Constructor for the plate downloader.

        :param bee_loader: the full path with the script name that downloads
        the data (e.g. /bla/..../BeeDataSetDownloader.sh)
        :param output_path: the folder where all the plates get stored and
        parsed to
        :param username: the user name of the open bis instance
        :param pw: the password of the open bis instance
        """
        self._bee_loader = bee_loader
        self._output_path = output_path
        self._username = username
        self._pw = pw

    def load(self, plate_id):
        """
        Download a plate using the bee-data downloader.

        :param plate_id: the full qualifier id of a plate
        :return:
        """
        sc = [self._bee_loader,
              "--user", self._username,
              "--password", self._pw,
              "--outputdir", self._output_path,
              "--plateid", plate_id,
              "--type", "HCS_ANALYSIS_CELL_FEATURES_CC_MAT",
              "--newest",
              "--files", ".*.mat",
              "--verbose", "1"]
        ret = subprocess.call(sc)
        return ret