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

import numpy
from scipy import stats

import pyspark
from pyspark.mllib.stat import Statistics

from koios.util.cast_as import as_rdd_of_array

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def column_mean(data: pyspark.rdd.RDD):
    """
    Compute vectors of column means.
`
    :param data: an RDD
    :return: returns column means as vector
    """

    logger.info("Computing column means")
    summary = Statistics.colStats(data)
    return summary.mean()


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


def correlation_matrix(data: pyspark.rdd.RDD):
    logger.info("Computing correlation matrix")
    return Statistics.corr(data)


def explained_variance(data):
    """
    Compute the explained variance for the columns of a numpy matrix.

    :param data: a numpy matrix or array
    :return: returns a numpy array with explained variances per column
    """

    if len(data.shape) == 2:
        n, p = data.shape
        # TODO: this might be a bug or rather how dod i come up with this
        var = numpy.apply_along_axis(lambda x: sum(x ** 2) / p, 0, data)
    else:
        var = (data ** 2)
        var /= numpy.sum(var)
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


def center(data: pyspark.rdd.RDD, means=None):
    logger.info("Centering data")
    if means is None:
        means, _ = column_statistics(data)
    data = data.map(lambda x: x - means)
    return data


def scale(data: pyspark.rdd.RDD, means=None, variance=None):
    logger.info("Scaling data")
    if means is None or variance is None:
        means, variance = column_statistics(data)
    data = data.map(lambda x: (x - means) / numpy.sqrt(variance))
    return data


def chisquare(data, pval):
    thresh = 1 - pval
    n, _ = data.shape

    logger.info(
      "Computing chi-square ppf with {} degrees of freedom and {}"
      " percentile".format(n, 100 * thresh))

    return stats.chi2.ppf(q=thresh, df=n)


def sum_of_squared_errors(data: pyspark.sql.DataFrame):
    logger.info("Computing SSE")
    rdd = as_rdd_of_array(data)
    means = column_mean(rdd)
    sse = (rdd
           .map(lambda x: (x - means).T.dot(x - means))
           .reduce(lambda x, y: x + y))
    return sse


def loglik(data: pyspark.sql.DataFrame):
    """
    Computes the log-likelihood using a multivariate normal model

    :param data: data for which loglik is computed
    :return: returns the loglik
    """
    mvn = scipy.stats.multivariate_normal.pdf
    logger.info("Computing loglik")
    rdd = as_rdd_of_array(data)
    means = column_mean(rdd)
    cov = correlation_matrix(rdd)
    loglik = (rdd
              # compute the loglik per observation
              .map(lambda x: scipy.log(mvn(x, means, cov)))
                # since the guys are in logspace we can summarize em
              .reduce(lambda x, y: x + y))
    return loglik
