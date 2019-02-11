# Copyright (C) 2018 Simon Dirmeier
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

from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.evaluation import RegressionEvaluator

from pybda.fit.transformed_data import TransformedData
from pybda.globals import GAUSSIAN_, BINOMIAL_

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EnsembleFit:
    def __init__(self, data, model, response, family, features):
        self.__data = data
        self.__model = model
        self.__response = response
        self.__family = family
        self.__features = features

        if family == GAUSSIAN_:
            evaluator = RegressionEvaluator(labelCol=self.response)
            self.__rmse = evaluator.evaluate(
              self.data, {evaluator.metricName: "rmse"})
            self.__mse = self.__rmse ** 2
            self.__r2 = evaluator.evaluate(
              self.data, {evaluator.metricName: "r2"})
        else:
            evaluator = MulticlassClassificationEvaluator(
              labelCol=self.response)
            self.__f1 = evaluator.evaluate(
              self.data, {evaluator.metricName: "f1"})
            self.__accuracy = evaluator.evaluate(
              self.data, {evaluator.metricName: "accuracy"})
            self.__precision = evaluator.evaluate(
              self.data, {evaluator.metricName: "weightedPrecision"})
            self.__recall = evaluator.evaluate(
              self.data, {evaluator.metricName: "weightedRecall"})

    def write_files(self, outfolder):
        logger.info("Writing regression statistics")
        out_file = outfolder + "-statistics.tsv"
        with open(out_file, "w") as fh:
            if self.family == BINOMIAL_:
                fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                  "family", "response", "accuracy", "f1", "precision", "recall"))
                fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                  self.family, self.response, self.__accuracy,
                  self.__f1, self.__precision, self.__recall))
            else:
                fh.write("{}\t{}\t{}\t{}\t{}\n".format(
                  "family", "response", "mse", "r2", "rmse"))
                fh.write("{}\t{}\t{}\t{}\t{}\n".format(
                  self.family, self.response, self.__mse,
                  self.__r2, self.__rmse))

    @property
    def family(self):
        return self.__family

    @property
    def response(self):
        return self.__response

    def transform(self, data):
        return TransformedData(self.__model.transform(data))

    @property
    def data(self):
        return self.__data

    @property
    def mse(self):
        return self.__mse

    @property
    def r2(self):
        return self.__r2

    @property
    def rmse(self):
        return self.__rmse
