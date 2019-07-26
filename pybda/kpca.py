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
from pyspark.sql import DataFrame

from pybda.decorators import timing
from pybda.fit.kpca_fit import KPCAFit
from pybda.fit.kpca_transform import KPCATransform
from pybda.pca import PCA
from pybda.stats.stats import fourier, fourier_transform

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class KPCA(PCA):
    def __init__(self, spark, n_components, features, n_fourier_features=200,
                 gamma=1.):
        super().__init__(spark, n_components, features)
        self.__n_fourier_features = n_fourier_features
        self.__gamma = gamma
        self.__seed = 23

    @property
    def gamma(self):
        return self.__gamma

    @property
    def n_fourier_features(self):
        return self.__n_fourier_features

    @timing
    def _fit(self, data):
        logger.info("Fitting KPCA")
        X = self._preprocess_data(data)
        X, w, b = fourier(X, self.n_fourier_features, self.__seed, self.gamma)
        loadings, sds = PCA._compute_pcs(X)
        self.model = KPCAFit(self.n_components, loadings, sds, self.features,
                             self.n_fourier_features, w, b, self.gamma)
        return X, self.model

    def transform(self, data):
        X = self._setup_matrix_for_transform(data)
        X = fourier_transform(X,
                              self.model.fourier_coefficients,
                              self.model.fourier_offset)
        return KPCATransform(self._transform(data, X), self.model)

    def _transform(self, data, X):
        return super()._transform(data, X)

    def fit_transform(self, data: DataFrame):
        X, _ = self._fit(data)
        return KPCATransform(self._transform(data, X), self.model)


@click.command()
@click.argument("components", type=int)
@click.argument("file", type=str)
@click.argument("features", type=str)
@click.argument("outpath", type=str)
def run(components, file, features, outpath):
    """
    Fit a kernel PCA to a data set.
    """

    from pybda.util.string import drop_suffix
    from pybda.logger import set_logger
    from pybda.spark_session import SparkSession
    from pybda.io.io import read_info, read_and_transmute
    from pybda.io.as_filename import as_logfile

    outpath = drop_suffix(outpath, "/")
    set_logger(as_logfile(outpath))

    with SparkSession() as spark:
        try:
            features = read_info(features)
            data = read_and_transmute(spark, file, features,
                                      assemble_features=False)
            fl = KPCA(spark, components, features)
            tran = fl.fit_transform(data)
            tran.write(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
