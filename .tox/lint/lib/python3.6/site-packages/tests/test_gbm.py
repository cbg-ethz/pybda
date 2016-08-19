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
import pandas

import numpy

import pytest
from sklearn import datasets

from pybda.gbm import GBM
from pybda.globals import PROBABILITY__, BINOMIAL_, GAUSSIAN_, PREDICTION__
from pybda.spark.features import split_vector, assemble
from tests.test_api import TestAPI
from tests.test_regression_api import TestRegressionAPI


class TestGBM(TestRegressionAPI):
    """
    Tests the GBM API
    """

    @classmethod
    def setUpClass(cls):
        cls.log("GBM")
        super().setUpClass()

        iris = datasets.load_iris()
        cls._features = ["sl", "sw", "pl", "pw"]
        cls._X = iris.data[iris.target < 2, :4]
        mu = cls._X.dot(numpy.array([-1, 2, -2, 1]))
        cls._y = mu + numpy.random.normal(0, .1, 100)
        eta = 1 / (1 + numpy.exp(-mu))
        cls._y_log = numpy.random.binomial(1, eta)
        df = pandas.DataFrame(
          data=numpy.column_stack((cls._X, cls._y, cls._y_log)),
          columns=cls.features() + [cls.response(),
                                    cls.log_response()])
        cls._spark_df = TestAPI.spark().createDataFrame(df)
        data = assemble(cls.spark_df(), cls.features(), True)

        cls.model_gau = GBM(cls.spark(), cls.response(), cls.features())
        cls.model_gau.fit(data)
        cls.fit_gau = cls.model_gau.model
        cls.transform_gau = cls.model_gau.predict(data)

        cls.model_bin = GBM(cls.spark(), cls.log_response(),
                            cls.features(), BINOMIAL_)
        cls.model_bin.fit(data)
        cls.fit_bin = cls.model_bin.model
        cls.transform_bin = cls.model_bin.predict(data)

    @classmethod
    def tearDownClass(cls):
        cls.log("GBM")
        super().tearDownClass()

    def test_fit_gbm_gaussian_family(self):
        assert self.fit_gau.family == GAUSSIAN_

    def test_fit_gbm_gaussian_response(self):
        assert self.fit_gau.response == self.response()

    def test_fit_gbm_gaussian_features(self):
        assert self.fit_gau.features == self.features()

    def test_fit_gbm_gaussian_mse(self):
        assert isinstance(self.fit_gau.mse, float)

    def test_fit_gbm_gaussian_r2(self):
        assert isinstance(self.fit_gau.r2, float)

    def test_fit_gbm_gaussian_rmse(self):
        assert isinstance(self.fit_gau.rmse, float)

    def test_fit_gbm_gaussian_rmse(self):
        assert isinstance(self.fit_gau.rmse, float)

    def test_fit_gbm_gaussian_precision_fails(self):
        with pytest.raises(AttributeError):
            self.fit_gau.precision

    def test_fit_gbm_gaussian_recall_fails(self):
        with pytest.raises(AttributeError):
            self.fit_gau.recall

    def test_fit_gbm_gaussian_f1_fails(self):
        with pytest.raises(AttributeError):
            self.fit_gau.f1

    def test_fit_gbm_gaussian_accuracy_fails(self):
        with pytest.raises(AttributeError):
            self.fit_gau.accuracy

    def test_fit_gbm_binomial_family(self):
        assert self.fit_bin.family == BINOMIAL_

    def test_fit_gbm_binomial_respose(self):
        assert self.fit_bin.response == self.log_response()

    def test_fit_gbm_binomial_features(self):
        assert self.fit_bin.features == self.features()

    def test_fit_gbm_binomial_precision(self):
        assert isinstance(self.fit_bin.precision, float)

    def test_fit_gbm_binomial_recall(self):
        assert isinstance(self.fit_bin.recall, float)

    def test_fit_gbm_binomial_f1(self):
        assert isinstance(self.fit_bin.f1, float)

    def test_fit_gbm_binomial_accuracy(self):
        assert isinstance(self.fit_bin.accuracy, float)

    def test_transform_gbm_gaussian(self):
        df = self.transform_gau.data.toPandas()
        assert PREDICTION__ in df.columns.values

    def test_transform_gbm_binomial(self):
        df = split_vector(self.transform_bin.data, PROBABILITY__)
        df = df.toPandas()
        assert "p_0" in df.columns.values
        assert "p_1" in df.columns.values

    def test_fit_gbm_binomial_rmse_fails(self):
        with pytest.raises(AttributeError):
            self.fit_bin.rmse

    def test_fit_gbm_binomial_mse_fails(self):
        with pytest.raises(AttributeError):
            self.fit_bin.mse

    def test_fit_gbm_binomial_r2_fails(self):
        with pytest.raises(AttributeError):
            self.fit_bin.r2
