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

from pybda.fit.clustering_transformed import ClusteringTransformed
from pybda.globals import FEATURES__
from pybda.io.io import mkdir
from pybda.spark.features import split_vector

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class KMeansTransformed(ClusteringTransformed):
    def __init__(self, data):
        super().__init__(data)

    def write_clusters(self, outpath, suff="", sort_me=True):
        outpath = outpath + "-clusters" + str(suff)
        logger.info("Writing clusters to: %s", outpath)
        mkdir(outpath)
        data = split_vector(self.data, FEATURES__)
        self._write_clusters(data, outpath, sort_me)
