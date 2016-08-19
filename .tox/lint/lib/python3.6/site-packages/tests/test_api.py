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

import inspect
import unittest

import pyspark


class TestAPI(unittest.TestCase):
    """
    Tests the factor analysis API
    """

    @classmethod
    def log(cls, frm):
        print('in {} - {}()'.format(frm, inspect.stack()[1][3]))

    @classmethod
    def setUpClass(cls):
        cls.log("API")
        unittest.TestCase.setUp(cls)
        TestAPI._spark = pyspark.sql.SparkSession.builder \
            .master("local") \
            .appName("unittest") \
            .config("spark.driver.memory", "3g") \
            .config("spark.executor.memory", "3g") \
            .getOrCreate()

    @classmethod
    def tearDownClass(cls):
        cls.log("API")
        TestAPI._spark.stop()

    @classmethod
    def spark(cls):
        return TestAPI._spark
