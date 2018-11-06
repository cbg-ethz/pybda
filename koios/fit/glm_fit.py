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
import os
import pandas

import scipy as sp

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GLMFit:
    def __init__(self, data, model, response):
        self.__data = data
        self.__model = model
        self.__response = response
        self.__mse = model.summary.meanSquaredError
        self.__r2 = model.summary.r2
        self.__rmse = model.summary.rootMeanSquaredError
        self.__table = pandas.DataFrame(
          {"beta": sp.append(sp.array(model.intercept),
                             sp.array(model.coefficients)),
           "p_values": model.summary.pValues,
           "t_values": model.summary.tValues,
           "se": model.summary.coefficientStandardErrors
           }
        )

    def write_files(self, outfolder):
        self._write_stats(outfolder)
        self._write_table(outfolder)

    def _write_table(self, outfolder):
        self.__table.to_csv(outfolder + "-table.tsv",
                            sep="\t", index=False, header=True)

    def _write_stats(self, outfolder):
        out_file = outfolder + "-statistics.tsv"
        with open(out_file, "w") as fh:
            fh.write("{}\t{}\t{}\t{}\t{}\n".format(
              "response", "df", "mse", "r2", "rmse"))
            fh.write("{}\t{}\t{}\t{}\t{}\n".format(
              self.__response, self.__df, self.__mse, self.__r2, self.__rmse))

    @property
    def response(self):
        return self.__response

    def transform(self, data):
        return self.__model.transform(data)

    @property
    def data(self):
        return self.__data

    @property
    def coefficients(self):
        return self.__coefficients

    @property
    def standard_errors(self):
        return self.__se

    @property
    def df(self):
        return self.__df

    @property
    def mse(self):
        return self.__mse

    @property
    def p_values(self):
        return self.__pvalues

    @property
    def t_values(self):
        return self.__tvalues

    @property
    def residuals(self):
        return self.__residuals

    @property
    def r2(self):
        return self.__r2

    @property
    def rmse(self):
        return self.__rmse
