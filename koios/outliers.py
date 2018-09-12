#!/usr/bin/env python3


import logging

import click
import scipy
from pyspark.mllib.linalg.distributed import RowMatrix
from pyspark.sql.functions import udf, col
from pyspark.sql.types import DoubleType

from koios.util.functions import as_rdd_of_array
from koios.util.stats import center, precision, chisquare

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Outliers:
    def __init__(self, spark, pvalue):
        self.__spark = spark
        self.__pvalue = pvalue

    @staticmethod
    def _mahalanobis(col):
        def maha_(v):
            arr = v.toArray()
            arr = scipy.sqrt(arr.dot(precision).dot(arr))
            return float(arr)

        return udf(maha_, DoubleType())(col)

    def remove_outliers(self, data):
        logger.info("Removing outliers..")
        data = as_rdd_of_array(data.select("features"))
        data = RowMatrix(center(data))
        pres = precision(data)

        data = data.withColumn("maha", self._mahalanobis(col("features")))
        quant = chisquare(pres, self.__pvalue)
        n = data.count()
        data = data.filter(data.maha < quant)
        logger.info("DataFrame rowcount before/after removal: {}/{}"
                    .format(n, data.count()))

        return data


@click.command()
@click.argument("inpath", type=str)
@click.argument("outpath", type=str)
@click.argument("pval", type=float)
def run(inpath, outpath, pval):
    from koios.spark_session import SparkSession
    from koios.io.io import read_parquet, write_parquet, as_logfile
    from koios.util.string import drop_suffix
    from koios.logger import set_logger

    outpath = drop_suffix(outpath, "/")
    set_logger(as_logfile(outpath))

    with SparkSession() as spark:
        try:
            outi = Outliers(spark, pval)
            data = outi.remove_outliers(read_parquet(spark, inpath))
            write_parquet(data, outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
