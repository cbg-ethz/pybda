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

import click
import scipy
from pyspark.mllib.linalg.distributed import RowMatrix
from pyspark.sql.functions import udf, col
from pyspark.sql.types import DoubleType

from pybda.spark_model import SparkModel
from pybda.util.cast_as import as_rdd_of_array
from pybda.stats.stats import center, chisquare, precision

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Outliers(SparkModel):
    def __init__(self, spark, pvalue):
        super().__init__(spark)
        self.__pvalue = pvalue

    def fit(self):
        raise NotImplementedError()

    def transform(self):
        raise NotImplementedError()

    def fit_transform(self, data):
        logger.info("Removing outliers..")
        pres = self._precision(data)

        data = data.withColumn("maha", self._mahalanobis(col("features"), pres))

        quant = chisquare(pres, self.__pvalue)
        n = data.count()
        data = data.filter(data.maha < quant)
        logger.info("DataFrame rowcount before/after removal: {}/{}".format(
            n, data.count()))

        return data

    @staticmethod
    def _mahalanobis(column, prec):
        def maha_(v):
            arr = v.toArray()
            arr = scipy.sqrt(arr.dot(prec).dot(arr))
            return float(arr)

        return udf(maha_, DoubleType())(column)

    @staticmethod
    def _precision(data):
        logger.info("Computing precision")
        X = as_rdd_of_array(data.select("features"))
        X = RowMatrix(center(X))
        pres = precision(X)
        return pres


@click.command()
@click.argument("inpath", type=str)
@click.argument("outpath", type=str)
@click.argument("pval", type=float)
def run(inpath, outpath, pval):
    from pybda.spark_session import SparkSession
    from pybda.io.as_filename import as_logfile
    from pybda.io.io import read_parquet, write_parquet
    from pybda.util.string import drop_suffix
    from pybda.logger import set_logger

    outpath = drop_suffix(outpath, "/")
    set_logger(as_logfile(outpath))

    with SparkSession() as spark:
        try:
            outi = Outliers(spark, pval)
            data = outi.fit_transform(read_parquet(spark, inpath))
            write_parquet(data, outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
