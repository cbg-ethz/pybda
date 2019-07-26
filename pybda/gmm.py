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

import click
import pyspark
import pyspark.ml.clustering
import scipy

from pybda.clustering import Clustering
from pybda.decorators import timing
from pybda.fit.gmm_fit import GMMFit
from pybda.fit.gmm_fit_profile import GMMFitProfile
from pybda.fit.gmm_transformed import GMMTransformed
from pybda.globals import RESPONSIBILITIES__, GMM__, FEATURES__
from pybda.spark.dataframe import dimension

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GMM(Clustering):
    def __init__(self, spark, clusters, threshold=scipy.inf, max_iter=25):
        super().__init__(spark, clusters, threshold, max_iter, GMM__)

    @timing
    def fit(self, data, outpath=None):
        n, p = dimension(data)
        data = data.select(FEATURES__)
        self.model = self._fit(GMMFitProfile(), outpath, data, n, p, scipy.nan)
        return self

    @staticmethod
    @timing
    def _fit_one(k, data, n, p, stat):
        logger.info("Clustering with K: {}".format(k))
        gmm = pyspark.ml.clustering.GaussianMixture(
            k=k, seed=23, probabilityCol=RESPONSIBILITIES__)
        fit = gmm.fit(data)
        model = GMMFit(data=None, fit=fit, k=k, mixing_weights=fit.weights,
                       estimates=fit.gaussiansDF,
                       loglik=fit.summary.logLikelihood, n=n, p=p, path=None)
        return model

    def write(self, data, outpath=None):
        for k, fit in self.model:
            m = GMMTransformed(fit.transform(data))
            if outpath:
                m.write(outpath, k)


@click.command()
@click.argument("clusters", type=str)
@click.argument("file", type=str)
@click.argument("features", type=str)
@click.argument("outpath", type=str)
def run(clusters, file, features, outpath):
    """
    Fit a gmm to a data set.
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
            fit = GMM(spark, clusters, features)
            fit = fit.fit(data, outfolder)
            fit.write(data, outfolder)
        except Exception as e:
            logger.error("Some error: {}".format(e))


if __name__ == "__main__":
    run()
