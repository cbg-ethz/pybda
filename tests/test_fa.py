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


import sklearn.decomposition

from pybda.factor_analysis import FactorAnalysis
from pybda.globals import FEATURES__
from pybda.spark.features import split_vector
from tests.test_api import TestAPI
from tests.test_dimred_api import TestDimredAPI


class TestFA(TestDimredAPI):
    """
    Tests the facor analysis API
    """

    def setUp(self):
        super().setUp()
        TestAPI.log("FA")
        self.fa = FactorAnalysis(TestAPI.spark(), 2, self.features)
        self.skfa = sklearn.decomposition.FactorAnalysis(2, max_iter=25)

    def test_fa(self):
        fit = self.fa.fit_transform(self.spark_df)
        df = (split_vector(fit.data, FEATURES__))[["f_0", "f_1"]]
        df = df.toPandas().values
        skfit = self.skfa.fit_transform(self.X)
