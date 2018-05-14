#!/usr/bin/env python3

import argparse
import logging
import pathlib
import re
import sys
import glob
import pyspark
import pandas
import numpy
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pyspark.ml.clustering import KMeansModel, KMeans
from pyspark.ml.feature import VectorAssembler
from pyspark.rdd import reduce

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
frmtr = logging.Formatter(
  '[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

spark = None


def read_args(args):
    parser = argparse.ArgumentParser(description='Cluster an RNAi dataset.')
    parser.add_argument('-o',
                        type=str,
                        help='the output folder the results are written to',
                        required=True,
                        metavar="output-folder")
    parser.add_argument('-f',
                        type=str,
                        help='the file or filder you want to cluster, i.e. a file derived '
                             'from rnai-query like '
                             'cells_sample_10_normalized_cut_100.tsv or '
                             'cells_sample_10_normalized_cut_100_factors. If it '
                             'is a folder we assume it is a parquet.',
                        required=True,
                        metavar="input")
    parser.add_argument('-k',
                          type=int,
                          help='numbers of clusters',
                          required=True,
                          metavar="cluster-count")
    opts = parser.parse_args(args)

    return opts.f, opts.o, opts.k, opts


def k_fit_path(outpath, k):
    return outpath + "-K{}".format(k)


def data_path(file_name):
    return file_name.replace(".tsv", "_parquet")


def read_parquet_data(file_name):
    logger.info("Reading parquet: {}".format(file_name))
    return spark.read.parquet(file_name)


def write_parquet_data(file_name, data):
    logger.info("Writing parquet: {}".format(file_name))
    data.write.parquet(file_name, mode="overwrite")


def get_feature_columns(data):
    return list(filter(
      lambda x: any(x.startswith(f) for f in ["cells", "perin", "nucle"]),
      data.columns))


def get_frame(file_name):
    if pathlib.Path(file_name).is_dir():
        logger.info("File is a dictionary. Assuming parquet file: {}".format(
          file_name))
        return read_parquet_data(file_name)

    parquet_file = data_path(file_name)
    # check if data has been loaded before
    if pathlib.Path(parquet_file).exists():
        logger.info("Parquet file exists already using parquet file: {}".format(
            file_name))
        return read_parquet_data(parquet_file)

    logger.info("Reading: {} and writing parquet".format(file_name))
    # if not read the file and parse some oclumns
    df = spark.read.csv(path=file_name, sep="\t", header='true')
    old_cols = df.columns
    new_cols = list(map(lambda x: x.replace(".", "_"), old_cols))
    df = reduce(
      lambda data, idx: data.withColumnRenamed(old_cols[idx], new_cols[idx]),
      range(len(new_cols)), df)
    feature_columns = get_feature_columns(df)
    for x in feature_columns:
        df = df.withColumn(x, df[x].cast("double"))
    df = df.fillna(0)
    # add a DenseVector column to the frame
    assembler = VectorAssembler(inputCols=feature_columns, outputCol='features')
    data = assembler.transform(df)

    # save the frame
    write_parquet_data(parquet_file, data)

    return data


def fit_cluster(file_name, K, outpath):
    data = get_frame(file_name)

    logger.info("Clustering with K: {}".format(K))
    km = KMeans().setK(K).setSeed(23)
    model = km.fit(data)

    clustout = k_fit_path(outpath, K)
    logger.info("Writing cluster fit to: {}".format(clustout))
    model.write().overwrite().save(clustout)

    logger.info("Writing clusterSize file")
    clust_sizes = model.summary.clusterSizes
    thefile = open(clustout + "_clusterSizes.tsv", 'w')
    for c in clust_sizes:
        thefile.write("{}\n".format(c))


def loggername(outpath, file_name, k=None):
    return k_fit_path(outpath, k) + ".log"


def run():
    # check files
    file_name, outpath, k, opts = read_args(sys.argv[1:])

    # logging format
    hdlr = logging.FileHandler(
      loggername(outpath, file_name, k))
    hdlr.setFormatter(frmtr)
    logger.addHandler(hdlr)

    if not pathlib.Path(file_name).exists():
        logger.error("Please provide a file: " + file_name)
        return

    logger.info("Starting Spark context")

    # spark settings
    pyspark.StorageLevel(True, True, False, False, 1)
    conf = pyspark.SparkConf()
    sc = pyspark.SparkContext(conf=conf)
    global spark
    spark = pyspark.sql.SparkSession(sc)

    # run analysis
    fit_cluster(file_name, opts.k, outpath)

    logger.info("Stopping Spark context")
    spark.stop()

if __name__ == "__main__":
    run()
