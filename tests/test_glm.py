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
import pytest

from pybda.glm import GLM
from pybda.globals import PROBABILITY__, BINOMIAL_, GAUSSIAN_, PREDICTION__, \
    INTERCEPT__
from pybda.spark.features import split_vector, assemble
from tests.test_regression_api import TestRegressionAPI


class TestGLM(TestRegressionAPI):
    """
    Tests the GLM API
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        data = assemble(cls.spark_df(), cls.features(), True)

        cls.model_gau = GLM(cls.spark(), cls.response(), cls.features())
        cls.fit_gau = cls.model_gau.fit(data)
        cls.transform_gau = cls.fit_gau.transform(data)

        cls.model_bin = GLM(cls.spark(), cls.log_response(),
                            cls.features(), BINOMIAL_)
        cls.fit_bin = cls.model_bin.fit(data)
        cls.transform_bin = cls.fit_bin.transform(data)
        k = 2

    @classmethod
    def tearDownClass(cls):
        cls.log("GLM")
        super().tearDownClass()

    def test_fit_glm_gaussian_family(self):
        assert self.fit_gau.family == GAUSSIAN_

    def test_fit_glm_gaussian_response(self):
        assert self.fit_gau.response == self.response()

    def test_fit_glm_gaussian_mse(self):
        assert isinstance(self.fit_gau.mse, float)

    def test_fit_glm_gaussian_r2(self):
        assert isinstance(self.fit_gau.r2, float)

    def test_fit_glm_gaussian_rmse(self):
        assert isinstance(self.fit_gau.rmse, float)

    def test_fit_glm_gaussian_features(self):
        assert (self.fit_gau.features == [INTERCEPT__] + self.features()).all()

    def test_fit_glm_gaussian_coefficients(self):
        assert len(self.fit_gau.coefficients) == 5

    def test_fit_glm_gaussian_pvals(self):
        assert len(self.fit_gau.p_values) == 5

    def test_fit_glm_gaussian_tvals(self):
        assert len(self.fit_gau.t_values) == 5

    def test_fit_glm_gaussian_errors(self):
        assert len(self.fit_gau.standard_errors) == 5

    def test_fit_glm_gaussian_accuracy_fails(self):
        with pytest.raises(AttributeError):
            self.fit_gau.accuracy

    def test_fit_glm_gaussian_auc_fails(self):
        with pytest.raises(AttributeError):
            self.fit_gau.auc

    def test_fit_glm_gaussian_pr_fails(self):
        with pytest.raises(AttributeError):
            self.fit_gau.precision_recall

    def test_fit_glm_gaussian_roc_fails(self):
        with pytest.raises(AttributeError):
            self.fit_gau.roc

    def test_fit_glm_gaussian_roc_fails(self):
        with pytest.raises(AttributeError):
            self.fit_gau.measures

    def test_fit_glm_binomial_family(self):
        assert self.fit_bin.family == BINOMIAL_

    def test_fit_glm_binomial_respose(self):
        assert self.fit_bin.response == self.log_response()

    def test_fit_glm_binomial_accuracy(self):
        assert isinstance(self.fit_bin.accuracy, float)

    def test_fit_glm_binomial_pre(self):
        assert isinstance(self.fit_bin.precision_recall, pandas.DataFrame)

    def test_fit_glm_binomial_roc(self):
        assert isinstance(self.fit_bin.roc, pandas.DataFrame)

    def test_fit_glm_binomial_measures(self):
        assert isinstance(self.fit_bin.measures, pandas.DataFrame)

    def test_transform_glm_gaussian(self):
        df = self.transform_gau.data.toPandas()
        assert PREDICTION__ in df.columns.values

    def test_transform_glm_binomial(self):
        df = split_vector(self.transform_bin.data, PROBABILITY__)
        df = df.toPandas()
        assert "p_0" in df.columns.values
        assert "p_1" in df.columns.values

    def test_fit_glm_binomial_features(self):
        assert (self.fit_bin.features == [INTERCEPT__] + self.features()).all()

    def test_fit_glm_binomial_coefficients(self):
        assert len(self.fit_bin.coefficients) == 5

    def test_fit_glm_binomial_pvals(self):
        assert len(self.fit_bin.p_values) == 5

    def test_fit_glm_binomial_tvals(self):
        assert len(self.fit_bin.t_values) == 5

    def test_fit_glm_binomial_errors(self):
        assert len(self.fit_bin.standard_errors) == 5

    def test_fit_glm_binomial_rmse_fails(self):
        with pytest.raises(AttributeError):
            self.fit_bin.rmse

    def test_fit_glm_binomial_mse_fails(self):
        with pytest.raises(AttributeError):
            self.fit_bin.mse

    def test_fit_glm_binomial_r2_fails(self):
        with pytest.raises(AttributeError):
            self.fit_bin.r2
