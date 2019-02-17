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
import sklearn.decomposition
from numpy.linalg import linalg
from sklearn.preprocessing import scale

from pybda.factor_analysis import FactorAnalysis
from pybda.globals import FEATURES__
from pybda.ica import ICA
from pybda.pca import PCA
from pybda.spark.features import split_vector
from tests.test_dimred_api import TestDimredAPI


class TestFA(TestDimredAPI):
    """
    Tests the FA API
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.log("FA")

        cls.X_lo = cls.X()[:10, :]
        cls.X_lo = scale(cls.X_lo)
        df = pandas.DataFrame(data=cls.X_lo, columns=cls.features())
        cls._spark_lo = TestDimredAPI.spark().createDataFrame(df)

        cls.sk_fa = sklearn.decomposition.FactorAnalysis(
          n_components=2, max_iter=5, random_state=23)
        cls.sk_fit = cls.sk_fa.fit(cls.X_lo)

        cls.fa = FactorAnalysis(cls.spark(), 2, cls.features(), max_iter=5)
        cls.X, cls.W, cls.ll, cls.psi = cls.fa.fit(cls._spark_lo)

        cls.trans = cls.fa.transform(cls._spark_lo, cls.X,
                                     cls.sk_fit.components_, cls.psi)
        #
        cls.sk_fit.mean_ = numpy.zeros(4)
        cls.sk_trans = cls.sk_fit.transform(cls.X.rows.collect())

    @classmethod
    def tearDownClass(cls):
        cls.log("FA")
        super().tearDownClass()

    def test_fa_loglik(self):
        assert numpy.allclose(
          numpy.absolute(self.ll),
          numpy.absolute(self.sk_fit.loglike_),
          atol=1e-01)

    def test_fa_transform(self):
        ta = split_vector(self.trans.select(FEATURES__),
                          FEATURES__).toPandas().values
        for i in range(2):
            ax1 = sorted(ta[:, i])
            ax2 = sorted(self.sk_trans[:, i])
            assert numpy.allclose(
              numpy.absolute(ax1),
              numpy.absolute(ax2),
              atol=1e-01
            )

    def test_fa_loadings(self):
        assert numpy.allclose(
          numpy.absolute(self.W),
          numpy.absolute(self.sk_fit.components_),
          atol=1e-01)

    def test_fa_psi(self):
        assert numpy.allclose(
          numpy.absolute(self.psi),
          numpy.absolute(self.sk_fit.noise_variance_),
          atol=1e-01)
