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

import numpy

from koios.globals import WITHIN_VAR_, EXPL_VAR_, TOTAL_VAR_

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class KMeansFitProfile:
    def __init__(self, max, models=None):
        self.__maximum = max
        self.__ks = []
        self.__variance_path = []
        self.__models = {} if models is None else models
        self.__loss = numpy.inf

    def __getitem__(self, key):
        return self.__models[key]

    @classmethod
    def as_profilefile(cls, fl):
        if fl.endswith(".tsv"):
            profilefile = fl.replace(".tsv", "-profile.tsv")
        else:
            profilefile = fl + "-profile.tsv"
        return profilefile

    def write_variance_path(self, outpath):
        lrt_file = KMeansFitProfile.as_profilefile(outpath)
        logger.info("Writing kmeans fit profile to {}".format(lrt_file))
        with open(lrt_file, "w") as fh:
            fh.write(self._header())
            for el in self.__variance_path:
                fh.write(str(el))

    @staticmethod
    def _header():
        return "left_bound\t" \
               "k\t" \
               "right_bound\t" \
               "{}\t".format(WITHIN_VAR_) + \
               "{}\t".format(EXPL_VAR_) + \
               "{}\t".format(TOTAL_VAR_) + \
               "percent_loss\n"

    @property
    def loss(self):
        return self.__loss

    @property
    def current_model(self):
        return self.__models[self.__ks[-1]]

    @property
    def max_model(self):
        if not self.has_max_model():
            return None
        return self.__models[self.__maximum]

    def has_max_model(self):
        return self.__maximum in self.__models.keys()

    def keys(self):
        return self.__models.keys()

    def _loss(self, model):
        if self.has_max_model():
            return 1 - model.explained_variance / self.max_model.explained_variance
        return 1

    def add(self, model, left, k, right):
        self.__ks.append(k)
        self.__models[k] = model
        self.__loss = self._loss(model)
        self.__variance_path.append(self.Element(left, k, right, model, self.loss))
        logger.info("Loss for K={} to {}".format(k, self.loss))
        return self

    class Element:
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



