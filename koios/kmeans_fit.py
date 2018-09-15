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
import scipy

from koios.globals import WITHIN_VAR, EXPL_VAR, TOTAL_VAR
from koios.io.as_filename import as_ssefile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class KMeansFit:
    def __init__(self, data, fit, k,
                 within_cluster_variance, total_variance,
                 n, p):
        self.__data = data
        self.__fit = fit
        self.__k = k
        self.__within_cluster_variance = within_cluster_variance
        self.__total_variance = total_variance
        self.__n = n
        self.__p = p
        self.__explained_variance = 1 - within_cluster_variance / total_variance
        self.__bic = within_cluster_variance + scipy.log(n) * (k * p + 1)

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
        self._write_sse(as_ssefile(outfolder))
        self._write_fit(self._k_fit_path(outfolder))
        self._write_cluster_sizes(self._k_fit_path(outfolder))
        self._write_cluster_centers(self._k_fit_path(outfolder))
        self._write_statistics(self._k_fit_path(outfolder))

    def _write_sse(self, outfile):
        logger.info("Writing SSEs to: {}".format(outfile))
        with open(outfile, 'w') as fh:
            fh.write("SSE\n{}\n".format(self.__within_cluster_variance))

    def k_fit_path(self, outpath):
        return outpath + "-K{}".format(self.K)

    def _write_fit(self, outfolder):
        logger.info("Writing cluster fit to: {}".format(outfolder))
        self.__fit.write().overwrite().save(outfolder)

    def _write_cluster_sizes(self, outfile):
        comp_files = outfile + "_cluster_sizes.tsv"
        logger.info("Writing cluster size file to: {}".format(comp_files))
        with open(comp_files + "_cluster_sizes.tsv", 'w') as fh:
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
            fh.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
              "K", WITHIN_VAR, EXPL_VAR, TOTAL_VAR, "BIC", "N", "P"))
            fh.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
              self.__k,
              self.__within_cluster_variance,
              self.__explained_variance,
              self.__total_variance,
              self.__bic,
              self.__n, self.__p))

    @classmethod
    def read_model_from_file(cls, file):
        import pandas
        tab = pandas.read_csv(file, sep="\t")
        within_var = tab[WITHIN_VAR][0]
        expl = tab[EXPL_VAR][0]
        total_var = tab[TOTAL_VAR][0]
        n, k, p = tab["N"][0] , tab["K"][0], tab["P"][0]
        logger.info("Loading model:K={}, P={},"
                    " within_cluster_variance={}, "
                    "explained_variance={} from file={}"
                    .format(k, p, within_var, expl, file))
        return KMeansFit(None, None, k, within_var, total_var, n, p)
