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

from pandas import DataFrame

from pybda.globals import FEATURES__
from pybda.io.io import write_tsv
from pybda.spark.features import split_vector

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DimensionReductionTransform(ABC):
    def __init__(self, data, n_components, features, W):
        self.__data = data
        self.__n_components = n_components
        self.__features = features
        self.__W = W

    @property
    def loadings(self):
        return self.__W

    @property
    def data(self):
        return self.__data

    @property
    def feature_names(self):
        return self.__features

    @property
    def n_components(self):
        return self.__n_components

    @abstractmethod
    def write_files(self, outfolder):
        pass

    def _write_loadings(self, outfile):
        logger.info("Writing loadings to file")
        DataFrame(self.loadings, columns=self.feature_names).to_csv(
            outfile, sep="\t", index=False)

    @abstractmethod
    def _plot(self, outfile):
        pass

    def write_tsv(self, outfolder):
        data = split_vector(self.data, FEATURES__)
        write_tsv(data, outfolder)
