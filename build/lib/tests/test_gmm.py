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

from pybda.fit.gmm_fit import GMMFit
from pybda.globals import PREDICTION__
from pybda.gmm import GMM
from pybda.spark.features import assemble
from tests.test_clustering_api import TestClusteringAPI


class TestGMM(TestClusteringAPI):
    """
    Tests the GMM API
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = assemble(cls.spark_df(), cls.features(), True)

        cls.model = GMM(cls.spark(), [2, 3])
        cls.model.fit(cls.data)
        cls.fit = cls.model.model
        cls.transform = cls.fit[2].transform(cls.data).toPandas()

    @classmethod
    def tearDownClass(cls):
        cls.log("GMM")
        super().tearDownClass()

    def test_fit_gmm_size(self):
        assert len(self.fit.models) == 2

    def test_fit_gmm_keys(self):
        assert 2 in self.fit.models.keys()
        assert 3 in self.fit.models.keys()

    def test_fit_gmm_accessor(self):
        assert isinstance(self.fit[2], GMMFit)

    def test_fit_gmm_mixing_weights(self):
        m2 = self.fit[2]
        assert isinstance(m2.weights, list)

    def test_fit_gmm_params_smaller(self):
        m2, m3 = self.fit[2], self.fit[3]
        assert m2.n_params < m3.n_params

    def test_fit_gmm_loglik(self):
        m2 = self.fit[2]
        assert isinstance(m2.loglik, float)

    def test_fit_gmm_values(self):
        assert isinstance(self.fit[3].values, dict)

    def test_fit_gmm_bic(self):
        assert isinstance(self.fit[3].bic, float)

    def test_fit_gmm_means(self):
        means = self.fit[3].estimates.select("mean").toPandas().values
        assert len(means) == 3

    def test_fit_gmm_means_len(self):
        means = self.fit[3].estimates.select("mean").toPandas().values
        assert means[0][0].values.shape == (4, )

    def test_fit_gmm_cov(self):
        cov = self.fit[3].estimates.select("cov").toPandas().values
        assert len(cov) == 3

    def test_fit_gmm_cov(self):
        cov = self.fit[3].estimates.select("cov").toPandas().values
        assert cov[0][0].toArray().shape == (4, 4)

    def test_transform_gmm_has_prediction(self):
        assert PREDICTION__ in self.transform.columns

    def test_transform_gmm_prediction_works(self):
        vals = numpy.unique(self.transform[PREDICTION__].values)
        assert len(vals) == 2

    def test_transform_gmm_write(self):
        self.model.write(self.data)
