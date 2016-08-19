# Copyright (C) 2018 Simon Dirmeier
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

import scipy
from pyspark.mllib.linalg.distributed import RowMatrix

from pybda.spark.dataframe import as_df_with_idx

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def svd(data: RowMatrix, n_components=None):
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
    var = scipy.dot(s, s)
    if n_components is not None:
        var = scipy.dot(s[n_components:], s[n_components:])
        s, V = s[:n_components], V[:n_components]
    return s, V, var


def elementwise_product(X: RowMatrix, Y: RowMatrix, spark):
    X = as_df_with_idx(X, "idx", spark)
    Y = as_df_with_idx(Y, "idx", spark)
    Y = Y.withColumnRenamed("_1", "_2")
    X = X.join(Y, on="idx").drop("idx")
    X = X.rdd.map(lambda x: scipy.array(x[0]) * scipy.array(x[1]))
    return X
