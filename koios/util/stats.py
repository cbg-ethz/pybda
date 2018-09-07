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
import scipy
import pyspark
from pyspark.mllib.stat import Statistics

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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

    logger.info("Computing SVD")
    svd = data.computeSVD(data.numCols(), computeU=False)
    s = svd.s.toArray()
    V = svd.V.toArray().T
    var = scipy.dot(s[n_components:], s[n_components:])
    return s[:n_components], V[:n_components], var


def explained_variance(data):
    """
    Compute the explained variance for the columns of a numpy matrix.

    :param data: a numpy matrix
    :return: returns a numpy array with explained variances per column
    """

    n, p = data.shape
    var = numpy.apply_along_axis(lambda x: sum(x ** 2) / p, 0, data)

    return var


def cumulative_explained_variance(data, sort=True):
    """
    Compute the cumulative explained variance for the columns of a
    numpy matrix. If sorted is set to false, the variances are not sorted
    before cumulation.

    :param data: a numpy matrix
    :param sort: boolean of the variances should be sorted decreasingly.
     This is the default.
    :return: returns a numpy array with cumulative variances
    """

    var = explained_variance(data)
    return numpy.cumsum(sorted(var, reverse=sort))