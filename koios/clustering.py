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

from abc import abstractmethod
from koios.spark_model import SparkModel


class Clustering(SparkModel):
    def __init__(self, spark, clusters, findbest, threshold, max_iter):
        super().__init__(spark)
        self.__threshold = threshold
        self.__max_iter = max_iter
        self.__clusters = clusters
        self.__findbest = findbest

    @property
    def clusters(self):
        return self.__clusters

    @property
    def findbest(self):
        return self.__findbest

    @property
    def max_iter(self):
        return self.__max_iter

    @property
    def threshold(self):
        return self.__threshold

    @abstractmethod
    def fit(self):
        pass

    @abstractmethod
    def fit_transform(self):
        pass
