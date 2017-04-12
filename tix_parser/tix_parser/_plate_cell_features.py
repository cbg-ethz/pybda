# __author__ = 'Simon Dirmeier'
# __email__  = 'simon.dirmeier@bsse.ethz.ch'
# __date__   = 22/09/16


from numpy import shape


class PlateCellFeature:
    """
    Class that stores the features for a single matlab files

    """

    def __init__(self, mat, n_images, n_max_cells_count,
                 filename, n_cells_per_image,
                 featurename):
        """
        :param mat: the parsed matrix
        :param n_images: the number of images * wells (this usually is 3456).
        :param n_max_cells_count: the max number of cells on the well
        :param filename: name of the feature file
        :param n_cells_per_image: the number of cells per image

        """
        self._mat = mat
        self._n_images = n_images
        self._n_max_cells_count = n_max_cells_count
        self._filename = filename
        self._n_cells_per_image = n_cells_per_image
        self._featurename = featurename.lower()
        self._feature_group, self._short_feature_name = self._featurename.split(".")[0:2]
        assert (shape(self._mat)[0] == self._n_images)
        assert (shape(self._mat)[1] == self._n_max_cells_count)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Feature " + self._featurename

    @property
    def max_cells(self):
        return self._n_max_cells_count

    @property
    def values(self):
        return self._mat

    @property
    def featurename(self):
        return self._featurename

    @property
    def ncells(self):
        return self._n_cells_per_image

    @property
    def feature_group(self):
        return self._feature_group

    @property
    def short_name(self):
        return self._short_feature_name