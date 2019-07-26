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

import numpy
import scipy
from scipy import stats, linalg

import pyspark
from pyspark.mllib.linalg import DenseMatrix
from pyspark.mllib.linalg.distributed import RowMatrix
from pyspark.mllib.stat import Statistics

from pybda.decorators import timing
from pybda.util.cast_as import as_rdd_of_array

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def group_mean(data: pyspark.sql.DataFrame, groups, response, features):
    means = scipy.zeros((len(groups), len(features)))
    for i, target in enumerate(groups):
        df_t = data.filter("{} == {}".format(response, target))
        X_t = df_t.select(features).rdd.map(numpy.array)
        means[i, :] = column_means(X_t)
    return means


def column_means(data: pyspark.rdd.RDD):
    """
    Compute vectors of column means.
`
    :param data: an RDD
    :return: returns column means as vector
    """

    logger.info("Computing data means")
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


def covariance_matrix(data: pyspark.mllib.linalg.distributed.RowMatrix):
    logger.info("Computing covariance")
    return data.computeCovariance().toArray()


def precision(data: pyspark.mllib.linalg.distributed.RowMatrix):
    logger.info("Computing precision")
    return scipy.linalg.inv(covariance_matrix(data))


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
        _, p = data.shape
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
        n = data.count()
        variance = variance * (n - 1) / n
    sd = numpy.sqrt(variance)
    data = data.map(lambda x: (x - means) / sd)
    return data, means, variance


def chisquare(data, pval):
    thresh = 1 - pval
    n, _ = data.shape

    logger.info(
      "Computing chi-square ppf with %d degrees of freedom and %d"
      " percentile", n, 100 * thresh)

    return stats.chi2.ppf(q=thresh, df=n)


def sum_of_squared_errors(data: pyspark.sql.DataFrame):
    logger.info("Computing SSE")
    rdd = as_rdd_of_array(data)
    means = column_means(rdd)
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
    means = column_means(rdd)
    cov = correlation_matrix(rdd)
    loglik = (rdd
              # compute the loglik per observation
              .map(lambda x: scipy.log(mvn(x, means, cov)))
              # since the guys are in logspace we can summarize em
              .reduce(lambda x, y: x + y))
    return loglik


def within_group_scatter(data: pyspark.sql.DataFrame,
                         features, response, targets):
    p = len(features)
    sw = numpy.zeros((p, p))
    for target in targets:
        df_t = data.filter("{} == '{}'".format(response, target))
        X_t = RowMatrix(df_t.select(features).rdd.map(numpy.array))
        sw += X_t.computeCovariance().toArray() * (df_t.count() - 1)
    return sw


def fourier_transform(X, w, b):
    Y = X.multiply(w)
    n_feat = len(b)
    Y = Y.rows.map(lambda x: numpy.sqrt(2.0 / n_feat) * numpy.cos(x + b))
    return RowMatrix(Y)


@timing
def fourier(X: RowMatrix, n_features, seed=23, gamma=1):
    p = X.numCols()
    random_state = numpy.random.RandomState(seed)

    w = numpy.sqrt(2 * gamma) * random_state.normal(size=(p, n_features))
    w = DenseMatrix(p, n_features, w.flatten(), isTransposed=True)
    b = random_state.uniform(0, 2 * numpy.pi, size=n_features)

    Y = fourier_transform(X, w, b)
    return Y, w, b


def normalized_cumsum(vec):
    return numpy.cumsum(vec / numpy.sum(vec))


def sym_decorrelate(w):
    s, u = linalg.eigh(numpy.dot(w, w.T))
    return numpy.dot(numpy.dot(u * (1. / numpy.sqrt(s)), u.T), w)


def gs_decorrelate(w, W, j):
    w -= scipy.dot(scipy.dot(w, W[:j].T), W[:j])
    return w
