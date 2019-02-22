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


class KPCATransform(PCAFit):
    __KIND__ = "kpca"

    def __init__(self, data, n_components, loadings,
                 sds, features, n_fourier_features, gamma):
        super().__init__(data, n_components, loadings, sds, features)
        self.__n_ff = n_fourier_features
        self.__gamma = gamma,
        self.__suffix = "kpca"
        self.__ff_features = list(
            map('fourier_feature_{}'.format, range(1, n_fourier_features + 1)))

    @property
    def kind(self):
        return KPCAFit.__KIND__

    @property
    def gamma(self):
        return self.__gamma

    @property
    def n_fourier_features(self):
        return self.__n_ff

    @property
    def feature_names(self):
        return self.__ff_features
