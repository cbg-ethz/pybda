#!/usr/bin/env python3

import argparse
import logging
import pathlib
import sys
import pandas
from numpy import linalg
from scipy import stats

import pyspark
from pyspark.sql.functions import udf, col, struct
from pyspark.sql.types import ArrayType, DoubleType, StringType
from pyspark.mllib.linalg.distributed import RowMatrix, DenseMatrix
from pyspark.mllib.stat import Statistics

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
frmtr = logging.Formatter(
  "[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s")

spark = None


def read_args(args):
    parser = argparse.ArgumentParser(description="Do a factor analysis.")
    parser.add_argument("-o",
                        type=str,
                        help="the output folder the results are written to",
                        required=True,
                        metavar="output-folder")
    parser.add_argument("-f",
                        type=str,
                        help="the input folder of the dimensionality reduced "
                             "data (e.g. FA/kPCA/PCA folder). A column called "
                             "'features' of type 'DenseVector' is expected",
                        required=True,
                        metavar="input-folder")
    opts = parser.parse_args(args)

    return opts.f, opts.o, opts


def read_parquet_data(file_name):
    logger.info("\treading parquet: {}".format(file_name))
    return spark.read.parquet(file_name)


def write_parquet_data(outpath, data):
    logger.info("\twriting parquet: {}".format(outpath))
    data.write.parquet(outpath, mode="overwrite")


def check_columns(data):
    if "features" not in data.columns:
        raise ValueError("DataFrame does not contain column 'features'")


def split_features(data):
    def to_array(col):
        def to_array_(v):
            return v.toArray().tolist()

        return udf(to_array_, ArrayType(DoubleType()))(col)

    logger.info("\tcomputing feature vectors")
    len_vec = len(data.select("features").take(1)[0][0])
    data = (data.withColumn("f", to_array(col("features")))
            .select(data.columns + [col("f")[i] for i in range(len_vec)]))

    for i, x in enumerate(data.columns):
        if x.startswith("f["):
            data = data.withColumnRenamed(
                x, x.replace("[", "_").replace("]", ""))

    return data


def center(data):
    logger.info("\tcentering data")
    data = split_features(data)
    f_cols = [x for x in data.columns if x.startswith("f_")]

    rdd = data.select(f_cols).rdd.map(list)
    means = Statistics.colStats(rdd).mean()
    X = RowMatrix(RowMatrix(rdd).rows.map(lambda x: x - means))
    return X


def get_precision_matrix(X):
    logger.info("\tcomputing precision")
    precision = linalg.inv(X.computeCovariance().toArray())
    return precision


def remove_outliers_(data):
    precision = get_precision_matrix(center(data))

    def maha(col):
        def maha_(v):
            arr = v.toArray()
            arr = arr.dot(precision).dot(arr)
            return float(arr)
        return udf(maha_, DoubleType())(col)

    data = data.withColumn("maha", maha(col("features")))
    logger.info("\tcomputing chi-square ppf with {} degrees of freedom and {}" \
                " percentile".format(precision.shape[0], 95))
    quant = stats.chi2.ppf(q=.95, df=precision.shape[0])
    logger.info("\tdataFrame rowcount before removal: {}".format(data.count()))
    data = data.filter(data.maha < quant)
    logger.info("\tdataFrame rowcount after removal: {}".format(data.count()))
    return data


def remove_outliers(infolder, outpath):
    if not pathlib.Path(infolder).is_dir():
        logger.error("infolder is not a directory")
        return

    logger.info("Removing outliers..")
    data = read_parquet_data(infolder)
    check_columns(data)

    data = remove_outliers_(data)
    write_parquet_data(outpath, data)


def run():
    # check files
    infolder, outpath, opts = read_args(sys.argv[1:])

    if outpath.endswith("/"):
        outpath = outpath[:-1]
    hdlr = logging.FileHandler(outpath + ".log")
    hdlr.setFormatter(frmtr)
    logger.addHandler(hdlr)

    logger.info("Starting Spark context")

    # spark settings
    pyspark.StorageLevel(True, True, False, False, 1)
    conf = pyspark.SparkConf()
    sc = pyspark.SparkContext(conf=conf)
    global spark
    spark = pyspark.sql.SparkSession(sc)

    try:
        remove_outliers(infolder, outpath)
    except Exception as e:
        logger.error("Some error: {}".format(str(e)))

    logger.info("Stopping Spark context")
    spark.stop()


if __name__ == "__main__":
    run()
