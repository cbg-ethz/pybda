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
from pyspark.mllib.linalg import DenseMatrix
from pyspark.mllib.linalg.distributed import RowMatrix

from koios.dimension_reduction import DimensionReduction
from koios.math.linalg import svd
from koios.math.stats import scale
from koios.pca_fit import PCAFit
from koios.spark.dataframe import join
from koios.spark.features import feature_columns
from koios.util.cast_as import as_rdd_of_array

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PCA(DimensionReduction):
    def __init__(self, spark, n_components):
        super().__init__(spark, numpy.inf, numpy.inf)
        self.__n_components = n_components

    @property
    def n_components(self):
        return self.__n_components

    @staticmethod
    def _preprocess_data(data):
        X = as_rdd_of_array(data.select(feature_columns(data)))
        X = RowMatrix(scale(X))
        return data

    @staticmethod
    def _compute_pcs(X):
        sds, loadings, _ = svd(X, X.numCols())
        sds = sds / numpy.sqrt(max(1, X.numRows() - 1))
        return X, loadings, sds

    def _fit(self, data):
        X = PCA._preprocess_data(data)
        X, loadings, sds = PCA._compute_pcs(X)
        return X, loadings, sds

    def _transform(self, data, X, loadings):
        logger.info("Transforming data")

        loadings = DenseMatrix(
          X.numCols(), self.__n_components,
          loadings[:self.__n_components].flatten()
        )
        X = X.multiply(loadings)
        data = join(data, X, self.spark)
        del X

        return data

    def fit(self):
        raise NotImplementedError()

    def transform(self):
        raise NotImplementedError()

    def fit_transform(self, data):
        logger.info("Running principal component analysis ...")
        X, loadings, sds = self._fit(data)
        data = self._transform(data, X, loadings)
        return PCAFit(data, self.__n_components, loadings, sds)


@click.command()
@click.argument("components", type=int)
@click.argument("file", type=str)
@click.argument("outpath", type=str)
def run(components, file, outpath):
    from koios.util.string import drop_suffix
    from koios.logger import set_logger
    from koios.spark_session import SparkSession
    from koios.io.io import read_tsv
    from koios.io.as_filename import as_logfile

    outpath = drop_suffix(outpath, "/")
    set_logger(as_logfile(outpath))

    with SparkSession() as spark:
        try:
            data = read_tsv(spark, file)
            data = to_double(data, feature_columns(data))
            data = fill_na(data)

            fl = PCA(spark, components)
            fit = fl.fit_transform(data)
            fit.write_files(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
