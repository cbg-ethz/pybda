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
import os

from pandas import DataFrame

from pybda.fit.dimension_reduction_fit import DimensionReductionFit
from pybda.io.io import mkdir
from pybda.plot.dimension_reduction_plot import biplot, \
    plot_cumulative_variance
from pybda.stats.stats import normalized_cumsum

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LDAFit(DimensionReductionFit):
    def __init__(self,  n_components, loadings, var, features, response):
        super().__init__(n_components, features, loadings)
        self.__vars = var
        self.__response = response

    @property
    def response(self):
        return self.__response

    @property
    def n_discriminants(self):
        return self.n_components

    @property
    def projection(self):
        return self.loadings

    @property
    def loglikelihood(self):
        return self.__ll

    @property
    def variances(self):
        return self.__vars

    def write(self, outfolder):
        self._write_loadings(outfolder + "-projection.tsv")
        plot_fold = outfolder + "-plot"
        mkdir(plot_fold)
        self._plot(os.path.join(plot_fold, "linear_discriminant_analysis"))

    def _plot(self, outfile):
        logger.info("Plotting")
        cev = normalized_cumsum(self.variances)
        for suf in ["png", "pdf", "svg", "eps"]:
            plot_cumulative_variance(
                outfile + "-discriminants-explained_variance." + suf, cev,
                "# discriminants")
            biplot(outfile + "-loadings-biplot." + suf,
                   DataFrame(self.loadings, columns=self.feature_names),
                   "Discriminant 1", "Discriminant 2")
