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
                        help="the folder originally used for clustering. "
                             "this is probaly a folder called 'outlier-detection or so'",
                        required=True,
                        metavar="input")
    parser.add_argument('-c',
                        type=str,
                        help="the folder prefix used for clustering. "
                             "this is probaly a folder called 'kmeans-fit'",
                        required=True,
                        metavar="input")
    opts = parser.parse_args(args)

    return opts.f, opts.o, opts.c, opts


def data_path(file_name):
    return file_name.replace(".tsv", "_parquet")


def read_parquet_data(file_name):
    logger.info("Reading parquet: {}".format(file_name))
    return spark.read.parquet(file_name)


def write_parquet_data(file_name, data):
    logger.info("Writing parquet: {}".format(file_name))
    data.write.parquet(file_name, mode="overwrite")


def write_tsv_data(file_name, data):
    logger.info("Writing tsv: {}".format(file_name))
    data.write.csv(file_name, mode="overwrite", header=True, sep="\t")


def k_fit_folders(clusterprefix):
    mpaths = []
    mreg =  re.compile(".*K\d+$")
    for x in glob.glob(clusterprefix + "*"):
         if pathlib.Path(x).is_dir():
             if mreg.match(x):
                 mpaths.append(x)
    return mpaths


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


def get_kmean_fit_statistics(mpaths, data):
    logger.info("\tcomputing fit statistics using BIC")
    kmean_fits = []
    for mpath in mpaths:
        try:
            # Get number of clusters
            K = int(re.match(".*_K(\d+)$", mpath).group(1))
            logger.info("\tloading model for K={}".format(K))
            model = KMeansModel.load(mpath)
            rss = model.computeCost(data)
            # number of samples
            N = data.count()
            # number of predictors (feature dimensionality)
            P = len(numpy.asarray(df.select("features").take(1)).flatten())
            bic = rss + numpy.log(N) * K * P
            kmean_fits.append({"K": K, "model": model, "BIC": bic})
        except AttributeError as e:
            logger.error(
                "\tcould not load model {}, due to: {}".format(mpath, str(e)))
    kmean_fits.sort(key=lambda x: x["K"])

    return kmean_fits


def plot_cluster(outpath, kmean_fits):
    plotpath = outpath + "-bic"
    logger.info("Plotting cluster BICs to: {}".format(plotpath))

    kmean_fits.sort(key=lambda x: x["K"])
    ks  = [ x["K"] for x in kmean_fits ]
    bic = [ x["BIC"] for x in kmean_fits ]

    statistics_file = plotpath + ".tsv"
    logger.info("\tsaving bic tsv to: {}".format(statistics_file))
    pandas.DataFrame(data={ "index": ks, "stat": bic }) \
        .to_csv(statistics_file, sep="\t", index=0)
        
    plot(ks, bic, "BIC", plotpath)

def plot(ks, score, axis_label, outpath, file_name):

    plotfile = outpath + ".eps"
    font = {'weight': 'normal', 'family': 'sans-serif', 'size': 14}
    plt.rc('font', **font)
    plt.figure()
    ax = plt.subplot(111)
    plt.tick_params(axis="both", which="both", bottom="off", top="off",
                    labelbottom="on", left="off", right="off", labelleft="on")
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(True)

    ax.plot(ks, score, "black")
    ax.plot(ks, score, "or")
    plt.xlabel('K', fontsize=15)
    plt.ylabel(axis_label, fontsize=15)
    plt.title('')
    ax.grid(True)
    logger.info("\tsaving plot to: {}".format(plotfile))
    plt.savefig(plotfile, bbox_inches="tight")


def get_optimal_k(datafolder, clusterprefix):
    logger.info("Finding optimal K for transformation...")

    data = get_frame(datafolder)
    mpaths = k_fit_folders(clusterprefix)
    kmeans_fits = get_kmean_fit_statistics(mpaths, data)

    plot_cluster(outpath)



def transform_cluster(datafolder, outpath, clusterprefix):
    bic =  get_optimal_k(datafolder, clusterprefix)
    # cpath = data_path(file_name)
    # mpath = k_model_path(outpath, file_name, k)
    # if not pathlib.Path(cpath).is_dir():
    #     logger.error("Directory doesnt exist: {}".format(cpath))
    #     return
    # if not pathlib.Path(mpath).is_dir():
    #     logger.error("Directory doesnt exist: {}".format(mpath))
    #     return
    #
    # logger.info("Loading data: {}".format(cpath))
    # logger.info("Loading model: {}".format(mpath))
    # logger.info("Loading/clustering KMeansModel with k={}".format(k))
    # data = read_parquet_data(cpath)
    # model = KMeansModel.load(mpath)
    #
    # copath = k_transform_centers_path(outpath, file_name, k)
    # logger.info("Writing cluster centers to: {}".format(copath))
    # with open(copath, "w") as fh:
    #     fh.write("#Clustercenters\n")
    #     for center in model.clusterCenters():
    #         fh.write("\t".join(map(str, center)) + '\n')
    #
    # # transform data and select
    # data = model.transform(data).select(
    #   "study", "pathogen", "library", "design", "replicate",
    #   "plate", "well", "gene", "sirna", "well_type",
    #   "image_idx", "object_idx", "prediction", "features")
    # logger.info("Writing clustered data to parquet")
    #
    # opath = k_transform_path(outpath, file_name, k)
    # write_parquet_data(opath, data)


def loggername(outpath):
    return outpath + ".log"


def run():
    # check files
    datafolder, outpath, clusterprefix, opts = read_args(sys.argv[1:])

    # logging format
    hdlr = logging.FileHandler(loggername(outpath))
    hdlr.setFormatter(frmtr)
    logger.addHandler(hdlr)

    if not pathlib.Path(datafolder).exists():
        logger.error("Please provide a file: " + datafolder)
        return

    logger.info("Starting Spark context")

    # spark settings
    pyspark.StorageLevel(True, True, False, False, 1)
    conf = pyspark.SparkConf()
    sc = pyspark.SparkContext(conf=conf)
    global spark
    spark = pyspark.sql.SparkSession(sc)


    transform_cluster(datafolder, outpath, clusterprefix)

    logger.info("Stopping Spark context")
    spark.stop()


if __name__ == "__main__":
    run()
