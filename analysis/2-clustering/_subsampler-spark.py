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
    parser = argparse.ArgumentParser(description='Sample genes from clustered dataset.')
    parser.add_argument('-f',
                        type=str,
                        help='the folder where the clustered/transformed data lie,'
                             ' i.e. kmeans_transform-*_K005',
                        required=True,
                        metavar="input-folder")
    parser.add_argument('-g',
                        type=str,
                        help='comma separated list of genes',
                        required=True,
                        metavar="input-folder")
    opts = parser.parse_args(args)

    return opts.f, opts.g, opts


def read_parquet_data(file_name):
    logger.info("Reading parquet: {}".format(file_name))
    return spark.read.parquet(file_name)


def write_pandas_tsv(file_name, data):
    data.to_csv(file_name, sep="\t", index=False)


def sample(folder, genes):
    if not pathlib.Path(folder).is_dir():
        logger.error("Directory doesnt exist: {}".format(folder))
        return

    logger.info("Loading Kmeans clustering")
    data = read_parquet_data(folder)
    opath = folder + "_sampled_genes.tsv"
    data = data.where(data.gene.isin(genes.split(",")))
    write_pandas_tsv(opath, data.toPandas())


def run():
    # check files
    folder, genes, opts = read_args(sys.argv[1:])
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
        sample(folder, genes)
    except Exception as e:
        logger.error("Random exception: {}".format(str(e)))
    spark.stop()


if __name__ == "__main__":
    run()
