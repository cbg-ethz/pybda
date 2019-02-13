# Copyright (C) 2018 Simon Dirmeier
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

import click
import pyspark
import pyspark.ml.clustering

from pybda.clustering import Clustering
from pybda.fit.kmeans_fit import KMeansFit
from pybda.fit.kmeans_fit_profile import KMeansFitProfile
from pybda.fit.kmeans_transformed import KMeansTransformed
from pybda.globals import FEATURES__, KMEANS__
from pybda.spark.dataframe import dimension
from pybda.spark.features import split_vector

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class KMeans(Clustering):
    def __init__(self, spark, clusters, threshold=.01, max_iter=25):
        super().__init__(spark, clusters, threshold, max_iter, KMEANS__)

    def fit(self, data, outpath):
        n, p = dimension(data)
        data = data.select(FEATURES__)
        tot_var = self.tot_var(split_vector(data, FEATURES__), outpath)
        models = KMeansFitProfile()
        return self._fit(models, outpath, data, n, p, tot_var)

    def _fit_one(self, k, data, n, p, tot_var):
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


@click.command()
@click.argument("clusters", type=str)
@click.argument("file", type=str)
@click.argument("features", type=str)
@click.argument("outpath", type=str)
def run(clusters, file, features, outpath):
    """
    Fit a kmeans-clustering to a data set.
    """

    from pybda.io.as_filename import as_logfile
    from pybda.logger import set_logger
    from pybda.spark_session import SparkSession
    from pybda.util.string import drop_suffix
    from pybda.io.io import read_info, read_and_transmute

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
