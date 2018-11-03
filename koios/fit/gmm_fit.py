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

from koios.fit.clustering_fit import ClusteringFit

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GMMFit(ClusteringFit):
    def __init__(self, data, fit, k, mixing_weights,
                 estimates, loglik, null_loglik,
                 n, p, path=None):
        self.__data = data
        self.__fit = fit
        self.__n = n
        self.__p = p
        self.__k = k
        self.__mixing_weights = mixing_weights
        self.__estimates = estimates
        self.__loglik = loglik
        self.__null_loglik = null_loglik
        self.__n_params = k * p + k * p * (p + 1) / 2 + k - 1
        self.__null_n_params = p + p * (p + 1) / 2
        self.__bic = scipy.log(n) * self.__n_params \
                     - 2 * scipy.log(self.__loglik)
        self.__null_bic = scipy.log(n) * self.__null_n_params \
                          - 2 * scipy.log(self.null_loglik)
        self.__path = path

    def _k_fit_path(self, k):
        pass

    @classmethod
    def load_model(cls, statistics_file, load_fit=False):
        pass
