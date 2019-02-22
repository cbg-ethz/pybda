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

from pybda.fit.pca_fit import PCAFit

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class KPCAFit(PCAFit):
    __KIND__ = "kpca"

    def __init__(self, n_components, loadings, sds, features,
                 n_fourier_features, fourier_coefficients, fourier_offset,
                 gamma):
        super().__init__(n_components, loadings, sds, features)
        self.__n_fourier_features = n_fourier_features
        self.__fourier_coefficients = fourier_coefficients
        self.__fourier_offset = fourier_offset
        self.__gamma = gamma
        self.__ff_features = list(
          map('fourier_feature_{}'.format, range(1, n_fourier_features + 1)))

    @property
    def fourier_coefficients(self):
        return self.__fourier_coefficients

    @property
    def fourier_offset(self):
        return self.__fourier_offset

    @property
    def gamma(self):
        return self.__gamma

    @property
    def n_fourier_features(self):
        return self.__n_fourier_features

    @property
    def feature_names(self):
        return self.__ff_features
