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

import sklearn.decomposition

from pybda.globals import FEATURES__
from pybda.pca import PCA
from pybda.spark.features import split_vector


class TestPCA(unittest.TestCase):
    """
    Tests the PCA API
    """

    def setUp(self):
        super().setUp()
        self.fa = PCA(self.spark, 2, self.features,)
        self.skfa = sklearn.decomposition.PCA(2, max_iter=1)

    def tearDown(self):
        super().tearDown()

    def test_pca(self):
        fit = self.fa.fit_transform(self.spark_df)
        df = (split_vector(fit.data, FEATURES__))[["f_0", "f_1"]]
        df = df.toPandas().values
        skfit = self.skfa.fit_transform(self.X)


