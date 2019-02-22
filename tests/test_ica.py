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

from pybda.globals import FEATURES__
from pybda.ica import ICA
from pybda.pca import PCA
from pybda.spark.features import split_vector
from tests.test_dimred_api import TestDimredAPI


class TestICA(TestDimredAPI):
    """
    Tests the CA API
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.log("ICA")

        cls.X_lo = cls.X()[:10, :]
        cls.X_lo = scale(cls.X_lo)
        df = pandas.DataFrame(data=cls.X_lo, columns=cls.features())
        cls._spark_lo = TestDimredAPI.spark().createDataFrame(df)

        cls.sk_ica = sklearn.decomposition.FastICA(
          n_components=2, algorithm="deflation", fun="exp",
          max_iter=5, random_state=23)
        cls.sk_fit = cls.sk_ica.fit(cls.X_lo)
        cls.sk_fit.whiten = False

        cls.ica = ICA(cls.spark(), 2, cls.features())
        cls.trans = cls.ica.fit_transform(cls._spark_lo)
        model = cls.ica.model
        cls.compo = model.loadings
        cls.W = model.unmixing
        cls.K = model.whitening

        cls.sk_trans = cls.sk_fit.transform(cls.X_lo)

    @classmethod
    def tearDownClass(cls):
        cls.log("ICA")
        super().tearDownClass()

    def test_ica_transform(self):
        mk = split_vector(self.trans.data.select(FEATURES__), FEATURES__) \
            .toPandas().values
        print(mk)
        print(self.sk_trans)
        for i in range(2):
            ax1 = sorted(numpy.absolute(mk[:, i]))
            ax2 = sorted(numpy.absolute(self.sk_trans[:, i]))
            assert numpy.allclose(ax1, ax2, atol=1e-02)

    def test_ica_whitening(self):
        assert numpy.allclose(
          numpy.absolute(self.K),
          numpy.absolute(self.sk_ica.whitening_.T),
          atol=1e-03)

    def test_ica_loadings(self):
        assert numpy.allclose(
          numpy.absolute(self.compo),
          numpy.absolute(self.sk_ica.components_),
          atol=1e-03)

    def test_ica_unmixing(self):
        sk_w = self.sk_ica.components_.dot(linalg.pinv(self.sk_ica.whitening_))
        assert numpy.allclose(
          numpy.absolute(self.W),
          numpy.absolute(sk_w),
          atol=1e-03)
