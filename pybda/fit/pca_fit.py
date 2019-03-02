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
from pybda.plot.dimension_reduction_plot import (biplot,
                                                 plot_cumulative_variance)
from pybda.stats.stats import cumulative_explained_variance

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PCAFit(DimensionReductionFit):
    __KIND__ = "pca"

    def __init__(self, n_components, loadings, sds, features):
        super().__init__(n_components, features, loadings)
        self.__sds = sds

    @property
    def kind(self):
        return PCAFit.__KIND__

    @property
    def sds(self):
        return self.__sds

    def write(self, outfolder):
        self._write_loadings(outfolder + "-loadings.tsv")
        plot_fold = outfolder + "-plot"
        mkdir(plot_fold)
        self._plot(os.path.join(plot_fold, self.kind))

    def _plot(self, outfile):
        logger.info("Plotting")
        cev = cumulative_explained_variance(self.sds)
        for suf in ["png", "pdf", "svg", "eps"]:
            plot_cumulative_variance(
                outfile + "-loadings-explained_variance." + suf,
                cev[:self.n_components], "# components")
            biplot(
                outfile + "-loadings-biplot." + suf,
                DataFrame(self.loadings[:self.n_components],
                          columns=self.feature_names), "PC 1", "PC 2")
