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
from pyspark.mllib.linalg.distributed import RowMatrix
from sklearn import datasets
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale

from pybda.kpca import KPCA
from pybda.stats.stats import fourier
from pybda.util.cast_as import as_rdd_of_array
from tests.test_api import TestAPI
from tests.test_dimred_api import TestDimredAPI


class TestStats(TestAPI):
    """
    Tests the Stats API
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.log("Stats")

        iris = datasets.load_iris()
        cls._X = iris.data[:10, :4]
        cls._X = scale(cls._X)
        cls._features = ["sl", "sw", "pl", "pw"]

        df = pandas.DataFrame(data=cls._X, columns=cls._features)
        cls._spark_lo = cls.spark().createDataFrame(df)

        cls.sbf_feature = sklearn.kernel_approximation.RBFSampler \
            (random_state=23, n_components=5)

        cls._sbf_X_transformed = cls.sbf_feature.fit_transform(cls._X)
        cls.Xf, cls.w, cls.b = fourier(
            RowMatrix(as_rdd_of_array(cls._spark_lo)), 5, 23, 1)

    @classmethod
    def tearDownClass(cls):
        cls.log("Stats")
        super().tearDownClass()

    def test_fourier_w(self):
        assert numpy.allclose(
          numpy.absolute(self.w.toArray()),
          numpy.absolute(self.sbf_feature.random_weights_),
          atol=1e-01,
        )

    def test_fourier_offset(self):
        assert numpy.allclose(
          numpy.absolute(self.b),
          numpy.absolute(self.sbf_feature.random_offset_),
          atol=1e-01,
        )

    def test_fourier_transform(self):
        assert numpy.allclose(
          numpy.absolute(self.Xf.rows.collect()),
          numpy.absolute(self._sbf_X_transformed),
          atol=1e-01,
        )
