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

from pybda.fit.pca_transform import PCATransform

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class KPCATransform(PCATransform):
    __KIND__ = "kpca"

    def __init__(self, data, model):
        super().__init__(data, model)

    @property
    def kind(self):
        return KPCATransform.__KIND__

    @property
    def gamma(self):
        return self.model.gamma

    @property
    def n_fourier_features(self):
        return self.model.n_fourier_features

    @property
    def feature_names(self):
        return self.model.feature_names
