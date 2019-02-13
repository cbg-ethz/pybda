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
import inspect

import numpy
import pandas
import unittest

import pyspark
from sklearn import datasets


class TestAPI(unittest.TestCase):
    """
    Tests the factor analysis API
    """

    def log(self):
        currentTest = self.id().split('.')[-1]
        callingFunction = inspect.stack()[1][3]
        print('in {} - {}()'.format(currentTest, callingFunction))

    def setUp(self):
        self.log()
        unittest.TestCase.setUp(self)
        self._spark = (pyspark.sql.SparkSession.builder
                      .master("local")
                      .appName("unittest")
                      .config("spark.driver.memory", "3g")
                      .config("spark.executor.memory", "3g")
                      .getOrCreate())

    def tearDown(self):
        self.log()
        self._spark.stop()

    @property
    def spark(self):
        return self._spark
