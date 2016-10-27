# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 24/10/16

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlateLayoutMeta:
    """
    Class that loads the layout meta files for the plates, i.e. which siRNAs
    map to which well, etc.

    """

    def __init__(self, file):
        """
        Constructor for the meta file loader from an open-bis instance.

        :param file: the experiment meta file
        :param pattern: the patterns you are searching for
        """

        self._meta_file = file
        self._meta = {}
        logger.info("Loading layout...")
        self._load()

    def _load(self):
        with open(self._meta_file, "r") as f:
            for entry in f.readlines():
                entry = entry.upper()
                if entry.startswith("BARCODE"):
                    continue
                tokens = entry.strip().split("\t")
                self._add(tokens)

    def _add(self, tokens):
        bar, expr, pathogen, geneset, replicate, library, row, col, well, \
        well_type, gene, sirna = tokens

        classifier = expr + "-" + bar
        if classifier not in self._meta:
            self._meta[classifier] = PlateLayout(classifier, geneset, library)
        self._meta[classifier].add(gene, sirna, well, well_type)

    def get(self, pathogen, library, replicate, plate):
        """
        Get the layout for a specific plate.

        :param pathogen: the pathogen, e.g. BRUCELLA
        :param library: the library, e.g. DP
        :param replicate: replicate, e.. G1
        :param plate: the plate, e.g. DZ44-1K
        :return: returns a PlateLayout
        """

        cl = "-".join([pathogen, library, replicate, plate]).upper()
        if cl in self._meta:
            return self._meta[cl]
        logger.warn("Did not find " + cl + " in meta file")
        return None


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

    @property
    def sirna(self, well):
        if well not in self._well_layout:
            logger.warn("Could not find well:" + well)
            return None
        return self._well_layout[well].sirna

    @property
    def welltype(self, well):
        if well not in self._well_layout:
            logger.warn("Could not find well:" + well)
            return None
        return self._well_layout[well].welltype

    @property
    def gene(self, well):
        if well not in self._well_layout:
            logger.warn("Could not find well:" + well)
            return None
        return self._well_layout[well].gene


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
    def welltype(self):
        return self._well_type
