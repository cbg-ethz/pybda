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
import glob
import logging
import pandas
import pathlib
from abc import abstractmethod

from koios.globals import GMM__, FEATURES__, TOTAL_VAR_
from koios.io.as_filename import as_ssefile
from koios.io.io import write_line
from koios.spark.features import n_features
from koios.spark_model import SparkModel
from koios.stats.stats import sum_of_squared_errors

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Clustering(SparkModel):
    def __init__(self, spark, clusters, threshold, max_iter, kind):
        super().__init__(spark)
        self.__kind = kind
        if kind == GMM__:
            self.__name_components = "components"
            self.__algorithm_type = "mixture"
        else:
            self.__name_components = "clusters"
            self.__algorithm_type = "clustering"
        if isinstance(clusters, str):
            clusters = list(map(int, clusters.split(",")))
        self.__threshold = threshold
        self.__max_iter = max_iter
        self.__clusters = clusters

    @property
    def clusters(self):
        return self.__clusters

    @property
    def max_iter(self):
        return self.__max_iter

    @property
    def threshold(self):
        return self.__threshold

    def fit_transform(self, data, outpath):
        models = self.fit(data, outpath)
        self.transform(data, models, outpath)

    @abstractmethod
    def fit(self):
        pass

    @staticmethod
    def _check_transform(models, fit_folder):
        if fit_folder is None and models is None:
            raise ValueError("Provide either 'models' or a 'models_folder'")

    def tot_var(self, data, outpath=None):
        if outpath:
            sse_file = as_ssefile(outpath)
        else:
            sse_file = None
        if sse_file and pathlib.Path(sse_file).exists():
            logger.info("Loading variance file")
            tab = pandas.read_csv(sse_file, sep="\t")
            sse = tab[TOTAL_VAR_][0]
        else:
            logger.info("Computing variance")
            sse = sum_of_squared_errors(data)
            if sse_file:
                write_line("{}\n{}\n".format(TOTAL_VAR_, sse), sse_file)
        logger.info("\t{}: {}".format(TOTAL_VAR_, sse))
        return sse

    def dimension(self, data):
        n, p = data.count(), n_features(data, FEATURES__)
        logger.info("Using data with n={} and p={}".format(n, p))
        return n, p

    def _fit(self, models, outpath, data, n, p, stat):
        for k in self.clusters:
            models[k] = self._fit_one(k, data, n, p, stat)
            models[k].write_files(outpath)
        models.write_files(outpath)
        return models
