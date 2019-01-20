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
import pyspark
from pyspark.mllib.linalg import DenseMatrix
from pyspark.mllib.linalg.distributed import RowMatrix
import scipy

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def svd(data: RowMatrix, n_components):
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


def precision(data: pyspark.rdd.RDD):
    logger.info("Computing precision")
    return scipy.linalg.inv(data.computeCovariance().toArray())

def fourier(X: RowMatrix, n_features, seed=23, gamma=1):
    p = X.numCols()

    random_state = numpy.random.RandomState(seed)
    w = numpy.sqrt(2 * gamma) * random_state.normal(size=(p, n_features))
    w = DenseMatrix(p, n_features, w.flatten())
    b = random_state.uniform(0, 2 * numpy.pi, size=n_features)

    Y = X.multiply(w)
    Y = Y.rows.map(lambda x: numpy.sqrt(2.0 / n_features) * numpy.cos(x + b))

    return RowMatrix(Y)
