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

from pyspark.ml.evaluation import RegressionEvaluator

from pybda.fit.regression_fit import RegressionFit
from pybda.globals import GAUSSIAN_, BINOMIAL_

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EnsembleFit(RegressionFit):
    def __init__(self, data, model, response, family, features):
        super().__init__(data, model, response, family, features)
        if family == GAUSSIAN_:
            evaluator = RegressionEvaluator(labelCol=self.response)
            self.__rmse = evaluator.evaluate(self.data,
                                             {evaluator.metricName: "rmse"})
            self.__mse = self.__rmse**2
            self.__r2 = evaluator.evaluate(self.data,
                                           {evaluator.metricName: "r2"})

    def write(self, outfolder):
        self._write_stats(outfolder)

    def _write_stats(self, outfolder):
        logger.info("Writing regression statistics")
        out_file = outfolder + "-statistics.tsv"
        with open(out_file, "w") as fh:
            if self.family == BINOMIAL_:
                fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                    "family", "response", "accuracy", "f1", "precision",
                    "recall"))
                fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                    self.family, self.response, self.accuracy, self.f1,
                    self.precision, self.recall))
            else:
                fh.write("{}\t{}\t{}\t{}\t{}\n".format("family", "response",
                                                       "mse", "r2", "rmse"))
                fh.write("{}\t{}\t{}\t{}\t{}\n".format(
                    self.family, self.response, self.mse, self.r2, self.rmse))

    @property
    def mse(self):
        return self.__mse

    @property
    def r2(self):
        return self.__r2

    @property
    def rmse(self):
        return self.__rmse
