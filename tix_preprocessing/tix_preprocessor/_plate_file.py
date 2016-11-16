# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 23/09/16


class PlateFile:
    """
    Class that stores the feature name and the absolute filename.

    """

    def __init__(self, filename, feature):
        self._filename = filename
        self._feature = feature

    @property
    def filename(self):
        return self._filename

    @property
    def featurename(self):
        return self._feature

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self._feature

