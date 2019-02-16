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

import numpy
import pandas
import scipy as sp
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

from pybda.fit.transformed_data import TransformedData
from pybda.globals import GAUSSIAN_, BINOMIAL_, INTERCEPT__
from pybda.plot.regression_plot import plot_curves

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GLMFit:
    def __init__(self, data, model, response, family, features):
        self.__data = data
        self.__model = model
        self.__response = response
        self.__family = family
        self.__features = features

        if family == GAUSSIAN_:
            self.__df = model.summary.degreesOfFreedom
            self.__mse = model.summary.meanSquaredError
            self.__r2 = model.summary.r2
            self.__rmse = model.summary.rootMeanSquaredError
        else:
            evaluator = MulticlassClassificationEvaluator(labelCol=response)
            self.__data = self.__model.transform(self.__data)

            self.__f1 = evaluator.evaluate(self.data,
                                           {evaluator.metricName: "f1"})
            self.__accuracy = evaluator.evaluate(
              self.data, {evaluator.metricName: "accuracy"})
            self.__precision = evaluator.evaluate(
              self.data, {evaluator.metricName: "weightedPrecision"})
            self.__recall = evaluator.evaluate(
              self.data, {evaluator.metricName: "weightedRecall"})
        self.__table = self._compute_table_stats(model)

    def _compute_table_stats(self, model):
        beta = sp.append(
          sp.array(model.intercept), sp.array(model.coefficients))
        ps = sp.ones_like(beta) * sp.nan
        ts = sp.ones_like(beta) * sp.nan
        se = sp.ones_like(beta) * sp.nan
        try:
            ps = model.summary.pValues
            ts = model.summary.tValues
            se = model.summary.coefficientStandardErrors
        except Exception as _:
            logger.warning("Could not compute p-values, t-values and SEs. "
                           "Possibly due to singular vcov.")

        return pandas.DataFrame({
            "features": [INTERCEPT__] + self.__features,
            "beta": beta,
            "p_values": ps,
            "t_values": ts,
            "se": se
        })

    def write_files(self, outfolder):
        self._write_stats(outfolder)
        self._write_table(outfolder)
        if self.family == BINOMIAL_:
            self._write_binomial_measures(outfolder)
            self._plot(outfolder)

    def _write_table(self, outfolder):
        logger.info("Writing regression table")
        self.__table.to_csv(outfolder + "-table.tsv", na_rep="NaN", sep="\t",
                            index=False, header=True)

    def _write_stats(self, outfolder):
        logger.info("Writing regression statistics")
        out_file = outfolder + "-statistics.tsv"
        with open(out_file, "w") as fh:
            if self.family == BINOMIAL_:
                fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                  "family", "response", "accuracy", "f1", "precision",
                  "recall"))
                fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                  self.family, self.response, self.__accuracy, self.__f1,
                  self.__precision, self.__recall))
            else:
                fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                  "family", "response", "df", "mse", "r2", "rmse"))
                fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                  self.family, self.__response, self.__df, self.__mse,
                  self.__r2, self.__rmse))

    def _write_binomial_measures(self, outfolder):
        logger.info("Writing regression measures")
        self.__pr.to_csv(outfolder + "-precision_recall.tsv", sep="\t",
                         index=False, header=True)
        self.__roc.to_csv(outfolder + "-roc_curve.tsv", sep="\t", index=False,
                          header=True)
        self.__measures.to_csv(outfolder + "-measures.tsv", sep="\t",
                               index=False, header=True)

    def _plot(self, outfolder):
        for suf in ["png", "pdf", "svg", "eps"]:
            plot_curves(outfolder + "-plot." + suf, self.__pr, self.__roc)

    @property
    def family(self):
        return self.__family

    @property
    def response(self):
        return self.__response

    @property
    def features(self):
        return numpy.squeeze(self.__table[["features"]].values)

    def transform(self, data):
        return TransformedData(self.__model.transform(data))

    @property
    def data(self):
        return self.__data

    @property
    def coefficients(self):
        return numpy.squeeze(self.__table[["beta"]].values)

    @property
    def standard_errors(self):
        return numpy.squeeze(self.__table[["se"]].values)

    @property
    def df(self):
        return self.__df

    @property
    def mse(self):
        return self.__mse

    @property
    def p_values(self):
        return numpy.squeeze(self.__table[["p_values"]].values)

    @property
    def t_values(self):
        return numpy.squeeze(self.__table[["t_values"]].values)

    @property
    def r2(self):
        return self.__r2

    @property
    def rmse(self):
        return self.__rmse

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

