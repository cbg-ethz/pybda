# Copyright (C) 2018 Simon Dirmeier
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


class TestRegressionAPI(TestAPI):
    """
    Tests the factor analysis API
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.log("Regression")
        iris = datasets.load_iris()
        cls._features = ["sl", "sw", "pl", "pw"]
        cls._X = iris.data[iris.target < 2, :4]
        mu = cls._X.dot(numpy.array([-1, 2, -2, 1]))
        cls._y = mu + numpy.random.normal(0, .1, 100)
        eta = 1 / (1 + numpy.exp(-mu))
        cls._y_log = numpy.random.binomial(1, eta)
        df = pandas.DataFrame(
          data=numpy.column_stack((cls._X,
                                   cls._y,
                                   cls._y_log)),
          columns=cls.features() +
                  [cls.response(),
                   cls.log_response()])
        cls._spark_df = TestAPI.spark().createDataFrame(df)

    @classmethod
    def X(cls):
        return cls._X

    @classmethod
    def features(cls):
        return cls._features

    @classmethod
    def log_response(cls):
        return "logresponse"

    @classmethod
    def response(cls):
        return "response"

    @classmethod
    def spark_df(cls):
        return cls._spark_df
