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
from pybda.plot.dimension_reduction_plot import biplot

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ICAFit(DimensionReductionFit):
    def __init__(self, n_components, loadings, features, unmixing, whitening):
        super().__init__(n_components, features, loadings.T)
        self.__unmixing = unmixing
        self.__whitening = whitening

    @property
    def unmixing(self):
        return self.__unmixing

    @property
    def whitening(self):
        return self.__whitening

    def write(self, outfolder):
        self._write_loadings(outfolder + "-loadings.tsv")
        plot_fold = outfolder + "-plot"
        mkdir(plot_fold)
        self._plot(os.path.join(plot_fold, "ica"))

    def _plot(self, outfile):
        logger.info("Plotting")
        for suf in ["png", "pdf", "svg", "eps"]:
            biplot(outfile + "-loadings-biplot." + suf,
                   DataFrame(self.loadings, columns=self.feature_names),
                   "Component 1", "Component 2")
