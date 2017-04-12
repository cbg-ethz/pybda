# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24/10/16


import logging
import re

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)-1s/%(processName)-1s/%('
                           'name)-1s]: %(message)s')
logger = logging.getLogger(__name__)


class PlateList:
    """
    Class that stores plate file names as array and removes lines that should not be used

    """

    def __init__(self, file, pattern):
        """
        Constructor for the meta file loader from an open-bis instance.

        :param file: the experiment meta file
        :param pattern: a regex that you want to use for file searching
        """
        self._meta_file = file
        self._pattern = pattern
        # regex that automatically excludes files
        self._regex = re.compile(
            ".*((BACKUP)|(INVASIN)|(OLIGOPROFILE)|(TITRATION)|"
            "(RHINO-TEST)|(1PMOL)).*".upper())
        logger.info("Loading experiments...")
        self._plate_files = self._load()

    def __iter__(self):
        for f in self._plate_files:
            yield f

    @property
    def plate_files(self):
        return self._plate_files

    def _load(self):
        fls = []
        pat = re.compile(self._pattern)
        with open(self._meta_file, "r") as f:
            for entry in f.readlines():
                entry = entry.upper()
                if entry.startswith("PLATENAME"):
                    continue
                toks = entry.strip().split("\t")
                if len(toks) < 2:
                    continue
                filename, platetype = toks[0], toks[1]
                if not platetype.lower().startswith("screeningplate"):
                    continue
                if self._regex.match(filename) or not pat.match(filename):
                    continue
                fls.append(filename)
        return fls
