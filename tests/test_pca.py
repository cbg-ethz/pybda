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
from sklearn.preprocessing import scale

from pybda.globals import FEATURES__
from pybda.pca import PCA
from pybda.spark.features import split_vector
from tests.test_dimred_api import TestDimredAPI


class TestPCA(TestDimredAPI):
    """
    Tests the PCA API
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.log("PCA")

        cls.X_lo = cls.X()[:10, :]
        cls.X_lo = scale(cls.X_lo)
        df = pandas.DataFrame(data=cls.X_lo, columns=cls.features())
        cls._spark_lo = TestDimredAPI.spark().createDataFrame(df)

        cls.sk_pca = sklearn.decomposition.PCA(n_components=2)

        cls.pca = PCA(cls.spark(), 2, cls.features())
        cls.X__, cls.loadings, cls.sds = cls.pca.fit(cls._spark_lo)

        cls.sk_pca_trans = cls.sk_pca.fit(cls.X_lo).transform(cls.X_lo)
        cls.trans = cls.pca.transform(cls._spark_lo, cls.X__,
                                      cls.sk_pca.components_)

    @classmethod
    def tearDownClass(cls):
        cls.log("PCA")
        super().tearDownClass()

    def test_pca(self):
        df = split_vector(self.trans, FEATURES__).toPandas()
        assert "f_0" in df.columns
        assert "f_1" in df.columns
        assert "f_2" not in df.columns

    def test_loadings(self):
        assert numpy.allclose(
          numpy.absolute(self.loadings[:2]),
          numpy.absolute(self.sk_pca.components_),
          atol=1e-01
        )

    def test_scores(self):
        sk_ax1 = sorted(self.sk_pca_trans[:, 0])
        sk_ax2 = sorted(self.sk_pca_trans[:, 1])
        m = split_vector(self.trans.select(FEATURES__),
                         FEATURES__).toPandas().values
        ax1 = sorted(m[:, 0])
        ax2 = sorted(m[:, 1])
        assert numpy.allclose(numpy.absolute(ax1), numpy.absolute(sk_ax1),
                              atol=1e-01)
        assert numpy.allclose(numpy.absolute(ax2), numpy.absolute(sk_ax2),
                              atol=1e-01)
