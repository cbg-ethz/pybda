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

import click
import numpy
import scipy
from pyspark.mllib.linalg import DenseMatrix
from pyspark.mllib.linalg.distributed import RowMatrix

from koios.dimension_reduction import DimensionReduction
from koios.fit.lda_fit import LDAFit
from koios.spark.dataframe import join
from koios.stats.linalg import svd
from koios.stats.random import mtrand
from koios.stats.stats import center, decorrelate

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ICA(DimensionReduction):
    def __init__(self, spark, n_components, features, response):
        super().__init__(spark, features, scipy.inf, scipy.inf)
        self.__n_components = n_components
        self.__response = response
        numpy.random.seed(seed=233423)

    @property
    def response(self):
        return self.__response

    @property
    def n_components(self):
        return self.__n_components

    def fit(self, data):
        logger.info("Fitting ICA")
        X = self._center(data)
        X = self._whiten(X)
        w_init = decorrelate(mtrand(self.n_components, self.n_components))
        for i in range(self.max_iter):
            g, g_deriv = self.exp(X)
            K =  g.T.dot(X1) / p_ - g_wtx[:, numpy.newaxis] * W

    def exp(self, X):
        g = X.rows.map(lambda x: x * numpy.exp(-(x ** 2) / 2))
        g_ = X.rows.map(lambda x: (1 - x ** 2) * numpy.exp(-(x ** 2) / 2))
        gm = g_.computeColumnSummaryStatistics().mean()
        return g, gm


    def _whiten(self, X):
        s, v, _ = svd(X, len, X.numCols())
        K = (v.T / s)[:, :self.n_components] * X.numRows()
        K = DenseMatrix(K.numRows(), K.numCols(), K.flatten(), True)
        return X.multiply(K)

    def _center(self, data):
        X = self._feature_matrix(data)
        return RowMatrix(center(X))

    def _compute_eigens(self, SW, SB):
        logger.info("Computing eigen values")
        eval, evec = scipy.linalg.eig(scipy.linalg.inv(SW).dot(SB))
        eval = scipy.real(eval)
        sorted_idxs = scipy.argsort(-abs(eval))
        eval, evec = eval[sorted_idxs], evec[:, sorted_idxs]
        return eval, evec

    def transform(self, data, W):
        logger.info("Transforming data")
        W =  W[:, :self.n_components]
        logger.info(W)
        W = DenseMatrix(numRows=W.shape[0],
                        numCols=W.shape[1], isTransposed=True,
                        values=W.flatten())
        logger.info(W.toArray())
        X = self._row_matrix(data).multiply(W)
        data = join(data, X, self.spark)
        del X
        return data

    def fit_transform(self, data):
        logger.info("Running LDA ...")
        W, eval = self.fit(data)
        data = self.transform(data, W)
        return LDAFit(data, self.n_components, W, eval,
                      self.features, self.response)


@click.command()
@click.argument("discriminants", type=int)
@click.argument("file", type=str)
@click.argument("features", type=str)
@click.argument("response", type=str)
@click.argument("outpath", type=str)
def run(discriminants, file, features, response, outpath):
    """
    Fit a linear discriminant analysis to a data set.
    """

    from koios.util.string import drop_suffix
    from koios.logger import set_logger
    from koios.spark_session import SparkSession
    from koios.io.as_filename import as_logfile
    from koios.io.io import read_and_transmute, read_info

    outpath = drop_suffix(outpath, "/")
    set_logger(as_logfile(outpath))

    with SparkSession() as spark:
        try:
            features = read_info(features)
            data = read_and_transmute(
              spark, file, features, assemble_features=False)
            fl = LDA(spark, discriminants, features, response)
            fit = fl.fit_transform(data)
            fit.write_files(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
