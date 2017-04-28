# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 28.04.17


class Table:
    _gsw_ = ["_gene_map", "_sirna_map", "_well_map"]
    _descr = ["_study_map", "_pathogen_map", "_library_map", "_design_map",
              "_replicate_map", "_plate_map"]

    def __init__(self):
        self._map = {}
        li = Table._gsw_ + Table._descr
        for m in li:
            self._map[m] = {}

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        import random
        ret = ""
        for m in Table._gsw_ + Table._descr:
            ret += "\n" + m + "\n" + "------------\n"
            i = 0
            for k, v in self._map[m].items():
                if i == 10:
                    break
                i += 1
                fls = [x.filename for x in random.sample(v, min(5, len(v)))]
                ret += ": ".join([k, "(" + ", ".join(fls) + ")"]) + "\n"
        return ret

    def add_file_descriptor(self, study, pathogen, library, design,
                            replicate, plate, file):
        els = [study, pathogen, library, design, replicate, plate]
        for i, e in enumerate(Table._descr):
            self._add(e, els[i], file)

    def add_element(self, gene, sirna, well, file):
        els = [gene, sirna, well]
        for i, e in enumerate(Table._gsw_):
            self._add(e, els[i], file)

    def _add(self, name, element, file):
        di = self._map[name]
        if element not in di:
            di[element] = set()
        di[element].add(file)

    def get(self, **kwargs):
        res = set()
        for k, v in kwargs.items():
            if v is not None:
                cres = self._map["_" + k + "_map"][v]
                if cres:
                    for x in cres:
                        res.add(x)
        return res

