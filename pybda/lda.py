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
import scipy
from pyspark.mllib.linalg import DenseMatrix
from pyspark.mllib.linalg.distributed import RowMatrix

from pybda.dimension_reduction import DimensionReduction
from pybda.fit.lda_fit import LDAFit
from pybda.spark.dataframe import join
from pybda.spark.features import distinct
from pybda.stats.stats import within_group_scatter, covariance_matrix

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LDA(DimensionReduction):
    def __init__(self, spark, n_components, features, response):
        super().__init__(spark, features, scipy.inf, scipy.inf)
        self.__n_components = n_components
        self.__response = response

    @property
    def response(self):
        return self.__response

    @property
    def n_components(self):
        return self.__n_components

    def fit(self, data):
        logger.info("Fitting LDA")
        targets = distinct(data, self.__response)
        SW = within_group_scatter(data, self.features, self.response, targets)
        SB = covariance_matrix(self._row_matrix(data)) * (data.count() - 1) - SW
        eval, evec = self._compute_eigens(SW, SB)
        return evec, eval

    def _row_matrix(self, data):
        return RowMatrix(self._feature_matrix(data))

    def _compute_eigens(self, SW, SB):
        logger.info("Computing eigen values")
        eval, evec = scipy.linalg.eig(scipy.linalg.inv(SW).dot(SB))
        eval = scipy.real(eval)
        sorted_idxs = scipy.argsort(-abs(eval))
        eval, evec = eval[sorted_idxs], evec[:, sorted_idxs]
        return eval, evec

    def transform(self, data, W):
        logger.info("Transforming data")
        W = W[:, :self.n_components]
        W = DenseMatrix(numRows=W.shape[0], numCols=W.shape[1],
                        isTransposed=True, values=W.flatten())
        X = self._row_matrix(data).multiply(W)
        data = join(data, X, self.spark)
        del X
        return data

    def fit_transform(self, data):
        logger.info("Running LDA ...")
        W, eigen_vals = self.fit(data)
        data = self.transform(data, W)
        return LDAFit(data, self.n_components, W, eigen_vals, self.features,
                      self.response)


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
            fl = LDA(spark, discriminants, features, response)
            fit = fl.fit_transform(data)
            fit.write_files(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
