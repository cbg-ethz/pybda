# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 08.05.17


from tix_query.tix_query._global import WELL, GENE, SIRNA


class ResultSet:

    _filters_ = [GENE, SIRNA, WELL]

    def __init__(self, files, sample, **kwargs):
        self._file_set = files
        self._sample = sample
        self._set_filters(**kwargs)

    def _set_filters(self, **kwargs):
        for f in ResultSet._filters_:
            self.__setattr__("_" + f, None)
        for k, v in kwargs.items():
            if k in ResultSet._filters_:
                self.__setattr__("_" + k, v)


    def dump(self, filename=None):
        pass
