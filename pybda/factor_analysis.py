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
import numpy
import pyspark.sql.functions as func
from pyspark.ml.linalg import VectorUDT
from pyspark.mllib.linalg.distributed import RowMatrix, DenseMatrix
from pyspark.sql.functions import udf

from pybda.dimension_reduction import DimensionReduction
from pybda.fit.factor_analysis_fit import FactorAnalysisFit
from pybda.stats.linalg import svd
from pybda.stats.stats import column_statistics, center

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FactorAnalysis(DimensionReduction):
    def __init__(self, spark, n_factors, features, threshold=1e-9, max_iter=25):
        super().__init__(spark, features, threshold, max_iter)
        self.__n_factors = n_factors

    @property
    def n_factors(self):
        return self.__n_factors

    def fit(self, data):
        logger.info("Fitting FA")
        X, _, var = self._preprocess_data(data)
        W, ll, psi = self._estimate(X, var, self.n_factors)
        return X, W, ll, psi

    def _preprocess_data(self, data):
        X = self._feature_matrix(data)
        means, var = column_statistics(X)
        X = RowMatrix(center(X, means=means))
        return X, means, var

    def _estimate(self, X, var, n_factors):
        n, p = X.numRows(), X.numCols()
        old_ll = -numpy.inf
        llconst = p * numpy.log(2. * numpy.pi) + n_factors
        psi = numpy.ones(p, dtype=numpy.float32)
        nsqrt = numpy.sqrt(n)
        logliks = []

        logger.info("Computing factor analysis")
        for i in range(self.max_iter):
            sqrt_psi = numpy.sqrt(psi) + self.threshold
            s, V, unexp_var = svd(self._tilde(X, sqrt_psi, nsqrt), n_factors)
            s = s**2

            # factor updated
            W = self._update_factors(s, V, sqrt_psi)
            # loglik update
            ll = self._loglik(llconst, unexp_var, s, psi, n)
            logliks.append(ll)
            # variance update
            psi = self._update_variance(var, W)

            if abs(ll - old_ll) < 0.001:
                break
            old_ll = ll

        return W, logliks, psi

    @staticmethod
    def _tilde(X, psi_sqrt, n_sqrt):
        norm = psi_sqrt * n_sqrt
        return RowMatrix(X.rows.map(lambda x: x / norm))

    @staticmethod
    def _update_factors(s, V, sqrt_psi):
        W = numpy.sqrt(numpy.maximum(s - 1., 0.))[:, numpy.newaxis] * V
        W *= sqrt_psi
        return W

    @staticmethod
    def _loglik(llconst, unexp_var, s, psi, n):
        ll = llconst + numpy.sum(numpy.log(s))
        ll += unexp_var + numpy.sum(numpy.log(psi))
        ll *= -n / 2.

        return ll

    def _update_variance(self, var, W):
        psi = numpy.maximum(var - numpy.sum(W**2, axis=0), self.threshold)
        return psi

    def transform(self, data, X, W, psi):
        logger.info("Transforming data")
        Ih = numpy.eye(len(W))
        Wpsi = W / psi
        cov_z = numpy.linalg.inv(Ih + numpy.dot(Wpsi, W.T))
        tmp = numpy.dot(Wpsi.T, cov_z)
        tmp_dense = DenseMatrix(numRows=tmp.shape[0], numCols=tmp.shape[1],
                                values=tmp.flatten())

        as_ml = udf(lambda v: v.asML() if v is not None else None, VectorUDT())

        X = X.multiply(tmp_dense)
        X = self.spark.createDataFrame(X.rows.map(lambda x: (x, )))
        X = X.withColumnRenamed("_1", "features")
        X = X.withColumn("features", as_ml("features"))

        data = self._join(data, X)
        del X

        return data

    def fit_transform(self, data):
        logger.info("Running factor analysis ...")
        X, W, ll, psi = self.fit(data)
        data = self.transform(data, X, W, psi)
        return FactorAnalysisFit(data, self.n_factors, W, psi, ll,
                                 self.features)

    @staticmethod
    def _join(data, X):
        X = X.withColumn("row_index", func.monotonically_increasing_id())
        data = data.withColumn("row_index", func.monotonically_increasing_id())
        data = data.join(X["row_index", "features"],
                         on=["row_index"]).drop("row_index")

        return data


@click.command()
@click.argument("factors", type=int)
@click.argument("file", type=str)
@click.argument("features", type=str)
@click.argument("outpath", type=str)
def run(factors, file, features, outpath):
    """
    Fit a factor analysis to a data set
    """

    from pybda.util.string import drop_suffix
    from pybda.logger import set_logger
    from pybda.spark_session import SparkSession
    from pybda.io.io import read_info, read_and_transmute
    from pybda.io.as_filename import as_logfile

    outpath = drop_suffix(outpath, "/")
    set_logger(as_logfile(outpath))

    with SparkSession() as spark:
        try:
            features = read_info(features)
            data = read_and_transmute(spark, file, features,
                                      assemble_features=False)
            fl = FactorAnalysis(spark, factors, features)
            fit = fl.fit_transform(data)
            fit.write_files(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
