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


import logging
from abc import ABC, abstractmethod

from pybda.globals import FEATURES__
from pybda.io.io import write_tsv
from pybda.spark.features import split_vector

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DimensionReductionTransform(ABC):
    def __init__(self, data, model):
        self.__data = data
        self.__model = model

    @property
    def data(self):
        return self.__data

    @property
    def loadings(self):
        return self.__model.loadings

    @property
    def feature_names(self):
        return self.__model.feature_names

    @property
    def n_components(self):
        return self.__model.n_components

    @property
    def model(self):
        return self.__model

    @abstractmethod
    def write(self, outfolder):
        pass

    @abstractmethod
    def _plot(self, outfile):
        pass

    def write_tsv(self, outfolder):
        data = split_vector(self.data, FEATURES__)
        write_tsv(data, outfolder)
