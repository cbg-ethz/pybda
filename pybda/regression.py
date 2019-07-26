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
from abc import abstractmethod

from pybda.decorators import timing
from pybda.globals import BINOMIAL_
from pybda.spark_model import SparkModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Regression(SparkModel):
    def __init__(self, spark, family, response, features):
        super().__init__(spark)
        self.__family = family
        self.__response = response
        self.__features = features
        self.__model = None

    @property
    def model(self):
        return self.__model

    @model.setter
    def model(self, model):
        self.__model = model

    def write(self, outfolder):
        self.model.write(outfolder)

    @property
    def features(self):
        return self.__features

    @property
    def response(self):
        return self.__response

    @property
    def family(self):
        return self.__family

    @abstractmethod
    def fit(self, data):
        pass

    @timing
    def predict(self, data):
        return self.model.predict(data)

    @timing
    def _balance(self, data):
        data = data.coalesce(300)
        if self.family == BINOMIAL_:
            mcnt = data.groupby(self.response).count().toPandas()
            cnts = mcnt["count"].values
            cnt_0, cnt_1 = int(cnts[0]), int(cnts[1])
            if cnt_0 != cnt_1:
                logger.info("Found inbalanced data-set...going to balance.")
                mcnt = int(cnts.min())
                logger.info("Minimum count of one label: {}".format(mcnt))
                df_0 = data.filter("{} == 0".format(self.response)).limit(mcnt)
                logger.info("#group 0: {}".format(df_0.count()))
                df_1 = data.filter("{} == 1".format(self.response)).limit(mcnt)
                logger.info("#group 1: {}".format(df_1.count()))
                data = df_0.union(df_1)
                logger.info("Size of data set after subsampling: {}".format(
                  data.count()))
        data = data.coalesce(300)
        return data

    @timing
    def _fit(self, data):
        data = self._balance(data)
        return self._model().fit(data)
