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
        cls.pca = PCA(cls.spark(), 2, cls.features())
        cls.X, cls.loadings, cls.sds = cls.pca.fit(cls.spark_df())
        cls.trans = cls.pca.transform(cls.spark_df(), cls.X, cls.loadings)

    @classmethod
    def tearDownClass(cls):
        cls.log("PCA")
        super().tearDownClass()

    def test_pca(self):
        df = split_vector(self.trans, FEATURES__).toPandas()
        assert "f_0" in df.columns
        assert "f_1" in df.columns
        assert "f_2" not in df.columns
