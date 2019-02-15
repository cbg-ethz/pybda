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
from pybda.ica import ICA
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
        cls.log("ICA")

        cls.X_lo = cls.X()[:10, :]
        cls.X_lo = scale(cls.X_lo)
        df = pandas.DataFrame(data=cls.X_lo, columns=cls.features())
        cls._spark_lo = TestDimredAPI.spark().createDataFrame(df)

        cls.sk_ica = sklearn.decomposition.FastICA(
          n_components=2, algorithm="deflation", fun="exp",
          max_iter=5, random_state=23)
        cls.sk_ica_trans = cls.sk_ica.fit(cls.X_lo).transform(cls.X_lo)

        cls.ica = ICA(cls.spark(), 2, cls.features())
        cls.X__, cls.unmixing = cls.ica.fit(cls._spark_lo)
        cls.trans = cls.ica.transform(cls._spark_lo, cls.X__, cls.unmixing)

    @classmethod
    def tearDownClass(cls):
        cls.log("ICA")
        super().tearDownClass()

    def test_mixing(self):
        print(self.unmixing)
        print(self.sk_ica.components_)
        assert numpy.allclose(
          numpy.absolute(self.unmixing),
          numpy.absolute(self.sk_ica.components_.T),
          atol=1e-01
        )
