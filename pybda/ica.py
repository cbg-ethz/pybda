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
import scipy
from pyspark.mllib.linalg import DenseMatrix
from pyspark.mllib.linalg.distributed import RowMatrix

from pybda.dimension_reduction import DimensionReduction
from pybda.fit.ica_fit import ICAFit
from pybda.spark.dataframe import join
from pybda.stats.linalg import svd, elementwise_product
from pybda.stats.random import mtrand
from pybda.stats.stats import center, gs_decorrelate, column_mean

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ICA(DimensionReduction):
    def __init__(self, spark, n_components, features, max_iter=25, thresh=1e-03):
        super().__init__(spark, features, thresh, max_iter)
        self.__n_components = n_components
        self.__seed = 23

    @property
    def response(self):
        return self.__response

    @property
    def n_components(self):
        return self.__n_components

    def fit(self, data):
        logger.info("Fitting ICA")
        X = self._center(data)
        W, K = self._fit(X)
        return X, K.dot(W)

    def _fit(self, X):
        print("test")
        Xw, K = self._whiten(X)
        W = scipy.zeros(shape=(self.n_components, self.n_components))
        w_init = mtrand(self.n_components, self.n_components, seed=self.__seed)

        for c in range(self.n_components):
            w = w_init[c, :].copy()
            w /= scipy.sqrt((w**2).sum())
            print("w", w)
            for _ in range(self.max_iter):
                g, gd = self.exp(Xw.multiply(DenseMatrix(len(w), 1, w)))
                w1 = column_mean(elementwise_product(Xw, g, self.spark))
                del g
                w1 = w1 - gd * w
                w1 = gs_decorrelate(w1, W, c)
                w1 /= scipy.sqrt((w1**2).sum())
                lim = scipy.absolute(scipy.absolute((w1 * w).sum()) - 1)
                w = w1
                if lim < self.threshold:
                    break
            W[c, :] = w
        del Xw
        print("W", W)
        return W, K

    @staticmethod
    def exp(X):
        g = X.rows.map(lambda x: x * scipy.exp(-(scipy.power(x, 2.0)) / 2.0))
        g_ = X.rows.map(lambda x: (1 - scipy.power(x, 2.0)) *
                                  scipy.exp(-(scipy.power(x, 2.0)) / 2.0))
        gm = column_mean(g_).mean()
        return RowMatrix(g), gm

    def _whiten(self, X):
        s, v, _ = svd(X, X.numCols())
        K = (v.T / s)[:, :self.n_components] * scipy.sqrt(X.numRows())
        K = DenseMatrix(K.shape[0], K.shape[1], K.flatten(), True)
        return X.multiply(K), K.toArray()

    def _center(self, data):
        X = self._feature_matrix(data)
        return RowMatrix(center(X))

    def transform(self, data, X, unmixing):
        logger.info("Transforming data")
        L = DenseMatrix(numRows=unmixing.shape[0],
                        numCols=unmixing.shape[1],
                        values=unmixing.flatten())
        data = join(data, X.multiply(L), self.spark)
        del X
        return data

    def fit_transform(self, data):
        logger.info("Running ICA ...")
        X, unmixing = self.fit(data)
        data = self.transform(data, X, unmixing)
        return ICAFit(data, self.n_components, unmixing, self.features)


@click.command()
@click.argument("components", type=int)
@click.argument("file", type=str)
@click.argument("features", type=str)
@click.argument("outpath", type=str)
def run(components, file, features, outpath):
    """
    Fit a linear discriminant analysis to a data set.
    """

    from pybda.util.string import drop_suffix
    from pybda.logger import set_logger
    from pybda.spark_session import SparkSession
    from pybda.io.as_filename import as_logfile
    from pybda.io.io import read_and_transmute, read_info

    outpath = drop_suffix(outpath, "/")
    set_logger(as_logfile(outpath))

    with SparkSession() as spark:
        try:
            features = read_info(features)
            data = read_and_transmute(spark, file, features,
                                      assemble_features=False)
            fl = ICA(spark, components, features)
            fit = fl.fit_transform(data)
            fit.write_files(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
