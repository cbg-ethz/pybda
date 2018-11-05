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

from koios.globals import *


class TestKoios(unittest.TestCase):
    """
    Tests the control parsing module.

    """

    __CONFIG__ = {
        "dimension_reduction": [PCA__, KPCA__, FACTOR_ANALYSIS__],
        "n_components": 5,
        "outliers": MAHA__,
        "clustering": [GMM__, KMEANS__],
        "regression": [GLM__],
        "family": GAUSSIAN_,
        "response": "infection",
        "centers": {
            "max_centers": 10,
            "n_centers": 10,
        },
        "infile": "data/single_cell_samples.tsv",
        "outfolder": "data/test",
        "meta": "data/meta_columns.tsv",
        "features": "data/feature_columns.tsv"
    }

    def setUp(self):
        unittest.TestCase.setUp(self)
        self._test_path = os.path.dirname(__file__)
        self._koios_path = os.path.dirname(self._test_path)
        self._test_file = os.path.join(self._test_path, "koios-test.config")
        self._koios = os.path.join(self._koios_path, "scripts", "koios")

    def test_dim_red(self):
        test_path = os.path.join(self._koios_path, "data", "test")
        for d in TestKoios.__CONFIG__["dimension_reduction"]:
            out = os.path.join(self._test_path, d + ".config")
            if not os.path.exists(test_path):
                os.mkdir(test_path)
            with open(out, "w") as fr, open(self._test_file, "r") as fh:
                for l in fh.readlines():
                    fr.write(l)
                fr.write("dimension_reduction: {}\n".format(d))
            pr = subprocess.run(
              ["./scripts/koios", "dimension_reduction", out, "local"])
            assert pr.returncode == 0
            os.remove(out)

    # def test_outliers(self):
    #     pr = subprocess.run(
    #       [self._koios, "outliers", self._test_file, "local"])
    #     assert pr.returncode == 0
    #
    # def test_clustering_fit(self):
    #     pr = subprocess.run(
    #       [self._koios, "clustering_fit", self._test_file, "local"])
    #     assert pr.returncode == 0
    #
    # def test_clustering_transform(self):
    #     pr = subprocess.run(
    #       [self._koios, "clustering_transform", self._test_file, "local"])
    #     assert pr.returncode == 0
    #
    # def test_regression(self):
    #     pr = subprocess.run(
    #       [self._koios, "regression", self._test_file, "local"])
    #     assert pr.returncode == 0
