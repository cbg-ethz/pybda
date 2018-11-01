#!/usr/bin/env python3


import logging

import click
import scipy
from pyspark.mllib.linalg.distributed import RowMatrix
from pyspark.sql.functions import udf, col
from pyspark.sql.types import DoubleType

from koios.spark_model import SparkModel
from koios.util.cast_as import as_rdd_of_array
from koios.math.stats import center, precision, chisquare

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
        logger.info("DataFrame rowcount before/after removal: {}/{}"
                    .format(n, data.count()))

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
    from koios.spark_session import SparkSession
    from koios.io.as_filename import as_logfile
    from koios.io.io import read_parquet, write_parquet
    from koios.util.string import drop_suffix
    from koios.logger import set_logger

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
