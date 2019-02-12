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

import unittest

import numpy
import pandas
import pyspark

from sklearn import datasets
import sklearn.decomposition

from pybda.factor_analysis import FactorAnalysis
from pybda.globals import FEATURES__
from pybda.spark.features import split_vector


class TestKPCA(unittest.TestCase):
    """
    Tests the facor analysis API
    """

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.spark = (pyspark.sql.SparkSession.builder
                      .master("local")
                      .appName("unittest")
                      .config("spark.driver.memory", "3g")
                      .config("spark.executor.memory", "3g")
                      .getOrCreate())
        iris = datasets.load_iris()
        self.X = iris.data[:, :4]
        y = iris.target
        self.features = ["sl", "sw", "pl", "pw"]
        df = pandas.DataFrame(data=numpy.column_stack((self.X, y)),
                                   columns=self.features + ["species"])
        self.spark_df = self.spark.createDataFrame(df)
        self.fa = FactorAnalysis(self.spark, 2, self.features)

        self.skfa = sklearn.decomposition.FactorAnalysis(2, max_iter=25)

    def tearDown(self):
        self.spark.stop()

    def test_fa(self):
        fit = self.fa.fit_transform(self.spark_df)
        df = (split_vector(fit.data, FEATURES__))[["f_0", "f_1"]]
        df = df.toPandas().values
        skfit = self.skfa.fit_transform(self.X)

