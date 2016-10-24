# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24/10/16

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LayoutMeta:
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
            for entry in f.readlines():
                entry = entry.lower()
                if entry.startswith("barcode"):
                    continue
                tokens = entry.strip().split("\t")
                self._add(tokens)

    def _add(self, tokens):
        bar, expr, pathogen, geneset, replicate, library, row, col, well, \
        well_type, gene, sirna = tokens
        classifier = expr + "-" + bar
        if classifier not in self._meta:
            self._meta[classifier] = PlateLayout(classifier, geneset,
                                                 library)
        self._meta[classifier].add(gene, sirna, well, well_type)


class PlateLayout(object):
    def __init__(self, classifier, geneset, library):
        self._classifier = classifier
        self._geneset = geneset
        self._library = library
        self._well_layout = {}

    def add(self, gene, sirna, well, well_type):
        if well in self._well_layout:
            logger.warn("Adding " + well + " multiple times to " +
                        self._classifier + " layout!")
        self._well_layout[well] = Well(gene, sirna, well, well_type)


class Well:
    def __init__(self, gene, sirna, well, well_type):
        self._gene = gene
        self._sirna = sirna
        self._well = well
        self._well_type = well_type

    @property
    def gene(self):
        return self._gene

    @property
    def sirna(self):
        return self._sirna

    @property
    def well_type(self):
        return self._well_type
