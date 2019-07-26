# Copyright (C) 2018, 2019 Simon Dirmeier
#
# This file is part of pybda.
#
# pybda is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pybda is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pybda. If not, see <http://www.gnu.org/licenses/>.
#
# @author = 'Simon Dirmeier'
# @email = 'simon.dirmeier@bsse.ethz.ch'


from abc import abstractmethod

from pybda.decorators import timing
from pybda.spark_model import SparkModel
from pybda.util.cast_as import as_rdd_of_array


class DimensionReduction(SparkModel):
    def __init__(self, spark, features, threshold, max_iter):
        super().__init__(spark)
        self.__features = features
        self.__threshold = threshold
        self.__max_iter = max_iter
        self.__model = None

    @property
    def model(self):
        return self.__model

    @model.setter
    def model(self, model):
        self.__model = model

    def write(self, outfolder):
        self.model.write(outfolder)

    @property
    def features(self):
        return self.__features

    @property
    def threshold(self):
        return self.__threshold

    @property
    def max_iter(self):
        return self.__max_iter

    @abstractmethod
    def fit(self, data):
        pass

    @abstractmethod
    def fit_transform(self, data):
        pass

    @abstractmethod
    def transform(self, data):
        pass

    @timing
    def _feature_matrix(self, data):
        return as_rdd_of_array(data.select(self.features))
