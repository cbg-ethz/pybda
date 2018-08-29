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
import pathlib
import sys

import numpy
import pandas
import pyspark
import pyspark.mllib.linalg.distributed
import pyspark.sql.functions as func
import scipy
from pyspark.ml.linalg import VectorUDT
from pyspark.mllib.linalg.distributed import RowMatrix, DenseMatrix
from pyspark.mllib.stat import Statistics
from pyspark.rdd import reduce
from pyspark.sql.functions import udf


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

class FactorAnalysis:

    def __init__(self, spark, config):
        self.__spark =  spark
        self.__config = config



def svd(X, comps):
    svd = X.computeSVD(X.numCols(), computeU=False)
    s = svd.s.toArray()
    V = svd.V.toArray().T
    var = numpy.dot(s[comps:], s[comps:])
    return s[:comps], V[:comps], var


def tilde(X, psi_sqrt, n_sqrt):
    norm = psi_sqrt * n_sqrt
    Xtilde = RowMatrix(X.rows.map(lambda x: x / norm))
    return Xtilde


def stats(data):
    logger.info("\tcomputing data statistics")
    rdd = data.select(get_feature_columns(data)).rdd.map(list)
    summary = Statistics.colStats(rdd)
    return RowMatrix(rdd), summary.mean(), summary.variance()


def fit(X, var, n_components):
    iter, DELTA, MAX_ITER = 0, 1e-12, 100
    N, P = X.numRows(), X.numCols()

    ll = old_ll = -numpy.inf
    llconst = P * numpy.log(2. * numpy.pi) + n_components
    logliks = []

    psi = numpy.ones(P, dtype=numpy.float64)
    nsqrt = numpy.sqrt(N)

    logger.info("\tcomputing factor analysis")
    for i in range(MAX_ITER):
        sqrt_psi = numpy.sqrt(psi) + DELTA
        s, V, unexp_var = svd(tilde(X, sqrt_psi, nsqrt), n_components)
        s = s ** 2

        # factor updated
        W = numpy.sqrt(numpy.maximum(s - 1., 0.))[:, numpy.newaxis] * V
        W *= sqrt_psi

        # loglik update
        ll = llconst + numpy.sum(numpy.log(s))
        ll += unexp_var + numpy.sum(numpy.log(psi))
        ll *= -N / 2.
        logliks.append(ll)

        # variance update
        psi = numpy.maximum(var - numpy.sum(W ** 2, axis=0), DELTA)
        if numpy.abs(ll - old_ll) < 0.001:
            break
        old_ll = ll

    return W, logliks, psi


def transform(X, W, psi):
    logger.info("\ttransforming data")
    Ih = numpy.eye(len(W))
    Wpsi = W / psi
    cov_z = scipy.linalg.inv(Ih + numpy.dot(Wpsi, W.T))
    tmp = numpy.dot(Wpsi.T, cov_z)
    tmp_dense = DenseMatrix(
      numRows=tmp.shape[0], numCols=tmp.shape[1], values=tmp.flatten())

    as_ml = udf(lambda v: v.asML() if v is not None else None, VectorUDT())

    X = X.multiply(tmp_dense)
    X = spark.createDataFrame(X.rows.map(lambda x: (x,)))
    X = X.withColumnRenamed("_1", "features")
    X = X.withColumn("features", as_ml("features"))

    return X


def fa(file_name, outpath, ncomp):
    if not pathlib.Path(file_name).is_file():
        logger.error("File doesnt exist: {}".format(file_name))
        return
    if pathlib.Path(outpath).is_file():
        logger.error("Not a path: {}".format(outpath))
        return

    data = get_frame(file_name)
    features = get_feature_columns(data)

    logger.info("Running factor analysis ...")
    X, means, var = stats(data)
    X = RowMatrix(X.rows.map(lambda x: x - means))
    W, ll, psi = fit(X, var, ncomp)
    X = transform(X, W, psi)

    X = X.withColumn('row_index', func.monotonically_increasing_id())
    data = data.withColumn('row_index', func.monotonically_increasing_id())
    data = data.join(X["row_index", "features"],
                     on=["row_index"]).drop("row_index")
    del X

    write_parquet_data(outpath, data)

    logger.info("\twriting factor to data")
    W = pandas.DataFrame(data=W)
    W.columns = features
    W.to_csv(outpath + "_factors.tsv", sep="\t", index=False)

    logger.info("\twriting likelihood profile")
    L = pandas.DataFrame(data=ll)
    L.to_csv(outpath + "_likelihood.tsv", sep="\t", index=False)
