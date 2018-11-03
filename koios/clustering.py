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
import pandas
import pathlib
from abc import abstractmethod

from koios.fit.clustering_fit import ClusteringFit
from koios.fit.clustering_transformed import ClusteringTransformed
from koios.globals import GMM__, FEATURES__, KMEANS__, TOTAL_VAR_, LOGLIK_
from koios.io.as_filename import as_loglikfile, as_ssefile
from koios.io.io import write_line
from koios.spark.features import n_features, split_vector
from koios.spark_model import SparkModel
from koios.stats.stats import loglik, sum_of_squared_errors

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Clustering(SparkModel):
    def __init__(self, spark, clusters, findbest, threshold, max_iter, kind):
        super().__init__(spark)

        self.__kind = kind
        if kind == GMM__:
            self.__name_components = "components"
            self.__algorithm_type = "mixture"
        else:
            self.__name_components = "clusters"
            self.__algorithm_type = "clustering"

        if clusters is not None and isinstance(clusters, str):
            clusters = list(map(int, clusters.split(",")))
            if findbest and len(clusters) > 1:
                raise ValueError(
                  "Cannot find optimal {} with multiple {}."
                  "Use only a single K or set findbest=false.".format(
                    self.__algorithm_type, self.__name_components))
            if findbest:
                clusters = clusters[0]

        self.__threshold = threshold
        self.__max_iter = max_iter
        self.__clusters = clusters
        self.__findbest = findbest

    @property
    def clusters(self):
        return self.__clusters

    @property
    def findbest(self):
        return self.__findbest

    @property
    def max_iter(self):
        return self.__max_iter

    @property
    def threshold(self):
        return self.__threshold

    @abstractmethod
    def fit_transform(self):
        pass

    def fit(self, data, precomputed_models_path=None, outfolder=None):
        n, p = data.count(), n_features(data, FEATURES__)
        logger.info("Using data with n={} and p={}".format(n, p))
        data = data.select(FEATURES__)
        tots = Clustering._totals(
          split_vector(data, FEATURES__), self.__type, outfolder)

        if self.findbest:
            return self._fit_recursive(
              data, n, p, tots,
              precomputed_models_path, outfolder)
        return self._fit_single(data, n, p, tots, outfolder)

    def transform(self, data, models=None, fit_folder=None):
        if fit_folder is None and models is None:
            raise ValueError("Provide either 'models' or a 'models_folder'")
        if fit_folder:
            fit = ClusteringFit.find_best_fit(fit_folder)
        return ClusteringTransformed(fit.transform(data))

    @staticmethod
    def _totals(data, type, outpath=None):
        if type == GMM__:
            f_file = as_loglikfile
            f = loglik
            column = TOTAL_VAR_
        elif type == KMEANS__:
            f_file = as_ssefile
            f = sum_of_squared_errors
            column = LOGLIK_
        else:
            raise ValueError("Please provide either '{}/{}'".format(
              GMM__, KMEANS__))

        if outpath:
            outf = f_file(outpath)
        else:
            outf = None
        if outf and pathlib.Path(outf).exists():
            logger.info("Loading totals file")
            tab = pandas.read_csv(outf, sep="\t")
            tot = tab[column][0]
        else:
            logger.info("Computing totals anew")
            tot = f(data)
            if outf:
                write_line("{}\n{}\n".format(column, tot), outf)
        logger.info("\t{}: {}".format(column, tot))
        return tot