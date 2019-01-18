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
from pyspark.ml.regression import LinearRegression
from pyspark.ml.classification import LogisticRegression

from koios.fit.glm_fit import GLMFit
from koios.globals import GAUSSIAN_, BINOMIAL_
from koios.regression import Regression

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GLM(Regression):
    def __init__(self, spark, response, meta, features,
                 family=GAUSSIAN_, max_iter=20):
        super().__init__(spark, family)
        self.__max_iter = max_iter
        self.__response = response
        self.__meta = meta
        self.__features = features

    def fit(self, data):
        logger.info("Fitting GLM with family='{}'".format(self.family))
        model = self._fit(data)
        return GLMFit(data, model, self.__response,
                      self.family, self.__features)

    def _fit(self, data):
        data = data.coalesce(300)
        if self.family == BINOMIAL_:
            mcnt = data.groupby(self.__response).count().toPandas()
            cnts = mcnt["count"].values
            cnt_0, cnt_1 = int(cnts[0]), int(cnts[1])
            if cnt_0 != cnt_1:
                logger.info("Found inbalanced data-set...going to balance.")
                mcnt = int(cnts.min())
                logger.info("Minimum count of one label: {}".format(mcnt))
                df_0 = data.filter("{} == 0".format(self.__response)).limit(mcnt)
                logger.info("#group 0: {}".format(df_0.count()))
                df_1 = data.filter("{} == 1".format(self.__response)).limit(mcnt)
                logger.info("#group 1: {}".format(df_1.count()))
                data = df_0.union(df_1)
                logger.info("Size of data set after subsampling: {}".format(data.count()))
        data = data.coalesce(300)
        logger.info(data.storageLevel)
        return self._model().fit(data)

    def _model(self):
        if self.family == GAUSSIAN_:
            reg = LinearRegression()
        elif self.family == BINOMIAL_:
            reg = LogisticRegression(family="binomial")
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
    """
    Fit a generalized linear regression model.
    """

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
            fl = GLM(spark, response, meta, features, family)
            fit = fl.fit(data)
            fit.write_files(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
