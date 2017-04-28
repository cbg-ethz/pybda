# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 28.04.17


class TableFile:
    def __init__(self, path, filename, feature_class, feature_list):
        self._path = path
        self._filename = filename.replace("_meta.tsv", "_data.tsv")
        self._feature_class = feature_class
        self._feature_list = feature_list

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self._filename

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
