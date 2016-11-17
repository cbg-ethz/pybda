# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 17/11/16


import logging

logger = logging.getLogger(__name__)


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

    def sirna(self, well):
        if well not in self._well_layout:
            logger.warn("Could not find well:" + well)
            return None
        return self._well_layout[well].sirna

    def welltype(self, well):
        if well not in self._well_layout:
            logger.warn("Could not find well:" + well)
            return None
        return self._well_layout[well].welltype

    def gene(self, well):
        if well not in self._well_layout:
            logger.warn("Could not find well:" + well)
            return None
        return self._well_layout[well].gene