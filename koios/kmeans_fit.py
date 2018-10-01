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

import scipy

from koios.globals import WITHIN_VAR_, EXPL_VAR_, TOTAL_VAR_, K_, N_, PATH_, \
    P_, BIC_

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class KMeansFit:
    def __init__(self, data, fit, k,
                 within_cluster_variance, total_variance,
                 n, p, path=None):
        self.__data = data
        self.__fit = fit
        self.__n = n
        self.__p = p
        self.__k = k
        self.__within_cluster_variance = within_cluster_variance
        self.__total_variance = total_variance
        self.__explained_variance = 1 - within_cluster_variance / total_variance
        self.__bic = within_cluster_variance + scipy.log(n) * (k * p + 1)
        self.__path = path

    def transform(self, data):
        return self.__fit.transform(data)

    @property
    def explained_variance(self):
        return self.__explained_variance

    @property
    def within_cluster_variance(self):
        return self.__within_cluster_variance

    @property
    def total_variance(self):
        return self.__total_variance

    @property
    def data(self):
        return self.__data

    @property
    def K(self):
        return self.__k

    def write_files(self, outfolder):
        import os
        if not os.path.exists(outfolder):
            os.mkdir(outfolder)
        path = os.path.join(outfolder, KMeansFit._k_fit_path(self.K))
        self._write_fit(path)
        self._write_cluster_sizes(path)
        self._write_cluster_centers(path)
        self._write_statistics(path)

    @classmethod
    def as_statfile(cls, fit_folder, k):
        return os.path.join(
          fit_folder, KMeansFit._k_fit_path(k) + "_statistics.tsv")

    @classmethod
    def _k_fit_path(cls, k):
        return "kmeans-fit-K{}".format(k)

    def _write_fit(self, outfolder):
        logger.info("Writing cluster fit to: {}".format(outfolder))
        self.__fit.write().overwrite().save(outfolder)

    def _write_cluster_sizes(self, outfile):
        comp_files = outfile + "_cluster_sizes.tsv"
        logger.info("Writing cluster size file to: {}".format(comp_files))
        with open(comp_files, 'w') as fh:
            for c in self.__fit.summary.clusterSizes:
                fh.write("{}\n".format(c))

    def _write_cluster_centers(self, outfile):
        ccf = outfile + "_cluster_centers.tsv"
        logger.info("Writing cluster centers to: {}".format(ccf))
        with open(ccf, "w") as fh:
            fh.write("#Clustercenters\n")
            for center in self.__fit.clusterCenters():
                fh.write("\t".join(map(str, center)) + '\n')

    def _write_statistics(self, outfile):
        sse_file = outfile + "_statistics.tsv"
        logger.info("Writing SSE and BIC to: {}".format(sse_file))
        with open(sse_file, 'w') as fh:
            fh.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
              K_, WITHIN_VAR_, EXPL_VAR_, TOTAL_VAR_, BIC_, N_, P_, "path"))
            fh.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
              self.__k,
              self.__within_cluster_variance,
              self.__explained_variance,
              self.__total_variance,
              self.__bic,
              self.__n,
              self.__p,
              outfile))

    @classmethod
    def load_model(cls, statistics_file, load_fit=False):
        import pandas
        from pyspark.ml.clustering import KMeansModel
        logger.info(statistics_file)
        tab = pandas.read_csv(statistics_file, sep="\t")
        n, k, p = tab[N_][0], tab[K_][0], tab[P_][0]
        within_var = tab[WITHIN_VAR_][0]
        expl = tab[EXPL_VAR_][0]
        total_var = tab[TOTAL_VAR_][0]
        path = tab[PATH_][0]
        logger.info("Loading model:K={}, P={},"
                    " within_cluster_variance={}, "
                    "explained_variance={} from file={}"
                    .format(k, p, within_var, expl, statistics_file))
        fit = KMeansModel.load(path) if load_fit else None
        return KMeansFit(None, fit, k, within_var, total_var, n, p, path)

    @classmethod
    def find_best_fit(cls, fit_folder):
        import pandas
        from koios.kmeans_fit_profile import KMeansFitProfile
        profile_file = KMeansFitProfile.as_profilefile(fit_folder)
        tab = pandas.read_csv(profile_file, sep="\t")
        stat_file = KMeansFit.as_statfile(fit_folder, tab[K_].values[-1])
        return KMeansFit.load_model(stat_file, True)
