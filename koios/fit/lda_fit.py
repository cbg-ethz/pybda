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
import numpy
import os

from pandas import DataFrame

from koios.fit.dimension_reduction_fit import DimensionReductionFit
from koios.globals import FEATURES__
from koios.plot.descriptive import scatter, histogram
from koios.plot.dimension_reduction_plot import biplot, \
    plot_cumulative_variance, plot_likelihood_path
from koios.sampler import sample
from koios.spark.features import split_vector
from koios.stats.stats import cumulative_explained_variance, normalized_cumsum
from koios.util.cast_as import as_pandas

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LDAFit(DimensionReductionFit):
    def __init__(self, data, n_components, W, vars, features, response):
        super().__init__(data, n_components, features)
        self.__data = data
        self.__W = W
        self.__vars = vars
        self.__response = response

    @property
    def response(self):
        return self.__response

    @property
    def n_discriminants(self):
        return self.n_components

    @property
    def projection(self):
        return self.__W

    @property
    def loglikelihood(self):
        return self.__ll

    @property
    def variances(self):
        return self.__vars

    def write_files(self, outfolder):
        self.write_tsv(outfolder)
        self._write_projection(outfolder + "-projection.tsv")
        plot_fold = outfolder + "-plot"
        if not os.path.exists(plot_fold):
            os.mkdir(plot_fold)
        self._plot(os.path.join(plot_fold, "linear_discriminant_analysis"))

    def _plot(self, outfile):
        logger.info("Plotting")
        cev = normalized_cumsum(self.sds)
        subsamp = as_pandas(
          split_vector(sample(self.__data, 10000), FEATURES__))
        for suf in ["png", "pdf", "svg", "eps"]:
            plot_cumulative_variance(
              outfile + "-discriminants-explained_variance." + suf,
              cev, "# discriminants")
            biplot(
              outfile + "-loadings-biplot." + suf,
              DataFrame(self.__W, columns=self.feature_names),
              "Discriminant 1", "Discriminant 2")
            scatter(
              outfile + "-scatter_plot." + suf,
              subsamp, "f_0", "f_1", "Discriminant 1", "Discriminant 2",
              color=self.response)
            for i in map(lambda x: "f_" + str(x),
                         range(min(10, self.n_discriminants))):
                histogram(outfile + "-histogram_{}.".format(i) + suf,
                          subsamp[i].values, i)
