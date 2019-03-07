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

import logging
import os

import numpy
import scipy

from pybda.fit.clustering_fit import ClusteringFit
from pybda.globals import K_, P_, N_, BIC_, LOGLIK_
from pybda.io.io import mkdir

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GMMFit(ClusteringFit):
    def __init__(self, data, fit, k, mixing_weights, estimates, loglik, n, p,
                 path=None):
        super().__init__(data, fit, n, p, k)
        self.__mixing_weights = mixing_weights
        self.__estimates = estimates
        self.__loglik = loglik
        self.__n_params = k * p + k * p * (p + 1) / 2 + k - 1
        self.__bic = scipy.log(n) * self.__n_params - 2 * self.__loglik
        self.__path = path

    def __str__(self):
        return "{}\t".format(self.k) + \
               "{}\t".format(self.__loglik) + \
               "{}\t".format(self.__bic) + \
               "\n"

    @staticmethod
    def header():
        return "k\t" \
               "{}\t".format(LOGLIK_) + \
               "{}\t".format(BIC_) + \
               "\n"

    @property
    def n_params(self):
        return self.__n_params

    @property
    def weights(self):
        return self.__mixing_weights

    @property
    def estimates(self):
        return self.__estimates

    @property
    def values(self):
        return {K_: self.k, LOGLIK_: self.__loglik, BIC_: self.__bic}

    @property
    def bic(self):
        return self.__bic

    @property
    def loglik(self):
        return self.__loglik

    def write(self, outfolder):
        mkdir(outfolder)
        path = os.path.join(outfolder, self._k_fit_path(self.k))
        self._write_fit(path)
        self._write_cluster_sizes(path)
        self._write_estimates(path)
        self._write_statistics(path)

    def _k_fit_path(self, k):
        return "gmm-fit-K{}".format(k)

    def _write_estimates(self, outfile):
        logger.info("Writing cluster weights/means/variances")
        ccw = outfile + "_mixing_weights.tsv"
        numpy.savetxt(ccw, self.__mixing_weights, delimiter="\t")
        means = self.__estimates.select("mean").toPandas().values
        varis = self.__estimates.select("cov").toPandas().values
        for i in range(self.__estimates.count()):
            ccm = outfile + "_means_{}.tsv".format(i)
            ccv = outfile + "_variances_{}.tsv".format(i)
            numpy.savetxt(ccm, means[i][0].values, delimiter="\t")
            numpy.savetxt(ccv, varis[i][0].toArray(), delimiter="\t")

    def _write_statistics(self, outfile):
        ll_file = outfile + "_statistics.tsv"
        logger.info("Writing LogLik and BIC to: {}".format(ll_file))
        with open(ll_file, 'w') as fh:
            fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(K_, LOGLIK_, BIC_, N_,
                                                       P_, "path"))
            fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                self.k, self.__loglik, self.__bic, self.n, self.p, outfile))
