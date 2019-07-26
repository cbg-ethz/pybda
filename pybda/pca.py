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
import scipy
from pyspark.mllib.linalg import DenseMatrix
from pyspark.mllib.linalg.distributed import RowMatrix

from pybda.decorators import timing
from pybda.dimension_reduction import DimensionReduction
from pybda.fit.pca_fit import PCAFit
from pybda.fit.pca_transform import PCATransform
from pybda.spark.dataframe import join
from pybda.stats.linalg import svd
from pybda.stats.stats import scale

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PCA(DimensionReduction):
    def __init__(self, spark, n_components, features):
        super().__init__(spark, features, scipy.inf, scipy.inf)
        self.__n_components = n_components

    @property
    def n_components(self):
        return self.__n_components

    def fit(self, data):
        self._fit(data)
        return self

    @timing
    def _fit(self, data):
        logger.info("Fitting PCA")
        X = self._preprocess_data(data)
        loadings, sds = self._compute_pcs(X)
        self.model = PCAFit(self.n_components, loadings, sds, self.features)
        return X, self.model

    @timing
    def _preprocess_data(self, data):
        if isinstance(data, pyspark.sql.DataFrame):
            X = self._feature_matrix(data)
        else:
            X = data.rows
        X, self.__means, self.__vars = scale(X)
        return RowMatrix(X)

    @staticmethod
    @timing
    def _compute_pcs(X):
        sds, loadings, _ = svd(X)
        sds = sds / scipy.sqrt(max(1, X.numRows() - 1))
        return loadings, sds

    def _setup_matrix_for_transform(self, data):
        X, _, _ = scale(self._feature_matrix(data), self.__means, self.__vars)
        X = RowMatrix(X)
        return X

    def transform(self, data):
        X = self._setup_matrix_for_transform(data)
        return PCATransform(self._transform(data, X), self.model)

    def _transform(self, data, X):
        logger.info("Transforming data")
        loadings = self.model.loadings[:self.n_components]
        loadings = DenseMatrix(X.numCols(),
                               self.n_components,
                               loadings.flatten())
        X = X.multiply(loadings)
        data = join(data, X, self.spark)
        del X
        return data

    def fit_transform(self, data):
        X, _ = self._fit(data)
        return PCATransform(self._transform(data, X), self.model)


@click.command()
@click.argument("components", type=int)
@click.argument("file", type=str)
@click.argument("features", type=str)
@click.argument("outpath", type=str)
def run(components, file, features, outpath):
    """
    Fit a PCA to a data set.
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
            data = read_and_transmute(
              spark, file, features, assemble_features=False)
            fl = PCA(spark, components, features)
            trans = fl.fit_transform(data)
            trans.write(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
