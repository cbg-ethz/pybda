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

import pyspark.sql.functions as func
from pyspark import sql
from pyspark.ml.linalg import VectorUDT
from pyspark.mllib.linalg.distributed import RowMatrix
from pyspark.sql.functions import udf
from pybda.globals import FEATURES__
from pybda.spark.features import n_features

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def join(data: sql.DataFrame, X: RowMatrix, spark, on=FEATURES__):
    as_ml = udf(lambda v: v.asML() if v is not None else None, VectorUDT())

    X = spark.createDataFrame(X.rows.map(lambda x: (x,)))
    X = X.withColumnRenamed("_1", on)
    X = X.withColumn(on, as_ml(on))

    ri = "row_index"
    X = X.withColumn(ri, func.monotonically_increasing_id())
    data = data.withColumn(ri, func.monotonically_increasing_id())
    data = data.join(X[ri, on], on=[ri]).drop(ri)

    return data


def as_df(X: RowMatrix, spark):
    return spark.createDataFrame(X.rows.map(lambda x: (x,)))


def as_df_with_idx(X: RowMatrix, idx, spark):
    X = spark.createDataFrame(X.rows.map(lambda x: (x,)))
    X = X.withColumn(idx, func.monotonically_increasing_id())
    return X


def dimension(data):
    n, p = data.count(), n_features(data, FEATURES__)
    logger.info("Using data with n=%d and p=%d", n, p)
    return n, p
