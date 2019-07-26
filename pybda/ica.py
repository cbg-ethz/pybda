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
import scipy
from pyspark.mllib.linalg import DenseMatrix
from pyspark.mllib.linalg.distributed import RowMatrix

from pybda.decorators import timing
from pybda.dimension_reduction import DimensionReduction
from pybda.fit.ica_fit import ICAFit
from pybda.fit.ica_transform import ICATransform
from pybda.spark.dataframe import join
from pybda.stats.linalg import svd, elementwise_product
from pybda.stats.random import mtrand
from pybda.stats.stats import center, gs_decorrelate, column_means

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ICA(DimensionReduction):
    def __init__(self, spark, n_components, features, max_iter=25,
                 thresh=1e-03):
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
        self._fit(data)
        return self

    @timing
    def _fit(self, data):
        logger.info("Fitting ICA..")
        X = self._preprocess_data(data)
        W, K = self._estimate(X)
        self.model = ICAFit(self.n_components, K.dot(W), self.features, W, K)
        return X, self.model

    def _preprocess_data(self, data):
        X = self._feature_matrix(data)
        self.__means = column_means(X)
        return RowMatrix(center(X, means=self.__means))

    @timing
    def _estimate(self, X):
        X_white, K = self._whiten(X)
        W = scipy.zeros(shape=(self.n_components, self.n_components))
        w_init = mtrand(self.n_components, self.n_components, seed=self.__seed)

        logger.info("Computing independent component analysis")
        for i in range(self.n_components):
            w = w_init[i, :].copy()
            w /= scipy.sqrt((w**2).sum())
            for _ in range(self.max_iter):
                w_new = self._compute_w_row(X_white, w, W, i)
                lim = scipy.absolute(scipy.absolute((w_new * w).sum()) - 1)
                w = w_new
                if lim < self.threshold:
                    break
            W[i, :] = w
        del X_white

        return W.T, K

    def _whiten(self, X):
        s, v, _ = svd(X, X.numCols())
        K = (v.T / s)[:, :self.n_components]
        S = K * scipy.sqrt(X.numRows())
        S = DenseMatrix(S.shape[0], S.shape[1], S.flatten(), True)
        return X.multiply(S), K

    def _compute_w_row(self, Xw, w, W, idx):
        g, gd = self._exp(Xw.multiply(DenseMatrix(len(w), 1, w)))
        w_new = column_means(elementwise_product(Xw, g, self.spark))
        del g
        w_new = w_new - gd * w
        w_new = gs_decorrelate(w_new, W, idx)
        w_new /= scipy.sqrt((w_new**2).sum())
        return w_new

    @staticmethod
    def _exp(X):
        g = X.rows.map(lambda x: x * scipy.exp(-(scipy.power(x, 2.0)) / 2.0))
        g_ = X.rows.map(lambda x: (1 - scipy.power(x, 2.0)) * scipy.exp(-(
            scipy.power(x, 2.0)) / 2.0))
        gm = column_means(g_).mean()
        return RowMatrix(g), gm

    def transform(self, data):
        X = self._feature_matrix(data)
        X = RowMatrix(center(X, self.__means))
        return ICATransform(self._transform(data, X), self.model)

    def _transform(self, data, X):
        logger.info("Transforming data")
        loadings = self.model.loadings.T
        L = DenseMatrix(numRows=loadings.shape[0], numCols=loadings.shape[1],
                        values=loadings.flatten(), isTransposed=True)
        data = join(data, X.multiply(L), self.spark)
        return data

    def fit_transform(self, data):
        X, _ = self._fit(data)
        return ICATransform(self._transform(data, X), self.model)


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
            trans = fl.fit_transform(data)
            trans.write(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
