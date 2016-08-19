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

from pybda.fit.kmeans_fit import KMeansFit
from pybda.globals import PREDICTION__
from pybda.kmeans import KMeans
from pybda.spark.features import assemble
from tests.test_clustering_api import TestClusteringAPI


class TestKMeans(TestClusteringAPI):
    """
    Tests the KMeans API
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = assemble(cls.spark_df(), cls.features(), True)

        cls.model = KMeans(cls.spark(), [2, 3])
        cls.model.fit(cls.data)
        cls.fit = cls.model.model
        cls.transform = cls.fit[2].transform(cls.data).toPandas()

    @classmethod
    def tearDownClass(cls):
        cls.log("Kmeans")
        super().tearDownClass()

    def test_fit_kmeans_size(self):
        assert len(self.fit.models) == 2

    def test_fit_kmeans_keys(self):
        assert 2 in self.fit.models.keys()
        assert 3 in self.fit.models.keys()

    def test_fit_kmeans_accessor(self):
        assert isinstance(self.fit[2], KMeansFit)

    def test_fit_kmeans_explained_variance(self):
        m2 = self.fit[2]
        assert isinstance(m2.explained_variance, float)

    def test_fit_kmeans_total_variance(self):
        m2 = self.fit[2]
        assert isinstance(m2.total_variance, float)

    def test_fit_kmeans_total_variance_same(self):
        m2, m3 = self.fit[2], self.fit[3]
        assert m2.total_variance == m3.total_variance

    def test_fit_kmeans_within_cluster_variance(self):
        m2 = self.fit[2]
        assert isinstance(m2.within_cluster_variance, float)

    def test_fit_kmeans_variance_smaller(self):
        m2, m3 = self.fit[2], self.fit[3]
        assert m2.explained_variance < m3.explained_variance

    def test_fit_kmeans_values(self):
        assert isinstance(self.fit[3].values, dict)

    def test_fit_kmeans_bic(self):
        assert isinstance(self.fit[3].bic, float)

    def test_transform_kmeans_has_prediction(self):
        assert PREDICTION__ in self.transform.columns

    def test_transform_kmeans_prediction_works(self):
        vals = numpy.unique(self.transform[PREDICTION__].values)
        assert len(vals) == 2

    def test_transform_kmeans_write(self):
        self.model.write(self.data)
