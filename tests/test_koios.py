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
        "n_components": 2,
        "clustering": [GMM__, KMEANS__],
        "regression": [GLM__],
        "family": GAUSSIAN_,
        "response": "infection",
        "n_centers": 2,
        "meta": "data/meta_columns.tsv",
        "features": "data/feature_columns.tsv"
    }

    def setUp(self):
        unittest.TestCase.setUp(self)
        self._test_path = os.path.dirname(__file__)
        self._koios_path = os.path.dirname(self._test_path)
        self._test_out = os.path.join(self._koios_path, "data", "test")
        self._test_file = os.path.join(self._test_path, "koios-test.config")
        self._fa_file = os.path.join(self._test_path, "factor_analysis.config")
        self._pca_file = os.path.join(self._test_path, "pca.config")
        self._kpca_file = os.path.join(self._test_path, "kpca.config")
        self._koios = os.path.join(self._koios_path, "scripts", "koios")
        self._create_dim_red_configs()

    def _recreate_test_folder(self):
        #if os.path.exists(self._test_out):
        #    shutil.rmtree(self._test_out)
        if not os.path.exists(self._test_out):
            print("asds")
            os.mkdir(self._test_out)

    def _create_dim_red_configs(self):
        for d in TestKoios.__CONFIG__[DIM_RED__]:
            out = os.path.join(self._test_path, d + ".config")
            with open(out, "w") as fr, open(self._test_file, "r") as fh:
                for l in fh.readlines():
                    fr.write(l)
                fr.write("{}: {}\n".format(DIM_RED__, d))
                fr.write("{}: {}".format(
                  N_COMPONENTS__, TestKoios.__CONFIG__[N_COMPONENTS__]))

    def tearDown(self):
        #shutil.rmtree(self._test_out)
        for d in TestKoios.__CONFIG__[DIM_RED__]:
            out = os.path.join(self._test_path, d + ".config")
            #os.remove(out)

    # def test_fa(self):
    #     self._recreate_test_folder()
    #     pr = subprocess.run([self._koios, "dimension-reduction",
    #                          self._fa_file, "local"])
    #     assert pr.returncode == 0
    # #
    # def test_pca(self):
    #     self._recreate_test_folder()
    #     pr = subprocess.run(
    #       [self._koios, "dimension-reduction", self._pca_file, "local"])
    #     assert pr.returncode == 0

    def test_kpca(self):
        self._recreate_test_folder()
        pr = subprocess.run(
          [self._koios, "dimension-reduction", self._kpca_file, "local"])
        assert pr.returncode == 0

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
