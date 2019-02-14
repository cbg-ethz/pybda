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

import os
import shutil
import subprocess
import unittest

from pybda.globals import *


class TestPyBDA(unittest.TestCase):
    """
    Tests the command line tool by calling every method.
    """

    __CONFIG__ = {
        DIM_RED__: [PCA__, KPCA__, FACTOR_ANALYSIS__, ICA__, LDA__],
        REGRESSION__: [GLM__, GBM__, FOREST__],
        N_COMPONENTS__: 2,
        CLUSTERING__: [GMM__, KMEANS__],
        N_CENTERS__: "2,3"
    }

    def setUp(self):
        unittest.TestCase.setUp(self)
        self._test_path = os.path.dirname(__file__)
        self._pybda_path = os.path.dirname(self._test_path)
        self._test_out = os.path.join(self._pybda_path, "data", "test")
        self._test_file = os.path.join(self._test_path, "pybda-test.config")

        self._fa_file = os.path.join(self._test_path, "factor_analysis.config")
        self._pca_file = os.path.join(self._test_path, "pca.config")
        self._kpca_file = os.path.join(self._test_path, "kpca.config")
        self._ica_file = os.path.join(self._test_path, "ica.config")
        self._lda_file = os.path.join(self._test_path, "lda.config")

        self._gmm_file = os.path.join(self._test_path, "gmm.config")
        self._kmeans_file = os.path.join(self._test_path, "kmeans.config")

        self._gbm_binomial_file = os.path.join(self._test_path,
                                               "gbm_binomial.config")
        self._glm_binomial_file = os.path.join(self._test_path,
                                               "glm_binomial.config")
        self._forst_binomial_file = os.path.join(self._test_path,
                                                 "forest_binomial.config")
        self._gbm_gauss_file = os.path.join(self._test_path,
                                            "gbm_gaussian.config")
        self._glm_gauss_file = os.path.join(self._test_path,
                                            "glm_gaussian.config")
        self._forst_gauss_file = os.path.join(self._test_path,
                                              "forest_gaussian.config")
        self._pybda = os.path.join(self._pybda_path, "scripts", "pybda")
        self._create_dim_red_configs()
        self._create_regression_configs()
        self._create_clustering_configs()

    def _recreate_test_folder(self):
        if os.path.exists(self._test_out):
            shutil.rmtree(self._test_out)
        if not os.path.exists(self._test_out):
            os.mkdir(self._test_out)
            for f in [BINOMIAL_, GAUSSIAN_]:
                os.mkdir(os.path.join(self._test_out, f))

    def _create_dim_red_configs(self):
        for d in TestPyBDA.__CONFIG__[DIM_RED__]:
            out = os.path.join(self._test_path, d + ".config")
            with open(out, "w") as fr, open(self._test_file, "r") as fh:
                for l in fh.readlines():
                    fr.write(l)
                fr.write("{}: {}\n".format(DIM_RED__, d))
                fr.write("{}: {}\n".format(
                    N_COMPONENTS__, TestPyBDA.__CONFIG__[N_COMPONENTS__]))
                if d == LDA__:
                    fr.write("{}: {}\n".format(RESPONSE__, "Species"))

    def _create_clustering_configs(self):
        for d in TestPyBDA.__CONFIG__[CLUSTERING__]:
            out = os.path.join(self._test_path, d + ".config")
            with open(out, "w") as fr, open(self._test_file, "r") as fh:
                for l in fh.readlines():
                    fr.write(l)
                if d == KMEANS__:
                    fr.write("{}: {}\n".format(DIM_RED__, FACTOR_ANALYSIS__))
                    fr.write("{}: {}\n".format(N_COMPONENTS__, "3"))
                fr.write("{}: {}\n".format(CLUSTERING__, d))
                fr.write("{}: {}\n".format(N_CENTERS__,
                                           TestPyBDA.__CONFIG__[N_CENTERS__]))

    def _create_regression_configs(self):
        for d in TestPyBDA.__CONFIG__[REGRESSION__]:
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
        if os.path.exists(self._test_out):
            shutil.rmtree(self._test_out)
        fls = []
        for d in TestPyBDA.__CONFIG__[DIM_RED__] + TestPyBDA.__CONFIG__[
                CLUSTERING__]:
            out = os.path.join(self._test_path, d + ".config")
            fls.append(out)
        for d in TestPyBDA.__CONFIG__[REGRESSION__]:
            for f in [BINOMIAL_, GAUSSIAN_]:
                out = os.path.join(self._test_path, d + "_" + f + ".config")
                fls.append(out)
        for fl in fls:
            os.remove(fl)

    def test_test(self):
        assert 0 == 0

    def test_fa(self):
        self._recreate_test_folder()
        pr = subprocess.run(
            [self._pybda, "dimension-reduction", self._fa_file, "local"])
        assert pr.returncode == 0

    def test_pca(self):
        self._recreate_test_folder()
        pr = subprocess.run(
            [self._pybda, "dimension-reduction", self._pca_file, "local"])
        assert pr.returncode == 0

    def test_kpca(self):
        self._recreate_test_folder()
        pr = subprocess.run(
            [self._pybda, "dimension-reduction", self._kpca_file, "local"])
        assert pr.returncode == 0

    def test_ica(self):
        self._recreate_test_folder()
        pr = subprocess.run(
            [self._pybda, "dimension-reduction", self._ica_file, "local"])
        assert pr.returncode == 0

    def test_lda(self):
        self._recreate_test_folder()
        pr = subprocess.run(
            [self._pybda, "dimension-reduction", self._lda_file, "local"])
        assert pr.returncode == 0

    def test_kmeans(self):
        pr = subprocess.run(
            [self._pybda, "clustering", self._kmeans_file, "local"])
        assert pr.returncode == 0

    def test_gmm(self):
        pr = subprocess.run(
            [self._pybda, "clustering", self._gmm_file, "local"])
        assert pr.returncode == 0

    def test_glm_gaussian(self):
        self._recreate_test_folder()
        pr = subprocess.run(
            [self._pybda, "regression", self._glm_gauss_file, "local"])
        assert pr.returncode == 0

    def test_glm_binomial(self):
        self._recreate_test_folder()
        pr = subprocess.run(
            [self._pybda, "regression", self._glm_binomial_file, "local"])
        assert pr.returncode == 0

    def test_forest_gaussian(self):
        self._recreate_test_folder()
        pr = subprocess.run(
            [self._pybda, "regression", self._forst_gauss_file, "local"])
        assert pr.returncode == 0

    def test_forest_binomial(self):
        self._recreate_test_folder()
        pr = subprocess.run(
            [self._pybda, "regression", self._forst_binomial_file, "local"])
        assert pr.returncode == 0

    def test_gbm_gaussian(self):
        self._recreate_test_folder()
        pr = subprocess.run(
            [self._pybda, "regression", self._gbm_gauss_file, "local"])
        assert pr.returncode == 0

    def test_gbm_binomial(self):
        self._recreate_test_folder()
        pr = subprocess.run(
            [self._pybda, "regression", self._glm_binomial_file, "local"])
        assert pr.returncode == 0
