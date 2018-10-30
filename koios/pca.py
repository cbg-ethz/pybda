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
from pyspark.mllib.linalg.distributed import RowMatrix

from koios.dimension_reduction import DimensionReduction
from koios.pca_fit import PCAFit
from koios.util.cast_as import as_rdd_of_array
from koios.util.features import feature_columns, to_double, fill_na, join
from koios.util.stats import scale

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PCA(DimensionReduction):
    def __init__(self, spark, n_components):
        super().__init__(spark, numpy.inf, numpy.inf)
        self.__n_components = n_components

    @property
    def n_components(self):
        return self.__n_components

    def _fit(self, data):
        X = as_rdd_of_array(data.select(feature_columns(data)))
        X = RowMatrix(scale(X))
        svd = X.computeSVD(self.__n_components)
        sds = numpy.sqrt(numpy.array(svd.s))
        loadings = numpy.array(svd.V)
        return X, loadings, sds

    def _transform(self, data, X, loadings):
        logger.info("Transforming data")

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
        return PCAFit(data, loadings, sds)


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
