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
from sklearn.preprocessing import scale

from tests.test_api import TestAPI


class TestDimredAPI(TestAPI):
    """
    Tests the factor analysis API
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        TestAPI.log("DimRed")

        iris = datasets.load_iris()

        cls._X = iris.data[:, :4]
        cls._X = scale(cls._X)
        cls._y = iris.target

        cls._features = ["sl", "sw", "pl", "pw"]
        df = pandas.DataFrame(
            data=numpy.column_stack((cls._X, cls._y[:, numpy.newaxis])),
            columns=cls.features() + [cls.response()])
        cls._spark_df = cls.spark().createDataFrame(df)

    @classmethod
    def tearDownClass(cls):
        cls.log("Dimred")
        super().tearDownClass()

    @classmethod
    def X(cls):
        return cls._X

    @classmethod
    def y(cls):
        return cls._y

    @classmethod
    def features(cls):
        return cls._features

    @classmethod
    def response(cls):
        return "species"

    @classmethod
    def spark_df(cls):
        return cls._spark_df
