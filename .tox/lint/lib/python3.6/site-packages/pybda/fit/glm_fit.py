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

from pybda.fit.regression_fit import RegressionFit
from pybda.globals import GAUSSIAN_, BINOMIAL_, INTERCEPT__

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GLMFit(RegressionFit):
    def __init__(self, data, model, response, family, features):
        super().__init__(data, model, response, family, features)

        if family == GAUSSIAN_:
            self.__df = model.summary.degreesOfFreedom
            self.__mse = model.summary.meanSquaredError
            self.__r2 = model.summary.r2
            self.__rmse = model.summary.rootMeanSquaredError

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
        except Exception:
            logger.warning("Could not compute p-values, t-values and SEs. "
                           "Possibly due to singular vcov.")

        return pandas.DataFrame({
            "features": self.features,
            "beta": beta,
            "p_values": ps,
            "t_values": ts,
            "se": se
        })

    def write(self, outfolder):
        self._write_stats(outfolder)
        self._write_table(outfolder)

    def _write_table(self, outfolder):
        logger.info("Writing regression table")
        self.table.to_csv(outfolder + "-table.tsv", na_rep="NaN", sep="\t",
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
                  self.family, self.response, self.accuracy, self.f1,
                  self.precision, self.recall))
            else:
                fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                  "family", "response", "df", "mse", "r2", "rmse"))
                fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                  self.family, self.response, self.df, self.mse,
                  self.r2, self.rmse))

    @property
    def table(self):
        return self.__table

    @property
    def features(self):
        return [INTERCEPT__] + super().features

    @property
    def df(self):
        return self.__df

    @property
    def coefficients(self):
        return numpy.squeeze(self.table[["beta"]].values)

    @property
    def standard_errors(self):
        return numpy.squeeze(self.table[["se"]].values)

    @property
    def p_values(self):
        return numpy.squeeze(self.table[["p_values"]].values)

    @property
    def t_values(self):
        return numpy.squeeze(self.table[["t_values"]].values)

    @property
    def mse(self):
        return self.__mse

    @property
    def r2(self):
        return self.__r2

    @property
    def rmse(self):
        return self.__rmse
