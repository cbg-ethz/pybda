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
from pyspark import StorageLevel
from pyspark.ml.regression import LinearRegression
from pyspark.ml.classification import LogisticRegression

from koios.fit.glm_fit import GLMFit
from koios.globals import GAUSSIAN_, BINOMIAL_
from koios.regression import Regression

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GLM(Regression):
    def __init__(self, spark, response,
                 family=GAUSSIAN_, max_iter=100):
        super().__init__(spark, family)
        self.__max_iter = max_iter
        self.__response = response

    def fit(self, data):
        logger.info("Fitting GLM with family='{}'".format(self.family))
        model = self._fit(data)
        return GLMFit(data, model, self.__response, self.family)

    def _fit(self, data):
        data.persist(StorageLevel.DISK_ONLY)
        logger.info(data.storageLevel)
        return self._model().fit(data)

    def _model(self):
        if self.family == GAUSSIAN_:
            reg = LinearRegression()
        elif self.family == BINOMIAL_:
            reg = LogisticRegression()
        else:
            raise NotImplementedError(
              "Family '{}' not implemented".format(self.family))
        reg.setLabelCol(self.__response)
        reg.setMaxIter(self.__max_iter)
        return reg

    def fit_transform(self):
        raise NotImplementedError()

    def transform(self):
        raise NotImplementedError()


@click.command()
@click.argument("file", type=str)
@click.argument("meta", type=str)
@click.argument("features", type=str)
@click.argument("response", type=str)
@click.argument("family", type=str)
@click.argument("outpath", type=str)
def run(file, meta, features, response, family, outpath):
    from koios.util.string import drop_suffix
    from koios.logger import set_logger
    from koios.spark_session import SparkSession
    from koios.io.as_filename import as_logfile
    from koios.io.io import read_and_transmute, read_column_info

    outpath = drop_suffix(outpath, "/")
    set_logger(as_logfile(outpath))

    with SparkSession() as spark:
        try:
            meta, features = read_column_info(meta, features)
            data = read_and_transmute(spark, file, features, response)
            fl = GLM(spark, response, family)
            fit = fl.fit(data)
            fit.write_files(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
