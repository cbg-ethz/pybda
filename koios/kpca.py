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

from koios.pca import PCA
from koios.pca_fit import PCAFit
from koios.util.cast_as import as_rdd_of_array
from koios.util.features import feature_columns, to_double, fill_na
from koios.math.stats import scale, svd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class KPCA(PCA):
    def __init__(self, spark, n_components, n_fourier_features, gamma=1):
        super().__init__(spark, n_components)
        self.__n_fourier_features = n_fourier_features
        self.__gamma = gamma
        self.__seed = 23

    @property
    def n_fourier_features(self):
        return self.__n_fourier_features

    def _fourier(self, X):
        p = X.numCols()

        random_state = numpy.random.RandomState(self.__seed)
        w = numpy.sqrt(2 * gamma) * \
            random_state.normal(size=(p, n_features))
        b = random_state.uniform(0, 2 * numpy.pi, size=n_features)
        w = DenseMatrix(p, n_features, w.flatten())
        Y = X.multiply(w)
        Y = Y.rows.map(
            lambda x: numpy.sqrt(2.0 / n_features) * numpy.cos(x + b))
        return RowMatrix(Y)

    def _fit(self, data):
        X = as_rdd_of_array(data.select(feature_columns(data)))
        X = RowMatrix(scale(X))
        sds, loadings, _ = svd(X, X.numCols())
        sds = sds / numpy.sqrt(max(1, data.count() - 1))
        return X, loadings, sds

    def fit(self):
        raise NotImplementedError()

    def transform(self):
        raise NotImplementedError()

    def fit_transform(self, data):
        logger.info("Running kernel principal component analysis ...")
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

            fl = KPCA(spark, components)
            fit = fl.fit_transform(data)
            fit.write_files(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
