# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24/10/16


import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlateExperimentMeta:
    """
    Class that loads the experiment meta files from an open-bis instance

    """

    def __init__(self, file, pattern):
        """
        Constructor for the meta file loader from an open-bis instance.

        :param file: the experiment meta file
        :param pattern: a regex that you want to use for file searching
        """
        self._meta_file = file
        self._pattern = pattern
        logger.info("Loading experiments...")
        self._plate_files = self._load()

    def __iter__(self):
        for f in self._plate_files:
            yield f

    def _load(self):
        fls = []
        reg = re.compile(".*((BACKUP)|(INVASIN)|(OLIGOPROFILE)|(TITRATION)|"
                         "(RHINO-TEST)|(1PMOL)).*".upper())
        pat = re.compile(self._pattern)
        with open(self._meta_file, "r") as f:
            for entry in f.readlines():
                entry = entry.upper()
                if entry.startswith("PLATENAME"):
                    continue
                toks = entry.strip().split("\t")
                if len(toks) < 2:
                    continue
                platetype = toks[1]
                # TODO: what?
                if not platetype.lower().startswith("screeningplate"):
                    continue
                filename = toks[0]
                if reg.match(filename):
                    continue
                if not pat.match(filename):
                    continue
                fls.append(filename)
        return fls
