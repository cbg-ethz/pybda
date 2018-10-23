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


from koios.spark_model import SparkModel


class Regression(SparkModel):
    def __init__(self, spark, family, do_crossvalidation):
        super().__init__(spark)
        self.__family = family
        self.__do_crossvalidation = do_crossvalidation

    @property
    def family(self):
        return self.__family

    @property
    def do_cross_validation(self):
        return self.__do_crossvalidation

    def fit(self):
        pass

    def fit_transform(self, data):
        pass

    def transform(self):
        pass
