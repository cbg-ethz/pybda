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

from pybda.fit.ensemble_fit import EnsembleFit
from pybda.regression import Regression

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Ensemble(Regression):
    def __init__(self, spark, family, response, features, max_depth,
                 subsampling_rate):
        super().__init__(spark, family, response, features)
        self.__max_depth = max_depth
        self.__subsampling_rate = subsampling_rate

    def fit(self, data):
        logger.info("Fitting forest with family='{}'".format(self.family))
        model = self._fit(data)
        self.model = EnsembleFit(data, model, self.response,
                                 self.family, self.features)
        return self

    @property
    def max_depth(self):
        return self.__max_depth

    @property
    def subsampling_rate(self):
        return self.__subsampling_rate
