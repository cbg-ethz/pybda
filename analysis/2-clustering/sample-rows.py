import argparse
import logging
import pathlib
import re
import sys
import uuid
import pandas
import pyspark

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pyspark.ml.feature import PCA
from pyspark.ml.linalg import Vector, Vectors
from pyspark.sql.window import Window
from pyspark.ml.feature import StandardScaler
from pyspark.sql.functions import row_number

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
frmtr = logging.Formatter(
  '[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')


spark = None


def read_args(args):
    parser = argparse.ArgumentParser(
      description='Sample genes from clustered dataset.')
    parser.add_argument('-f',
                        type=str,
                        help='parquet folder with data',
                        required=True,
                        metavar="input-folder")
    parser.add_argument('-o',
                        type=str,
                        help='output file will be tsv',
                        required=True,
                        metavar="output file")
    parser.add_argument('-n',
                        type=int,
                        help='number of samples',
                        required=True,
                        metavar="input-folder")
    opts = parser.parse_args(args)

    return opts.f, opts.o, opts.n, opts


def read_parquet_data(file_name):
    logger.info("Reading parquet: {}".format(file_name))
    return spark.read.parquet(file_name)


def write_pandas_tsv(file_name, data):
    data.to_csv(file_name, sep="\t", index=False)


def sample(folder, outfile, n_samples):
    if not pathlib.Path(folder).is_dir():
        logger.error("Directory doesnt exist: {}".format(folder))
        return

    logger.info("Loading data")
    data = read_parquet_data(folder)
    opath = folder + "_sampled_genes.tsv"
    data = data.sample(False, 0.1, seed=23).limit(n_samples)
    write_pandas_tsv(outfile, data.toPandas())


def run():
    # check files
    folder, out, n_samples,   opts = read_args(sys.argv[1:])
    if not pathlib.Path(folder).is_dir():
        logger.error("Folder does not exist: " + folder)
        return

    # spark settings
    pyspark.StorageLevel(True, True, False, False, 1)
    conf = pyspark.SparkConf()
    sc = pyspark.SparkContext(conf=conf)
    global spark
    spark = pyspark.sql.SparkSession(sc)
    try:
        sample(folder, out, n_samples)
    except Exception as e:
        logger.error("Random exception: {}".format(str(e)))
    spark.stop()


if __name__ == "__main__":
    run()
