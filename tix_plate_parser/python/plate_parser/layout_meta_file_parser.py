# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24/10/16

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LayoutMetaFileLoader:
    """
    Class that loads the layout meta files for the plates, i.e. which siRNAs
    map to which well, etc.

    """

    def __init__(self, file):
        """
        Constructor for the meta file loader from an open-bis instance.

        :param file: the experiment meta file
        """

        self._meta_file = file
        self._meta = {}
        self._load()

    def _load(self):
        with open(self._meta_file, "r") as f:
            for entry in f.readline():
                entry = entry.lower()
                if entry.startswith("barcode"):
                    continue
                tokens = entry.strip().split("\t")
                self._add(tokens)

    def _add(self, tokens):
        bar, pathogen, geneset, replicate, library, row, col, well, \
        well_type, gene, sirna = tokens
        classifier = pathogen + "-" + replicate
        if bar not in self._meta:
            self._meta[bar]
