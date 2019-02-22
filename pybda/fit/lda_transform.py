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

from pybda.fit.dimension_reduction_transform import DimensionReductionTransform
from pybda.globals import FEATURES__
from pybda.io.io import mkdir
from pybda.plot.descriptive import scatter, histogram
from pybda.plot.dimension_reduction_plot import biplot, \
    plot_cumulative_variance
from pybda.sampler import sample
from pybda.spark.features import split_vector
from pybda.stats.stats import normalized_cumsum
from pybda.util.cast_as import as_pandas

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LDATransform(DimensionReductionTransform):
    def __init__(self, data, model):
        super().__init__(data, model)

    @property
    def response(self):
        return self.model.response

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
        logger.info("Writing transform")
        self.model.write(outfolder)
        self.write_tsv(outfolder)
        plot_fold = outfolder + "-plot"
        mkdir(plot_fold)
        self._plot(os.path.join(plot_fold, "linear_discriminant_analysis"))

    def _plot(self, outfile):
        logger.info("Plotting")
        subsamp = as_pandas(
            split_vector(sample(self.data, 10000), FEATURES__))
        for suf in ["png", "pdf", "svg", "eps"]:
            scatter(outfile + "-scatter_plot." + suf, subsamp, "f_0", "f_1",
                    "Discriminant 1", "Discriminant 2", color=self.response)
            for i in map(lambda x: "f_" + str(x),
                         range(min(10, self.n_discriminants))):
                histogram(outfile + "-histogram_{}.".format(i) + suf,
                          subsamp[i].values, i)
