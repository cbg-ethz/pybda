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


from abc import ABC
from koios.spark_model import SparkModel


class DimensionReduction(ABC, SparkModel):
    def __init__(self, spark, threshold, max_iter):
        super().__init__(spark)
        self.__threshold = threshold
        self.__max_iter = max_iter

    @property
    def threshold(self):
        return self.__threshold

    @property
    def max_iter(self):
        return self.__max_iter
