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
import pyspark
from pyspark.mllib.stat import Statistics

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def column_statistics(data: pyspark.rdd.RDD):
    """
    Compute vectors of column means and variances of a data frame.
`
    :param data: an RDD
    :return: returns column means and variances as vectors
    """

    logger.info("Computing data statistics")
    summary = Statistics.colStats(data)
    return summary.mean(), summary.variance()


def svd(data, n_components):
    """
    Computes a singular value decomposition on a data matrix and the variance
    that is explained by the first n_components.

    :param data: a data frame
    :param n_components: number of components to be returned
    :return: returns the estimated components of a SVD.
    :rtype: a triple of (s, V, var)
    """

    svd = data.computeSVD(data.numCols(), computeU=False)
    s = svd.s.toArray()
    V = svd.V.toArray().T
    var = scipy.dot(s[n_components:], s[n_components:])
    return s[:n_components], V[:n_components], var
