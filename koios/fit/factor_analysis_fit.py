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

from pandas import DataFrame

from koios.fit.dimension_reduction_fit import DimensionReductionFit
from koios.globals import FEATURES__
from koios.io.io import write_parquet
from koios.plot.descriptive import scatter, histogram

from koios.plot.dimension_reduction_plot import biplot, \
    plot_cumulative_variance, plot_likelihood_path
from koios.sampler import sample
from koios.util.cast_as import as_pandas
from koios.spark.features import split_vector
from koios.stats.stats import cumulative_explained_variance


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FactorAnalysisFit(DimensionReductionFit):
    def __init__(self, data, n_factors, W, psi, ll, features):
        super().__init__(data, n_factors, features)
        self.__data = data
        self.__W = W
        self.__psi = psi
        self.__ll = ll

    @property
    def n_factors(self):
        return self.n_components

    @property
    def loadings(self):
        return self.__W

    @property
    def covariance(self):
        return self.__psi

    @property
    def loglikelihood(self):
        return self.__ll

    def write_files(self, outfolder):
        self.write_tsv(outfolder)
        self._write_loadings(outfolder + "-loadings.tsv")
        self._write_likelihood(outfolder + "-loglik.tsv")
        plot_fold = outfolder + "-plot"
        if not os.path.exists(plot_fold):
            os.mkdir(plot_fold)
        self._plot(os.path.join(plot_fold, "factor_analysis"))

    def _write_likelihood(self, outfile):
        logger.info("Writing likelihood profile")
        DataFrame(data=self.__ll).to_csv(outfile, sep="\t", index=False)

    def _plot(self, outfile):
        logger.info("Plotting")
        cev = cumulative_explained_variance(self.__W.transpose())
        subsamp = as_pandas(
          split_vector(sample(self.__data, 10000), FEATURES__))
        for suf in ["png", "pdf", "svg", "eps"]:
            plot_cumulative_variance(
              outfile + "-loadings-explained_variance." + suf,
              cev, "# factors")
            biplot(
              outfile + "-loadings-biplot." + suf,
              DataFrame(self.__W, columns=self.feature_names), "Factor 1", "Factor 2")
            plot_likelihood_path(
              outfile + "-likelihood_path." + suf,
              DataFrame({"L": self.__ll}))
            scatter(
              outfile + "-scatter_plot." + suf,
              subsamp["f_0"].values, subsamp["f_1"].values,
              "Factor 1", "Factor 2")
            for i in map(lambda x: "f_" + str(x),
                         range(min(10, self.n_factors))):
                histogram(
                  outfile + "-histogram_{}.".format(i) + suf,
                  subsamp[i].values, i)
