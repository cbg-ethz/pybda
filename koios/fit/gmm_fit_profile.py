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

import scipy

from koios.fit.clustering_fit_profile import FitProfile
from koios.globals import K_, LOGLIK_, BIC_, NULL_LOGLIK_
from koios.plot.cluster_plot import plot_cluster_sizes, plot_profile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GMMFitProfile(FitProfile):
    def __init__(self):
        super().__init__()

    def add(self, model, left, k, right):
        self.ks.append(k)
        self.models[k] = model
        self.loss = self._loss(model)
        self.path.append(self.GMMElement(left, k, right, model, self.loss))
        logger.info("Loss for K={} to {}".format(k, self.loss))
        return self

    def _plot(self, outpath):
        data, labels = self._cluster_sizes(outpath)
        for suf in ["png", "pdf", "svg", "eps"]:
            plot_profile(outpath + "-profile." + suf,
                         self.as_pandas(), BIC_, BIC_)
            plot_cluster_sizes(
              outpath + "-cluster_sizes-histogram." + suf, data, labels)
