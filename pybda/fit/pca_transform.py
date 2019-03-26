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

from pybda.fit.dimension_reduction_transform import DimensionReductionTransform
from pybda.globals import FEATURES__
from pybda.io.io import mkdir
from pybda.plot.descriptive import scatter, histogram
from pybda.sampler import sample
from pybda.spark.features import split_vector
from pybda.util.cast_as import as_pandas

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PCATransform(DimensionReductionTransform):
    __KIND__ = "pca"

    def __init__(self, data, model):
        super().__init__(data, model)

    @property
    def kind(self):
        return PCATransform.__KIND__

    @property
    def sds(self):
        return self.model.sds

    def write(self, outfolder):
        logger.info("Writing transform")
        self.model.write(outfolder)
        self.write_tsv(outfolder)
        plot_fold = outfolder + "-plot"
        mkdir(plot_fold)
        self._plot(os.path.join(plot_fold, self.kind))

    def _plot(self, outfile):
        logger.info("Plotting")
        subsamp = as_pandas(split_vector(sample(self.data, 10000), FEATURES__))
        for suf in ["png", "pdf", "svg", "eps"]:
            scatter(outfile + "-scatter_plot." + suf, subsamp,
                    "f_0", "f_1", "PC 1", "PC 2")
            for i in map(lambda x: "f_" + str(x),
                         range(min(10, self.n_components))):
                histogram(outfile + "-histogram_{}.".format(i) + suf,
                          subsamp[i].values, i)
