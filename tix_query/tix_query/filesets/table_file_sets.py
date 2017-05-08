# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 28.04.17


from tix_query.tix_query._global import GENE, SIRNA, WELL
from tix_query.tix_query._global import PLATE, REPLICATE, DESIGN
from tix_query.tix_query._global import LIBRARY, PATHOGEN, STUDY


class TableFileSets:
    def __init__(self):
        self._gsw_ = [
            TableFileSets._key_map(x) for x in [GENE, SIRNA, WELL]
        ]
        self._descr = [
            TableFileSets._key_map(x) for x in
            [STUDY, PATHOGEN, LIBRARY, DESIGN, REPLICATE, PLATE]
        ]

        # map of maps that hold file pointers
        # map - (1:n) -> [_gene_map , ...] - (1:m) -> filename
        self._map = {}
        self._file_set = set()
        li = self._gsw_ + self._descr
        for m in li:
            self._map[m] = {}

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        import random
        ret = ""
        for m in self._gsw_ + self._descr:
            ret += "\n" + m + "\n" + "------------\n"
            i = 0
            for k, v in self._map[m].items():
                if i == 10:
                    break
                i += 1
                fls = [x.filename for x in random.sample(v, min(5, len(v)))]
                ret += ": ".join([k, "(" + ", ".join(fls) + ")"]) + "\n"
        return ret

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
        res = self._file_set.copy()
        for k, v in kwargs.items():
            k = str(k)
            if v is not None:
                key = self._key_map(k)
                v = str(v)
                if key not in self._map:
                    raise ValueError(key + " is not a valid lookup key")
                if v in self._map[key]:
                    res = res & self._map[key][v]
                else:
                    return set()
        return res

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
