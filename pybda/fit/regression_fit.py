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
from abc import ABC, abstractmethod

from pyspark.ml.evaluation import MulticlassClassificationEvaluator

from pybda.fit.predicted_data import PredictedData
from pybda.globals import BINOMIAL_

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RegressionFit(ABC):
    def __init__(self, data, model, response, family, features):
        self.__data = model.transform(data)
        self.__model = model
        self.__response = response
        self.__family = family
        self.__features = features

        if family == BINOMIAL_:
            evaluator = MulticlassClassificationEvaluator(labelCol=response)
            self.__f1 = evaluator.evaluate(self.data,
                                           {evaluator.metricName: "f1"})
            self.__accuracy = evaluator.evaluate(
                self.data, {evaluator.metricName: "accuracy"})
            self.__precision = evaluator.evaluate(
                self.data, {evaluator.metricName: "weightedPrecision"})
            self.__recall = evaluator.evaluate(
                self.data, {evaluator.metricName: "weightedRecall"})

    @abstractmethod
    def write(self, outfolder):
        pass

    @property
    def family(self):
        return self.__family

    @property
    def response(self):
        return self.__response

    @property
    def features(self):
        return self.__features

    def predict(self, data=None):
        if data is None:
            return PredictedData(self.data)
        return PredictedData(self.__model.transform(data))

    @property
    def data(self):
        return self.__data

    @property
    def f1(self):
        return self.__f1

    @property
    def accuracy(self):
        return self.__accuracy

    @property
    def precision(self):
        return self.__precision

    @property
    def recall(self):
        return self.__recall
