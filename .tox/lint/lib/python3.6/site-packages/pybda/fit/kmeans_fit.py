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

import scipy

from pybda.fit.clustering_fit import ClusteringFit
from pybda.globals import WITHIN_VAR_, EXPL_VAR_, TOTAL_VAR_,\
    K_, N_, P_, BIC_
from pybda.io.io import mkdir

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class KMeansFit(ClusteringFit):
    def __init__(self, data, fit, k, within_cluster_variance, total_variance, n,
                 p, path=None):
        super().__init__(data, fit, n, p, k)
        self.__within_cluster_variance = within_cluster_variance
        self.__total_variance = total_variance
        self.__explained_variance = 1 - within_cluster_variance / total_variance
        self.__bic = within_cluster_variance + scipy.log(n) * (k * p + 1)
        self.__path = path

    def __str__(self):
        return "{}\t".format(self.k) + \
               "{}\t".format(self.__within_cluster_variance) + \
               "{}\t".format(self.__explained_variance) + \
               "{}\t".format(self.__total_variance) + \
               "{}\t".format(self.__bic) + \
               "\n"

    @staticmethod
    def header():
        return "k\t" \
               "{}\t".format(WITHIN_VAR_) + \
               "{}\t".format(EXPL_VAR_) + \
               "{}\t".format(TOTAL_VAR_) + \
               "{}\t".format(BIC_) + \
               "\n"

    @property
    def values(self):
        return {
            K_: self.k,
            WITHIN_VAR_: self.__within_cluster_variance,
            EXPL_VAR_: self.__explained_variance,
            TOTAL_VAR_: self.__total_variance,
            BIC_: self.__bic
        }

    @property
    def bic(self):
        return self.__bic

    @property
    def explained_variance(self):
        return self.__explained_variance

    @property
    def within_cluster_variance(self):
        return self.__within_cluster_variance

    @property
    def total_variance(self):
        return self.__total_variance

    def write(self, outfolder):
        mkdir(outfolder)
        path = os.path.join(outfolder, self._k_fit_path(self.k))
        self._write_fit(path)
        self._write_cluster_sizes(path)
        self._write_cluster_centers(path)
        self._write_statistics(path)

    def _k_fit_path(self, k):
        return "kmeans-fit-K{}".format(k)

    def _write_cluster_centers(self, outfile):
        ccf = outfile + "_cluster_centers.tsv"
        logger.info("Writing cluster centers to: {}".format(ccf))
        with open(ccf, "w") as fh:
            fh.write("#Clustercenters\n")
            for center in self.fit.clusterCenters():
                fh.write("\t".join(map(str, center)) + '\n')

    def _write_statistics(self, outfile):
        sse_file = outfile + "_statistics.tsv"
        logger.info("Writing SSE and BIC to: {}".format(sse_file))
        with open(sse_file, 'w') as fh:
            fh.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
                K_, WITHIN_VAR_, EXPL_VAR_, TOTAL_VAR_, BIC_, N_, P_, "path"))
            fh.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
                self.k, self.__within_cluster_variance,
                self.__explained_variance, self.__total_variance, self.__bic,
                self.n, self.p, outfile))
