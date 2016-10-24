# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24/10/16


import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExperimentMetaFileLoader:
    """
    Class that loads the experiment meta files from an open-bis instance

    """

    def __init__(self, file):
        """
        Constructor for the meta file loader from an open-bis instance.

        :param file: the experiment meta file
        """
        self._meta_file = file
        self._plate_files = self._load()

    def __iter__(self):
        for f in self._plate_files:
            yield f

    def _load(self):
        fls = []
        reg = re.compile("BACKUP|REIMAGED|INVASIN|OLIGOPROFILE")
        with open(self._meta_file, "r") as f:
            for entry in f.readlines():
                filename = entry.strip().split("\t")[0]
                if reg.match(filename):
                    continue
                fls.append(filename)
        return fls
