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
import scipy
from pyspark.mllib.linalg import DenseMatrix
from pyspark.mllib.linalg.distributed import RowMatrix

from koios.dimension_reduction import DimensionReduction
from koios.fit.pca_fit import PCAFit
from koios.spark.dataframe import join
from koios.stats.linalg import svd
from koios.stats.stats import scale
from koios.util.cast_as import as_rdd_of_array

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PCA(DimensionReduction):
    def __init__(self, spark, features, n_components):
        super().__init__(spark, features, scipy.inf, scipy.inf)
        self.__n_components = n_components

    @property
    def n_components(self):
        return self.__n_components

    def _preprocess_data(self, data):
        X = self._feature_matrix(data)
        return RowMatrix(scale(X))

    @staticmethod
    def _compute_pcs(X):
        sds, loadings, _ = svd(X, X.numCols())
        sds = sds / scipy.sqrt(max(1, X.numRows() - 1))
        return loadings, sds

    def fit(self, data):
        X = PCA._preprocess_data(data)
        loadings, sds = PCA._compute_pcs(X)
        return X, loadings, sds

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
        logger.info("Running principal component analysis ...")
        X, loadings, sds = self.fit(data)
        data = self.transform(data, X, loadings)
        return PCAFit(data, self.__n_components, loadings, sds)


@click.command()
@click.argument("components", type=int)
@click.argument("file", type=str)
@click.argument("features", type=str)
@click.argument("outpath", type=str)
def run(components, file, features, outpath):
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
            data = read_and_transmute(spark, file, features,
                                      assemble_features=False)
            fl = PCA(spark, components, features)
            fit = fl.fit_transform(data)
            fit.write_files(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
