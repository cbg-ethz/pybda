import os
import sys

import logging
import pandas
import numpy
import argparse


import matplotlib.pyplot as plt
import pathlib

import pyspark
from pyspark.sql.window import Window
import pyspark.sql.functions as func
from pyspark.rdd import reduce
from pyspark.sql.types import DoubleType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeansModel, KMeans
from pyspark.ml.linalg import SparseVector, VectorUDT, Vector, Vectors


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def read_args(args):
    parser = argparse.ArgumentParser(description='Cluster an RNAi dataset.')

    subparsers = parser.add_subparsers(help='sub-command help')
    parser_f = subparsers.add_parser(
      'fit', help='fit some k means models to determine the best')
    parser_f.set_defaults(which='fit')
    parser_t = subparsers.add_parser(
      'transform', help='put data into clusters')
    parser_t.set_defaults(which='transform')
    parser.add_argument('-o',
                        type=str,
                        help='the output folder the results are written to',
                        required=True,
                        metavar="output-folder")
    parser.add_argument('-f',
                        type=str,
                        help='the file you want to cluster',
                        required=True,
                        metavar="input file")
    parser_t.add_argument('K',
                          type=int,
                          help='numbers of clusters',
                          required=True)
    opts = parser.parse_args(args)

    return opts.f, opts.o, opts.which, opts


def model_path(outpath, k):
    return outpath + "/kmeans_fit_" + str(k)


def data_path(file_name):
    return file_name.replace(".tsv", "_parquet")


def read_parquet_data(file_name):
    return spark.read.parquet(file_name)


def write_parquet_data(file_name, data):
    data.write.parquet(file_name, mode="overwrite")

def get_frame(file_name):
    parquet_file = data_path(file_name)
    # check if data has been loaded before
    if pathlib.Path(parquet_file).exists():
        return read_parquet_data(parquet_file)
    # if not read the file and parse some oclumns
    df = spark.read.csv(path=file_name, sep="\t", header='true')
    old_cols = df.schema.names
    new_cols = list(map(lambda x: x.replace(".", "_"), old_cols))
    df = reduce(
      lambda data, idx: data.withColumnRenamed(old_cols[idx], new_cols[idx]),
      range(len(new_cols)), df)
    feature_columns = filter(
      lambda x: any(x.startswith(f) for f in ["cells", "perin", "nucle"]),
      df.columns)
    for x in feature_columns:
        df = df.withColumn(x, df[x].cast("double"))
    df = df.fillna(0)
    # add a DenseVector column to the frame
    assembler = VectorAssembler(inputCols=feature_columns, outputCol='features')
    data = assembler.transform(df)
    # save the frame
    write_parquet_data(parquet_file, data)

    return data


def plot(kmean_fits, outpath):
    plotfile = outpath + "/kmeans_performance.eps"

    ks = [x[0] for x in kmean_fits]
    mses = [x[2] for x in kmean_fits]

    font = {'weight': 'normal',
            'family': 'sans-serif',
            'size': 14}
    plt.rc('font', **font)

    ax = plt.subplot(111)
    plt.tick_params(axis="both", which="both", bottom="off", top="off",
                    labelbottom="on", left="off", right="off", labelleft="on")
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)

    ax.plot(ks, mses, "black")
    ax.plot(ks, mses, "or")
    plt.xlabel('K', fontsize=15)
    plt.ylabel('RSS', fontsize=15)
    plt.title('')
    ax.grid(True)

    plt.savefig(plotfile, bbox_inches="tight")


def fit_cluster(file_name, outpath):
    data = get_frame(file_name)
    if not pathlib.Path(outpath).is_dir():
        logger.error("Directory doesnt exist: {}".format(outpath))
        return
    # try several kmean_fits
    kmean_fits = []
    for k in range(2, 11):
        km = KMeans().setK(k).setSeed(23)
        model = km.fit(data)
        model.write().overwrite().save(model_path(outpath, k))
        kmean_fits.append((k, model, model.computeCost(data)))

    plot(kmean_fits, outpath)


def transform_cluster(file_name, k, outpath):
    cpath = data_path(file_name)
    if not pathlib.Path(outpath).is_dir():
        logger.error("Directory doesnt exist: {}".format(cpath))
        return
    mpath = model_path(outpath, k)
    if not pathlib.Path(outpath).is_dir():
        logger.error("Directory doesnt exist: {}".format(mpath))
        return
    data = read_parquet_data(cpath)
    model = KMeansModel.load(data)
    model.transform(data)
    write_parquet_data(cpath, data)


if __name__ == "__main__":
    pyspark.StorageLevel(True, True, False, False, 1)
    conf = pyspark.SparkConf()
    sc = pyspark.SparkContext(conf=conf)
    spark = pyspark.sql.SparkSession(sc)

    file_name, outpath, which, opts = read_args(sys.argv[1:])
    if not file_name.endswith(".tsv"):
        raise ValueError("Please provide a tsv file: " + file_name)
    if which == "transform":
        transform_cluster(file_name, opts.K, outpath)
    elif which == "fit":
        fit_cluster(file_name, outpath)
    else:
        logger.error("Wrong which chosen: " + which)

    spark.stop()



