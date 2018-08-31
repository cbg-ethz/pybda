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
import pyspark.sql.functions as func
from pyspark.ml.linalg import VectorUDT
from pyspark.mllib.linalg.distributed import RowMatrix, DenseMatrix
from pyspark.sql.functions import udf
from koios.dimension_reduction import DimensionReduction
from koios.factor_analysis_fit import FactorAnalysisFit
from koios.util.stats import svd, column_statistics

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class FactorAnalysis(DimensionReduction):

    def __init__(self, spark, threshold=1e-9, max_iter=100):
        super().__init__(spark, threshold, max_iter)

    @staticmethod
    def _tilde(X, psi_sqrt, n_sqrt):
        norm = psi_sqrt * n_sqrt
        return RowMatrix(X.rows.map(lambda x: x / norm))

    @staticmethod
    def _loglik(llconst, unexp_var, s, psi, n):
        ll = llconst + scipy.sum(scipy.log(s))
        ll += unexp_var + scipy.sum(scipy.log(psi))
        ll *= -n / 2.

        return ll

    @staticmethod
    def _update_factors(s, V, sqrt_psi):
        W = scipy.sqrt(scipy.maximum(s - 1., 0.))[:, scipy.newaxis] * V
        W *= sqrt_psi
        return W

    def _update_variance(self, var, W):
        psi = scipy.maximum(var - scipy.sum(W ** 2, axis=0), self.__threshold)
        return psi

    def _estimate(self, X, var, n_factors):
        n, p = X.numRows(), X.numCols()
        old_ll = -scipy.inf
        llconst = p * scipy.log(2. * scipy.pi) + n_factors
        psi = scipy.ones(p, dtype=scipy.float32)
        nsqrt = scipy.sqrt(n)
        logliks = []

        logger.info("\tcomputing factor analysis")
        for i in range(self.__max_iter):
            sqrt_psi = scipy.sqrt(psi) + self.__threshold
            s, V, unexp_var = svd(self._tilde(X, sqrt_psi, nsqrt), n_factors)
            s = s ** 2

            # factor updated
            W = self._update_factors(s, V, sqrt_psi)
            # loglik update
            ll = self._loglik(llconst, unexp_var, s, psi, n)
            logliks.append(ll)
            # variance update
            psi = self._update_variance(var, W)

            if scipy.abs(ll - old_ll) < 0.001:
                break
            old_ll = ll

        return W, logliks, psi

    def _transform(self, X, W, psi):
        logger.info("Transforming data")
        Ih = scipy.eye(len(W))
        Wpsi = W / psi
        cov_z = scipy.linalg.inv(Ih + scipy.dot(Wpsi, W.T))
        tmp = scipy.dot(Wpsi.T, cov_z)
        tmp_dense = DenseMatrix(
          numRows=tmp.shape[0], numCols=tmp.shape[1], values=tmp.flatten())

        as_ml = udf(lambda v: v.asML() if v is not None else None, VectorUDT())

        X = X.multiply(tmp_dense)
        X = self.__spark.createDataFrame(X.rows.map(lambda x: (x,)))
        X = X.withColumnRenamed("_1", "features")
        X = X.withColumn("features", as_ml("features"))

        return X

    def fit(self, data, n_factors):
        logger.info("Running factor analysis ...")
        X = data.rdd
        X, means, var = column_statistics(data)
        X = RowMatrix(X.rows.map(lambda x: x - means))
        W, ll, psi = self._estimate(X, var, n_factors)
        X = self._transform(X, W, psi)

        data = self._join(data, X)
        del X

        return FactorAnalysisFit(data, W, psi, ll)

    @staticmethod
    def _join(data, X):
        X = X.withColumn("row_index", func.monotonically_increasing_id())
        data = data.withColumn("row_index", func.monotonically_increasing_id())
        data = data.join(
          X["row_index", "features"], on=["row_index"]).drop("row_index")

        return data
