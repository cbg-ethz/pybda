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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DimensionReductionFit(ABC):
    def __init__(self, n_components, features, loadings):
        self.__n_components = n_components
        self.__features = features
        self.__loadings = loadings

    @property
    def loadings(self):
        return self.__loadings

    @property
    def feature_names(self):
        return self.__features

    @property
    def n_components(self):
        return self.__n_components

    @abstractmethod
    def write(self, outfolder):
        pass

    def _write_loadings(self, outfile):
        logger.info("Writing loadings to file")
        DataFrame(self.loadings, columns=self.feature_names).to_csv(
          outfile, sep="\t", index=False)

    @abstractmethod
    def _plot(self, outfile):
        pass
