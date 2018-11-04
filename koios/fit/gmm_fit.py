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


import logging
import os

import numpy
import scipy

from koios.fit.clustering_fit import ClusteringFit
from koios.globals import K_, P_, N_, PATH_, NULL_BIC_, BIC_, LOGLIK_, \
    NULL_LOGLIK_
from koios.io.io import mkdir

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GMMFit(ClusteringFit):
    def __init__(self, data, fit, k, mixing_weights,
                 estimates, loglik, null_loglik,
                 n, p, path=None):
        super().__init__(data, fit, n, p, k)
        self.__mixing_weights = mixing_weights
        self.__estimates = estimates
        self.__loglik = loglik
        self.__null_loglik = null_loglik
        self.__n_params = k * p + k * p * (p + 1) / 2 + k - 1
        self.__null_n_params = p + p * (p + 1) / 2
        self.__bic = scipy.log(n) * self.__n_params - \
                     2 * self.__loglik
        self.__null_bic = scipy.log(n) * self.__null_n_params - \
                          2 * self.__null_loglik
        self.__path = path

    @property
    def bic(self):
        return self.__bic

    @property
    def loglik(self):
        return self.__loglik

    @property
    def null_loglik(self):
        return self.__null_loglik

    @property
    def null_bic(self):
        return self.__null_bic

    def write_files(self, outfolder):
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
        vars = self.__estimates.select("cov").toPandas().values
        for i in range(self.__estimates.count()):
            ccm = outfile + "_means_{}.tsv".format(i)
            ccv = outfile + "_variances_{}.tsv".format(i)
            numpy.savetxt(ccm, means[i][0].values, delimiter="\t")
            numpy.savetxt(ccv, vars[i][0].values, delimiter="\t")

    def _write_statistics(self, outfile):
        ll_file = outfile + "_statistics.tsv"
        logger.info("Writing LogLik and BIC to: {}".format(ll_file))
        with open(ll_file, 'w') as fh:
            fh.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
              K_, LOGLIK_, BIC_, NULL_LOGLIK_, NULL_BIC_, N_, P_, "path"))
            fh.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
              self.k,
              self.__loglik,
              self.__bic,
              self.__null_loglik,
              self.__null_bic,
              self.n,
              self.p,
              outfile))

    @classmethod
    def load_model(cls, statistics_file, load_fit=False):
        import pandas
        from pyspark.ml.clustering import GaussianMixtureModel
        logger.info(statistics_file)
        tab = pandas.read_csv(statistics_file, sep="\t")
        n, k, p = tab[N_][0], tab[K_][0], tab[P_][0]
        bic = tab[BIC_][0]
        loglik = tab[LOGLIK_][0]
        null_loglik = tab[NULL_LOGLIK_][0]
        path = tab[PATH_][0]
        logger.info("Loading model:K={}, P={},"
                    " loglik={}, "
                    "bic={} from file={}"
                    .format(k, p, loglik, bic, statistics_file))
        fit = GaussianMixtureModel.load(path) if load_fit else None
        return GMMFit(None, fit, k, None, None, loglik, null_loglik, n, p, path)

    @classmethod
    def find_best_fit(cls, fit_folder):
        import pandas
        from koios.fit.gmm_fit_profile import GMMFitProfile
        profile_file = GMMFitProfile.as_profilefile(fit_folder)
        tab = pandas.read_csv(profile_file, sep="\t")
        stat_file = GMMFit.as_statfile(fit_folder, tab[K_].values[-1])
        return GMMFit.load_model(stat_file, True)
