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
from pandas import DataFrame
from koios.io.io import write_parquet_data

from koios.plot.dimension_reduction_plot import biplot, plot_cumulative_variance
from koios.util.features import feature_columns
from koios.util.stats import cumulative_explained_variance, explained_variance

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FactorAnalysisFit:
    def __init__(self, data, W, psi, ll):
        self.__data = data
        self.__W = W
        self.__psi = psi
        self.__ll = ll

    @property
    def data(self):
        return self.__data

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
        write_parquet_data(self.__data, outfolder)
        self._write_loadings(outfolder + "-loadings.tsv")
        self._write_likelihood(outfolder + "-loglik.tsv")
        self._plot(outfolder)

    def _write_loadings(self, outfile):
        logger.info("Writing loadings to data")
        features = feature_columns(self.__data)
        DataFrame(self.__W, columns=features).to_csv(
          outfile, sep="\t", index=False)

    def _write_likelihood(self, outfile):
        logger.info("Writing likelihood profile")
        DataFrame(data=self.__ll).to_csv(outfile, sep="\t", index=False)

    def _plot(self, outfile):
        logger.info("Plotting")
        ev = explained_variance(self.__W.transpose())
        cev = cumulative_explained_variance(self.__W.transpose())
        features = feature_columns(self.__data)
        for suf in ["png", "pdf", "svg", "eps"]:
            plot_cumulative_variance(
              outfile + "-loadings-explained_variance." + suf,
              cev, "# factors")
            biplot(outfile + "-loadings-biplot." + suf,
                   DataFrame(self.__W, columns=features),
                   "Factor 1",
                   "Factor 2")
