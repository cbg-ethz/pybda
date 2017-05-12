# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 28.04.17


import re

from tix_query.tix_query.globals import FEATURECLASS
from tix_query.tix_query.globals import GENE, SIRNA, LIBRARY, DESIGN
from tix_query.tix_query.globals import REPLICATE, PLATE, STUDY, PATHOGEN

class TableFile:
    def __init__(self, filename, **kwargs):
        f = filename.replace("_meta.tsv", "")
        self._filename = f + "_data.tsv"
        self._feature_class = f.split("_")[-1]
        self._feature_list_table = f.split("/")[-1].replace("-", "_")
        self._filter = kwargs

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Tablefile: " + self._feature_list_table

    def __eq__(self, other):
        if not isinstance(other, TableFile):
            return False
        return self._filename == other._filename

    def __hash__(self):
        return hash(self._filename)

    @property
    def filename(self):
        return self._filename

    @property
    def feature_class(self):
        return self._feature_class
