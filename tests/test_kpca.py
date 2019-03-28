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
import sklearn.kernel_approximation
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

from pybda.globals import FEATURES__
from pybda.kpca import KPCA
from pybda.spark.features import split_vector
from pybda.stats.stats import fourier_transform
from tests.test_dimred_api import TestDimredAPI


class TestKPCA(TestDimredAPI):
    """
    Tests the KPCA API
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.log("KPCA")

        cls.X_lo = cls.X()[:10, :]
        cls.X_lo = scale(cls.X_lo)
        df = pandas.DataFrame(data=cls.X_lo, columns=cls.features())
        cls._spark_lo = TestDimredAPI.spark().createDataFrame(df)

        cls.sbf_feature = sklearn.kernel_approximation.RBFSampler \
            (random_state=23, n_components=5)
        cls._X_transformed = cls.sbf_feature.fit_transform(cls.X_lo)
        cls.sk_pca = PCA(n_components=2).fit(cls._X_transformed)

        cls.kpca = KPCA(cls.spark(), 2, cls.features(), 5, 1.)
        cls.trans = cls.kpca.fit_transform(cls._spark_lo)
        cls.trans = split_vector(cls.trans.data.select(FEATURES__),
                                 FEATURES__).toPandas().values
        model = cls.kpca.model
        cls.evals = model.loadings
        cls.sds = model.sds
        cls.w = model.fourier_coefficients
        cls.b = model.fourier_offset

        cls.kpca.fit(cls._spark_lo)
        cls.fittransform_trans = cls.kpca.transform(cls._spark_lo)
        cls.fittransform_trans = split_vector(
          cls.fittransform_trans.data.select(FEATURES__),
          FEATURES__).toPandas().values

        # The sklearn PCA would substract the mean here
        # We don't want that to happen, but work and the Fourier matrix directly
        # setting the mean to None does the trick
        cls.sk_pca.mean_ = None
        cls.sk_pca.components_ = cls.evals
        cls.sk_pca_trans = cls.sk_pca.transform(cls._X_transformed)

    @classmethod
    def tearDownClass(cls):
        cls.log("KPCA")
        super().tearDownClass()

    def test_kpca_fourier(self):
        X = self.kpca._preprocess_data(self._spark_lo)
        X = fourier_transform(X,
                              self.kpca.model.fourier_coefficients,
                              self.kpca.model.fourier_offset)
        df = self.spark().createDataFrame(X.rows.map(lambda x: (x,)))
        df = split_vector(df, "_1").toPandas().values
        for i in range(5):
            ax1 = sorted(df[:, i])
            ax2 = sorted(self._X_transformed[:, i])
            assert numpy.allclose(
              numpy.absolute(ax1),
              numpy.absolute(ax2),
              atol=1e-01)

    def test_kpca_transform(self):
        for i in range(2):
            ax1 = sorted(numpy.absolute(self.trans[:, i]))
            ax2 = sorted(numpy.absolute(self.sk_pca_trans[:, i]))
            assert numpy.allclose(ax1, ax2, atol=1e-01)

    def test_kpca_fit_transform_is_same_as_fittransform(self):
        for i in range(2):
            ax1 = sorted(numpy.absolute(self.trans[:, i]))
            ax2 = sorted(numpy.absolute(self.fittransform_trans[:, i]))
            assert numpy.allclose(ax1, ax2, atol=1e-01)

