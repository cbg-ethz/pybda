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
import pathlib

import click
import pandas
import pyspark
import pyspark.ml.clustering

from koios.clustering import Clustering
from koios.fit.kmeans_fit import KMeansFit
from koios.fit.kmeans_transformed import KMeansTransformed
from koios.globals import TOTAL_VAR_, FEATURES__, KMEANS__
from koios.io.as_filename import as_ssefile
from koios.io.io import write_line
from koios.fit.kmeans_fit_profile import KMeansFitProfile
from koios.spark.features import n_features, split_vector
from koios.stats.stats import sum_of_squared_errors

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class KMeans(Clustering):
    def __init__(self, spark, clusters, threshold=.01, max_iter=25):
        super().__init__(spark, clusters, threshold, max_iter, KMEANS__)

    def fit(self, data, outpath):
        n, p = data.count(), n_features(data, FEATURES__)
        logger.info("Using data with n={} and p={}".format(n, p))
        data = data.select(FEATURES__)
        tot_var = self._tot_var(split_vector(data, FEATURES__), outpath)
        models = KMeansFitProfile()
        for k in self.clusters:
            models[k] = self._fit(k, data, n, p, tot_var)
            models[k].write_files(outpath)
        models.write_files(outpath)
        return models

    def _fit(self, k, data, n, p, tot_var):
        logger.info("Clustering with K: {}".format(k))
        km = pyspark.ml.clustering.KMeans(k=k, seed=23)
        fit = km.fit(data)
        model = KMeansFit(data=None, fit=fit, k=k,
                          within_cluster_variance=fit.computeCost(data),
                          total_variance=tot_var, n=n, p=p, path=None)
        return model

    def transform(self, data, models, outpath):
        for k, fit in models:
            m = KMeansTransformed(fit.transform(data))
            m.write_files(outpath, k)

    def fit_transform(self, data, outpath):
        models = self.fit(data, outpath)
        self.transform(data, models, outpath)

    @staticmethod
    def _tot_var(data, outpath=None):
        if outpath:
            sse_file = as_ssefile(outpath)
        else:
            sse_file = None
        if sse_file and pathlib.Path(sse_file).exists():
            logger.info("Loading variance file")
            tab = pandas.read_csv(sse_file, sep="\t")
            sse = tab[TOTAL_VAR_][0]
        else:
            logger.info("Computing variance anew")
            sse = sum_of_squared_errors(data)
            if sse_file:
                write_line("{}\n{}\n".format(TOTAL_VAR_, sse), sse_file)
        logger.info("\t{}: {}".format(TOTAL_VAR_, sse))
        return sse


@click.command()
@click.argument("clusters", type=str)
@click.argument("file", type=str)
@click.argument("features", type=str)
@click.argument("outpath", type=str)
def run(clusters, file, features, outpath):
    """
    Fit a kmeans-clustering to a data set.
    """

    from koios.io.as_filename import as_logfile
    from koios.logger import set_logger
    from koios.spark_session import SparkSession
    from koios.util.string import drop_suffix
    from koios.io.io import read_info, read_and_transmute

    outfolder = drop_suffix(outpath, "/")
    set_logger(as_logfile(outpath))

    with SparkSession() as spark:
        try:
            features = read_info(features)
            data = read_and_transmute(spark, file, features)
            km = KMeans(spark, clusters, features)
            km.fit_transform(data, outfolder)
        except Exception as e:
            logger.error("Some error: {}".format(e))


if __name__ == "__main__":
    run()
