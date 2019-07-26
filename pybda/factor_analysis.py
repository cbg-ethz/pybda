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
import numpy
import pyspark.sql.functions as func
from pyspark.mllib.linalg.distributed import RowMatrix, DenseMatrix

from pybda.decorators import timing
from pybda.dimension_reduction import DimensionReduction
from pybda.fit.factor_analysis_fit import FactorAnalysisFit
from pybda.fit.factor_analysis_transform import FactorAnalysisTransform
from pybda.spark.dataframe import join
from pybda.stats.linalg import svd
from pybda.stats.stats import column_statistics, center

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FactorAnalysis(DimensionReduction):
    def __init__(self, spark, n_factors, features, threshold=1e-3, max_iter=25):
        super().__init__(spark, features, threshold, max_iter)
        self.__eps = 1e-09
        self.__n_factors = n_factors

    @property
    def n_factors(self):
        return self.__n_factors

    def fit(self, data):
        self._fit(data)
        return self

    @timing
    def _fit(self, data):
        logger.info("Fitting factor analysis..")
        X, _, var = self._preprocess_data(data)
        loadings, ll, psi = self._estimate(X, var, self.n_factors)
        self.model = FactorAnalysisFit(self.n_factors, loadings, psi, ll,
                                       self.features)
        return X, self.model

    @timing
    def _preprocess_data(self, data):
        X = self._feature_matrix(data)
        n = X.count()
        self.__means, var = column_statistics(X)
        var = var * (n - 1) / n
        X = RowMatrix(center(X, means=self.__means))
        return X, self.__means, var

    @timing
    def _estimate(self, X, var, n_factors):
        n, p = X.numRows(), X.numCols()
        old_ll = -numpy.inf
        llconst = p * numpy.log(2. * numpy.pi) + n_factors
        psi = numpy.ones(p, dtype=numpy.float32)
        nsqrt = numpy.sqrt(n)
        logliks = []

        logger.info("Computing factor analysis")
        for _ in range(self.max_iter):
            sqrt_psi = numpy.sqrt(psi) + self.__eps
            s, V, unexp_var = svd(self._tilde(X, sqrt_psi, nsqrt), n_factors)
            s = s ** 2
            W = self._update_factors(s, V, sqrt_psi)
            ll = self._loglik(llconst, unexp_var, s, psi, n)
            logliks.append(ll)
            psi = self._update_variance(var, W)
            if abs(ll - old_ll) < self.threshold:
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
        psi = numpy.maximum(var - numpy.sum(W**2, axis=0), self.__eps)
        return psi

    def transform(self, data):
        X = self._feature_matrix(data)
        X = RowMatrix(center(X, self.__means))
        return FactorAnalysisTransform(self._transform(data, X), self.model)

    def _transform(self, data, X):
        logger.info("Transforming data")
        W = self.model.loadings
        psi = self.model.error_vcov

        Ih = numpy.eye(len(W))
        Wpsi = W / psi
        cov_z = numpy.linalg.inv(Ih + numpy.dot(Wpsi, W.T))
        tmp = numpy.dot(Wpsi.T, cov_z)
        tmp_dense = DenseMatrix(numRows=tmp.shape[0], numCols=tmp.shape[1],
                                values=tmp.flatten(), isTransposed=True)
        X = X.multiply(tmp_dense)
        data = join(data, X, self.spark)
        del X

        return data

    def fit_transform(self, data):
        X, _ = self._fit(data)
        return FactorAnalysisTransform(self._transform(data, X), self.model)

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
            trans = fl.fit_transform(data)
            trans.write(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
