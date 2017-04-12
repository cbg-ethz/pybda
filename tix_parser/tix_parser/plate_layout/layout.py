# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24/10/16

import logging

from .plate_layout import PlateLayout

logger = logging.getLogger(__name__)


class MetaLayout:
    """
    Class that loads the layout meta files for the plates, i.e. which siRNAs
    map to which well, etc.

    """

    def __init__(self, file):
        """
        Constructor for the meta file loader from an open-bis instance,
        e.g.: target_infect_x_library_layouts_beautified.tsv

        :param file: the layout meta file
        :param pattern: the patterns you are searching for
        """

        self._meta_file = file
        self._meta = {}
        logger.info("Loading layout...")
        self._load()

    def _load(self):
        with open(self._meta_file, "r") as f:
            for entry in f.readlines():
                entry = entry.lower()
                if entry.startswith("barcode"):
                    continue
                tokens = entry.strip().split("\t")
                self._add(tokens)

    def _add(self, tokens):
        bar, expr, pathogen, geneset, replicate, library, row, col, well, \
        well_type, gene, sirna = tokens
        classifier = (expr + "-" + bar)
        if classifier not in self._meta:
            self._meta[classifier] = PlateLayout(classifier, geneset, library)
        self._meta[classifier].add(gene, sirna, well, well_type)

    def get(self, pathogen, library, design, screen, replicate, plate):
        """
        Get the layout for a specific plate.

        :param pathogen: the pathogen, e.g. BRUCELLA
        :param library: the library, e.g. DP
        :param screen: replicate, e.g D
        :param replicate: replicate, e.g 1
        :param plate: the plate, e.g. DZ44-1K
        :return: returns a PlateLayout
        """

        cl = "-".join([pathogen,
                       "".join([library, design]),
                       "".join([screen, replicate]),
                       plate]).lower()
        if cl in self._meta:
            return self._meta[cl]
        logger.warn("Did not find " + cl + " in meta file")
        return None





