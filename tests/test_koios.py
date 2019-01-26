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
        DIM_RED__: [PCA__, KPCA__, FACTOR_ANALYSIS__],
        REGRESSION__ :[GLM__, GBM__, FOREST__],
        N_COMPONENTS__: 2,
        CLUSTERING__: [GMM__, KMEANS__],
        N_CENTERS__: "2,3",
        META__: "data/meta_columns.tsv",
        FEATURES__: "data/feature_columns.tsv"
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

        self._gmm_file = os.path.join(self._test_path, "gmm.config")
        self._kmeans_file = os.path.join(self._test_path, "kmeans.config")

        self._gbm_binomial_file = os.path.join(self._test_path, "gbm_binomial.config")
        self._glm_binomial_file = os.path.join(self._test_path, "glm_binomial.config")
        self._forst_binomial_file = os.path.join(self._test_path, "forest_binomial.config")
        self._gbm_gauss_file = os.path.join(self._test_path, "gbm_gaussian.config")
        self._glm_gauss_file = os.path.join(self._test_path, "glm_gaussian.config")
        self._forst_gauss_file = os.path.join(self._test_path, "forest_gaussian.config")

        self._koios = os.path.join(self._koios_path, "scripts", "koios")
        self._create_dim_red_configs()
        self._create_regression_configs()

    def _recreate_test_folder(self):
        #if os.path.exists(self._test_out):
        #    shutil.rmtree(self._test_out)
        if not os.path.exists(self._test_out):
            os.mkdir(self._test_out)
            for f in [BINOMIAL_, GAUSSIAN_]:
                os.mkdir(os.path.join(self._test_out, f))


    def _create_dim_red_configs(self):
        for d in TestKoios.__CONFIG__[DIM_RED__]:
            out = os.path.join(self._test_path, d + ".config")
            with open(out, "w") as fr, open(self._test_file, "r") as fh:
                for l in fh.readlines():
                    fr.write(l)
                fr.write("{}: {}\n".format(DIM_RED__, d))
                fr.write("{}: {}\n".format(
                  N_COMPONENTS__, TestKoios.__CONFIG__[N_COMPONENTS__]))

    def _create_regression_configs(self):
        for d in TestKoios.__CONFIG__[REGRESSION__]:
            for f in [BINOMIAL_, GAUSSIAN_]:
                outfolder = os.path.join(self._test_out, f)
                out = os.path.join(self._test_path, d + "_" + f + ".config")
                with open(out, "w") as fr, open(self._test_file, "r") as fh:
                    for l in fh.readlines():
                        if l.startswith(OUTFOLDER__):
                            fr.write("{}: {}\n".format(OUTFOLDER__, outfolder))
                        else:
                            fr.write(l)
                    fr.write("{}: {}\n".format(REGRESSION__, d))
                    fr.write("{}: {}\n".format(FAMILY__, f))
                    if f == BINOMIAL_:
                        fr.write("{}: {}\n".format(RESPONSE__, "log_response"))
                    else:
                        fr.write("{}: {}\n".format(RESPONSE__, "response"))



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

    # def test_kpca(self):
    #     self._recreate_test_folder()
    #     pr = subprocess.run(
    #       [self._koios, "dimension-reduction", self._kpca_file, "local"])
    #     assert pr.returncode == 0


    # def test_kmeans(self):
    #     pr = subprocess.run(
    #       [self._koios, "clustering", self._gmm_file, "local"])
    #     assert pr.returncode == 0
    #
    # def test_kmeans(self):
    #     pr = subprocess.run(
    #       [self._koios, "clustering", self._kmeans_file, "local"])
    #     assert pr.returncode == 0

    #
    def test_glm(self):
        self._recreate_test_folder()
        pr = subprocess.run(
           [self._koios, "regression", self._glm_gauss_file, "local"])
        assert pr.returncode == 0
