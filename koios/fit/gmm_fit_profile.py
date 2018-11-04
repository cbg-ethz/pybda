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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GMMFitProfile(FitProfile):
    def __init__(self, max, models=None):
        super().__init__(max, models)

    def write_files(self, outpath):
        self._write(outpath)
        self._write_cluster_quantiles(outpath)
        self._plot(outpath)

    @staticmethod
    def _header():
        return "left_bound\t" \
               "k\t" \
               "right_bound\t" \
               "{}\t".format(LOGLIK_) + \
               "{}\t".format(BIC_) + \
               "{}\t".format(NULL_LOGLIK_) + \
               "\n"

    def _loss(self, model):
        if self.has_max_model():
            return model.bic
        return scipy.inf

    def add(self, model, left, k, right):
        self.ks.append(k)
        self.models[k] = model
        self.loss = self._loss(model)
        self.path.append(self.GMMElement(left, k, right, model, self.loss))
        logger.info("Loss for K={} to {}".format(k, self.loss))
        return self

    class GMMElement:
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
                LOGLIK_: self.__model.loglik,
                BIC_: self.__model.bic,
                NULL_LOGLIK_: self.__model.null_loglik
            }

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return "{}\t{}\t{}\t{}\t{}\t{}\n".format(
              self.__left_boundary,
              self.__current,
              self.__right_boundary,
              self.__model.loglik,
              self.__model.bic,
              self.__model.null_loglik)
