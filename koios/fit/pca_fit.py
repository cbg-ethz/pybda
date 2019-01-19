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

from koios.globals import FEATURES_
from koios.io.io import write_parquet
from koios.plot.descriptive import scatter, histogram

from koios.plot.dimension_reduction_plot import biplot, \
    plot_cumulative_variance
from koios.sampler import sample
from koios.util.cast_as import as_pandas
from koios.spark.features import feature_columns, split_vector
from koios.stats.stats import cumulative_explained_variance


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PCAFit:
    def __init__(self, data, n_components, loadings, sds):
        self.__data = data
        self.__n_components = n_components
        self.__loadings = loadings
        self.__sds = sds
        self.__kind = "pca"
        self.__features = feature_columns(self.__data)

    @property
    def kind(self):
        return self.__kind

    @property
    def data(self):
        return self.__data

    @property
    def loadings(self):
        return self.__loadings

    @property
    def sds(self):
        return self.__sds

    @property
    def n_components(self):
        return self.__n_components

    @property
    def feature_names(self):
        return self.__features

    def write_files(self, outfolder):
        write_parquet(self.__data, outfolder)
        self._write_loadings(outfolder + "-loadings.tsv")
        plot_fold = outfolder + "-plot"
        if not os.path.exists(plot_fold):
            os.mkdir(plot_fold)
        self._plot(os.path.join(plot_fold, self.kind))

    def _write_loadings(self, outfile):
        logger.info("Writing loadings to file")
        DataFrame(
          self.loadings[:self.n_components],
          columns=self.feature_names).to_csv(outfile, sep="\t", index=False)

    def _plot(self, outfile):
        logger.info("Plotting")
        cev = cumulative_explained_variance(self.sds)
        subsamp = as_pandas(split_vector(sample(self.data, 10000), FEATURES_))
        for suf in ["png", "pdf", "svg", "eps"]:
            plot_cumulative_variance(
              outfile + "-loadings-explained_variance." + suf,
              cev[:self.n_components], "# components")
            biplot(
              outfile + "-loadings-biplot." + suf,
              DataFrame(self.loadings[:self.n_components],
                        columns=self.feature_names), "PC 1", "PC 2")
            scatter(
              outfile + "-scatter_plot." + suf,
              subsamp["f_0"].values, subsamp["f_1"].values,
              "PC 1", "PC 2")
            for i in map(lambda x: "f_" + str(x),
                         range(min(10, self.n_components))):
                histogram(
                  outfile + "-histogram_{}.".format(i) + suf,
                  subsamp[i].values, i)
