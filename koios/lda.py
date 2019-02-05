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
import scipy
from pyspark.mllib.linalg import DenseMatrix
from pyspark.mllib.linalg.distributed import RowMatrix

from koios.dimension_reduction import DimensionReduction
from koios.fit.pca_fit import PCAFit
from koios.spark.dataframe import join
from koios.spark.features import distinct
from koios.stats.linalg import svd
from koios.stats.stats import scale, column_mean, group_mean, \
    within_group_scatter, covariance_matrix

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
        self._fit(data)
        return X, loadings, sds

    def _fit(self, data):
        targets = distinct(data, self.__response)
        means = column_mean(self._feature_matrix(data))
        group_means = group_mean(data, targets, self.response, self.features)
        SW = within_group_scatter(data, self.features, self.response, targets)
        SB = covariance_matrix(self._row_matrix(data)) * (data.count() - 1) - SW
        eval, evec = self._compute_eigens(SW, SB)
        W = evec[:, :self.n_components]

        return W, eval, evec


    def _row_matrix(self, data):
        return RowMatrix(self._feature_matrix(data))

    def _compute_eigens(self, SW, SB):
        logger.info("Computing eigen values")
        eval, evec = scipy.linalg.eig(scipy.linalg.inv(SW).dot(SB))
        sorted_idxs = scipy.argsort(-abs(eval))
        eval, evec = eval[sorted_idxs], evec[:,sorted_idxs]
        return eval, evec

    def transform(self, data, X, loadings):
        logger.info("Transforming data")
        loadings = DenseMatrix(
          X.numCols(), self.n_components,
          loadings[:self.n_components].flatten()
        )
        X = X.multiply(loadings)
        data = join(data, X, self.spark)
        del X
        return data

    def fit_transform(self, data):
        logger.info("Running latent dirichlet allocation ...")
        X, loadings, sds = self.fit(data)
        data = self.transform(data, X, loadings)
        return PCAFit(data, self.n_components, loadings, sds, self.features)


@click.command()
@click.argument("components", type=int)
@click.argument("file", type=str)
@click.argument("features", type=str)
@click.argument("response", type=str)
@click.argument("outpath", type=str)
@click.option("-p", "--predict", default="None")
def run(components, file, features, response, outpath, predict):
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
            fl = LDA(spark, components, features, response)
            fit = fl.fit_transform(data)
            fit.write_files(outpath)
            if pathlib.Path(predict).exists():
                pre_data = read_and_transmute(
                  spark, predict, features, drop=False)
                pre_data = fit.predict(pre_data)
                pre_data.write_files(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
