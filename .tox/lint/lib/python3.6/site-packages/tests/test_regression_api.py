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


class TestRegressionAPI(TestAPI):
    """
    Setup for the regression unit tests
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.log("Regression")

    @classmethod
    def tearDownClass(cls):
        cls.log("Regression")
        super().tearDownClass()

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
