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

from koios.fit.clustering_fit_profile import FitProfile
from koios.globals import WITHIN_VAR_, EXPL_VAR_, TOTAL_VAR_, K_
from koios.plot.cluster_plot import plot_cluster_sizes, plot_profile

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class KMeansFitProfile(FitProfile):
    def __init__(self, max, models=None):
        super().__init__(max, models)

    @staticmethod
    def _header():
        return "left_bound\t" \
               "k\t" \
               "right_bound\t" \
               "{}\t".format(WITHIN_VAR_) + \
               "{}\t".format(EXPL_VAR_) + \
               "{}\t".format(TOTAL_VAR_) + \
               "percent_loss\n"

    def _loss(self, model):
        if self.has_max_model():
            return 1 - model.explained_variance / \
                   self.max_model.explained_variance
        return 1

    def add(self, model, left, k, right):
        self.ks.append(k)
        self.models[k] = model
        self.loss = self._loss(model)
        self.path.append(self.KMeansElement(left, k, right, model, self.loss))
        logger.info("Loss for K={} to {}".format(k, self.loss))
        return self

    def _plot(self, outpath):
        data, labels = self._cluster_sizes(outpath)
        for suf in ["png", "pdf", "svg", "eps"]:
            plot_profile(outpath + "-profile." + suf, self.as_pandas(),
                         EXPL_VAR_, "Explained Variance")
            plot_cluster_sizes(
              outpath + "-cluster_sizes-histogram." + suf, data, labels)

    class KMeansElement:
        def __init__(self, left, k, right, model, loss):
            self.__left_boundary = left
            self.__current = k
            self.__right_boundary = right
            self.__K = k
            self.__model = model
            self.__loss = loss

        @property
        def model(self):
            return self.__model

        @property
        def values(self):
            return {
                'left_bound': self.__left_boundary,
                K_: self.__current,
                'right_bound': self.__right_boundary,
                WITHIN_VAR_: self.__model.within_cluster_variance,
                EXPL_VAR_: self.__model.explained_variance,
                TOTAL_VAR_: self.__model.total_variance,
                'percent_loss': self.__loss
            }

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return "{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
              self.__left_boundary,
              self.__current,
              self.__right_boundary,
              self.__model.within_cluster_variance,
              self.__model.explained_variance,
              self.__model.total_variance,
              self.__loss)
