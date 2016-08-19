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
        # we need to scale this here, because sklearn does not do
        # the scaling for transformations
        cls.X_lo = scale(cls.X_lo)
        df = pandas.DataFrame(data=cls.X_lo, columns=cls.features())
        cls._spark_lo = TestDimredAPI.spark().createDataFrame(df)

        cls.pca = PCA(cls.spark(), 2, cls.features())
        cls.trans = cls.pca.fit_transform(cls._spark_lo)
        cls.trans_panda = split_vector(cls.trans.data.select(FEATURES__),
                                       FEATURES__).toPandas()
        cls.trans = cls.trans_panda.values
        model = cls.pca.model
        cls.loadings = model.loadings
        cls.sds = model.sds

        cls.pca.fit(cls._spark_lo)
        cls.fittransform_trans = cls.pca.transform(cls._spark_lo)
        cls.fittransform_trans = split_vector(
            cls.fittransform_trans.data.select(FEATURES__),
            FEATURES__).toPandas().values

        cls.sk_pca = sklearn.decomposition.PCA(n_components=2)
        cls.sk_pca_trans = cls.sk_pca.fit(cls.X_lo).transform(cls.X_lo)
        k = 2

    @classmethod
    def tearDownClass(cls):
        cls.log("PCA")
        super().tearDownClass()

    def test_pca_cols(self):
        assert "f_0" in self.trans_panda.columns
        assert "f_1" in self.trans_panda.columns
        assert "f_2" not in self.trans_panda.columns

    def test_pca_loadings(self):
        assert numpy.allclose(
          numpy.absolute(self.loadings[:2]),
          numpy.absolute(self.sk_pca.components_),
          atol=1e-01)

    def test_pca_scores(self):
        for i in range(2):
            ax1 = sorted(numpy.absolute(self.sk_pca_trans[:, i]))
            ax2 = sorted(numpy.absolute(self.trans[:, i]))
            assert numpy.allclose(ax1, ax2, atol=1e-01)

    def test_pca_fit_transform_is_same_as_fittransform(self):
        for i in range(2):
            ax1 = sorted(numpy.absolute(self.trans[:, i]))
            ax2 = sorted(numpy.absolute(self.fittransform_trans[:, i]))
            assert numpy.allclose(ax1, ax2, atol=1e-01)

