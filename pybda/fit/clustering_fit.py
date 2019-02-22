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
from abc import abstractmethod, ABC

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ClusteringFit(ABC):
    def __init__(self, data, fit, n, p, k):
        self.__data = data
        self.__fit = fit
        self.__n = n
        self.__p = p
        self.__k = k

    @abstractmethod
    def __str__(self):
        pass

    def transform(self, data):
        return self.__fit.transform(data)

    @property
    def fit(self):
        return self.__fit

    @property
    def data(self):
        return self.__data

    @property
    def k(self):
        return self.__k

    @property
    def n(self):
        return self.__n

    @property
    def p(self):
        return self.__p

    @abstractmethod
    def write(self, outfolder):
        pass

    @abstractmethod
    def _k_fit_path(self, k):
        pass

    @abstractmethod
    def _write_statistics(self, outfile):
        pass

    @abstractmethod
    def header(self):
        pass

    @abstractmethod
    def values(self):
        pass

    def as_statfile(self, fit_folder, k):
        return os.path.join(fit_folder, self._k_fit_path(k) + "_statistics.tsv")

    def _write_fit(self, outfolder):
        logger.info("Writing cluster fit to: {}".format(outfolder))
        self.__fit.write().overwrite().save(outfolder)

    def _write_cluster_sizes(self, outfile):
        comp_files = outfile + "_cluster_sizes.tsv"
        logger.info("Writing cluster size file to: {}".format(comp_files))
        with open(comp_files, 'w') as fh:
            for c in self.__fit.summary.clusterSizes:
                fh.write("{}\n".format(c))
