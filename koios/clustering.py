# Copyright (C) 2018 Simon Dirmeier
#
# This file is part of koios.
#
# koios is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# koios is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with koios. If not, see <http://www.gnu.org/licenses/>.
#
# @author = 'Simon Dirmeier'
# @email = 'simon.dirmeier@bsse.ethz.ch'
import glob
import logging
from abc import abstractmethod

from koios.globals import GMM__, FEATURES__
from koios.spark.features import n_features, split_vector
from koios.spark_model import SparkModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Clustering(SparkModel):
    def __init__(self, spark, clusters, threshold, max_iter, kind):
        super().__init__(spark)
        self.__kind = kind
        if kind == GMM__:
            self.__name_components = "components"
            self.__algorithm_type = "mixture"
        else:
            self.__name_components = "clusters"
            self.__algorithm_type = "clustering"
        if isinstance(clusters, str):
            clusters = list(map(int, clusters.split(",")))
        self.__threshold = threshold
        self.__max_iter = max_iter
        self.__clusters = clusters

    @property
    def clusters(self):
        return self.__clusters

    @property
    def max_iter(self):
        return self.__max_iter

    @property
    def threshold(self):
        return self.__threshold

    @abstractmethod
    def fit_transform(self):
        pass

    @abstractmethod
    def fit(self):
        pass

    @staticmethod
    def _check_transform(models, fit_folder):
        if fit_folder is None and models is None:
            raise ValueError("Provide either 'models' or a 'models_folder'")
