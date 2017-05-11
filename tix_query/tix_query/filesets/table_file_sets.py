# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 28.04.17
from tix_query.tix_query.dbms.database import DBMS


class TableFileSets:
    def __init__(self):
        # map of maps that hold file pointers
        # map - (1:n) -> [_gene_map , ...] - (1:m) -> filename
        self._file_set = set()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "TODO"

    def filter(self, **kwargs):
        """
        Get a set of files that meets some criteria. Kwargs is a names list, 
        that can have the following form:
         
         {
                study="infectx",
                pathogen="salmonella",
                well="a01",
                gene="tp53",
                sirna="blub",
                replicate=1,
                library="d"
         }
        
        :return: returns a set of TableFile
         :rtype: set(TableFile)
        """

        with DBMS() as d:
            res = d.query(**kwargs)

    def add_to_fileset(self, file):
        """
        Add a meta file to the set of all available files
                
        """
        self._file_set.add(file)

    def add_file_descriptor(self, study, pathogen,
                            library, design,
                            replicate, plate, file):
        # add 'file' to all different file maps
        els = [study, pathogen, library, design, replicate, plate]
        for i, e in enumerate(self._descr):
            self._add(e, els[i], file)

    def add_element(self, gene, sirna, well, file):
        # add 'file' to all gene/sirna/well maps
        els = [gene, sirna, well]
        for i, e in enumerate(self._gsw_):
            self._add(e, els[i], file)

    def _add(self, name, element, file):
        di = self._map[name]
        if element not in di:
            di[element] = set()
        di[element].add(file)

    @staticmethod
    def _key_map(k):
        return "_" + k + "_map"
