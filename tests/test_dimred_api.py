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


import numpy
import pandas
from sklearn import datasets

from tests.test_api import TestAPI


class TestDimredAPI(TestAPI):
    """
    Tests the factor analysis API
    """

    def setUp(self):
        TestAPI.log("DimRed")
        super().setUp()
        iris = datasets.load_iris()
        self._X = iris.data[:, :4]
        y = iris.target
        self._features = ["sl", "sw", "pl", "pw"]
        df = pandas.DataFrame(
            data=numpy.column_stack((self.X, y)),
            columns=self.features + ["species"])
        self._spark_df = TestAPI.spark().createDataFrame(df)

    @property
    def X(self):
        return self._X

    @property
    def features(self):
        return self._features

    @property
    def spark_df(self):
        return self._spark_df
