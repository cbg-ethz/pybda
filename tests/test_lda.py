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
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from pybda.lda import LDA
from tests.test_dimred_api import TestDimredAPI


class TestLDA(TestDimredAPI):
    """
    Tests the LDA API
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.log("LDA")
        cls.sk_lda = LinearDiscriminantAnalysis(n_components=2, solver="eigen")
        cls.sk_lda_trans = cls.sk_lda.fit(cls.X(), cls.y()).transform(cls.X())

        cls.lda = LDA(cls.spark(), 2, cls.features(), cls.response())
        cls.eval, cls.evec = cls.lda.fit(cls.spark_df())
        cls.trans = cls.lda.transform(cls.spark_df(), cls.sk_lda.scalings_)
        cls.fit_tran = cls.lda.fit_transform(cls.spark_df())

    @classmethod
    def tearDownClass(cls):
        cls.log("LDA")
        super().tearDownClass()

    def test_lda_loadings(self):
        assert numpy.allclose(
          numpy.absolute(self.sk_lda.scalings_[:,:2]),
          numpy.absolute(self.eval[:,:2]),
          atol=1e-01)

    def test_lda_response(self):
        assert self.fit_tran.response == self.response()

    def test_lda_discrimants(self):
        assert self.fit_tran.n_discriminants == 2

    def test_lda_projection(self):
        assert isinstance(self.fit_tran.projection, numpy.ndarray)

    def test_lda_correct_loadings_were_chosen(self):
        arr = self.fit_tran.variances
        assert numpy.all(arr[:-1] >= arr[1:])

