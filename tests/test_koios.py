# Copyright (C) 2018 Simon Dirmeier
#
# This file is part of koios.
#
# koios is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# koios is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with koios. If not, see <http://www.gnu.org/licenses/>.
#
# @author = 'Simon Dirmeier'
# @email = 'simon.dirmeier@bsse.ethz.ch'

import os
import subprocess
import unittest


class TestKoios(unittest.TestCase):
    """
    Tests the control parsing module.

    """

    def setUp(self):
        unittest.TestCase.setUp(self)
        self._file = os.path.join(
          os.path.dirname(__file__), "koios-test.config")

    def test_dim_red(self):
        pr = subprocess.run(
          ["./scripts/koios", "dimension_reduction", self._file, "local"])
        assert pr.returncode == 0

    def test_outliers(self):
        pr = subprocess.run(
          ["./scripts/koios", "outliers", self._file, "local"])
        assert pr.returncode == 0

    def test_clustering(self):
        pr = subprocess.run(
          ["./scripts/koios", "clustering_fit", self._file, "local"])
        assert pr.returncode == 0

    def test_regression(self):
        pr = subprocess.run(
          ["./scripts/koios", "regression", self._file, "local"])
        assert pr.returncode == 0
