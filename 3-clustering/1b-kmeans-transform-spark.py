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
import matplotlib.ticker as ticker

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
                        help="the output folder the results are written to. "
                              "this is probablt a folder called 'kmeans-transformed'",
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


def transform_path(outpath):
    return outpath


def cluster_center_file(outpath):
    return outpath + "-cluster_centers.tsv"


def get_feature_columns(data):
    return list(filter(
      lambda x: any(x.startswith(f) for f in ["cells", "perin", "nucle"]),
      data.columns))


def get_kmean_fit_statistics(mpaths, data):
    logger.info("\tcomputing fit statistics using BIC")
    kmean_fits = []
    for mpath in mpaths:
        try:
            # Get number of clusters
            K = int(re.match(".*-K(\d+)$", mpath).group(1))
            logger.info("\tloading model for K={}".format(K))
            model = KMeansModel.load(mpath)
            rss = model.computeCost(data)
            # number of samples
            N = data.count()
            # number of predictors (feature dimensionality)
            P = len(numpy.asarray(data.select("features").take(1)).flatten())
            bic = rss + numpy.log(N) * K * P
            kmean_fits.append({"K": K, "model": model, "BIC": bic, "path": mpath})
        except AttributeError as e:
            logger.error(
                "\tcould not load model {}, due to: {}".format(mpath, str(e)))
    kmean_fits.sort(key=lambda x: x["K"])

    return kmean_fits


def plot_cluster(outpath, kmean_fits):
    plotpath = outpath + "-bic"
    logger.info("Writing cluster BICs to: {}".format(plotpath))

    kmean_fits.sort(key=lambda x: x["K"])
    ks  = [ x["K"] for x in kmean_fits ]
    bic = [ x["BIC"] for x in kmean_fits ]

    statistics_file = plotpath + ".tsv"
    logger.info("\tsaving bic tsv to: {}".format(statistics_file))
    pandas.DataFrame(data={ "index": ks, "stat": bic }) \
        .to_csv(statistics_file, sep="\t", index=0)

    ks = [int(x) for x in ks]
    plot(ks, bic, "BIC", plotpath)


def plot(ks, score, axis_label, outpath):
    plotfile = outpath

    plt.style.use(["seaborn-whitegrid"])
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = 'Lucida Grande'
    _, ax = plt.subplots(figsize=(7, 4), dpi=720)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(True)
    ax.spines["left"].set_visible(True)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_label_coords(x=.9, y=-0.1)
    ax.yaxis.set_label_coords(x=-0.06, y=.95)
    ax.grid(linestyle="")
    ax.grid(which="major", axis="x", linestyle="-", color="gainsboro")
    #ax.tick_params(length=3.5, color="black")
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_color('black')

    min_idx = min(list(enumerate(score)), key=lambda x:x[1])[0]
    ax.plot(ks, score, "black", alpha=.5)
    ax.plot(ks, score, "ok")
    ax.plot(ks[min_idx], score[min_idx], marker="o", color="#65ADC2")

    for index, label in enumerate(ax.xaxis.get_ticklabels()):
        if index % 2 == 0:
            label.set_visible(False)
    for label in ax.yaxis.get_ticklabels()[::2]:
        label.set_visible(False)

    plt.xlabel('Number of clusters', fontsize=15)
    plt.ylabel(axis_label, fontsize=15)
    plt.title('')

    logger.info("\tsaving plot to: {}.eps/svg/png".format(plotfile))
    plt.savefig(plotfile + ".eps", bbox_inches="tight")
    plt.savefig(plotfile + ".svg", bbox_inches="tight")
    plt.savefig(plotfile + ".png", bbox_inches="tight")


def get_optimal_k(data, outpath, clusterprefix):
    logger.info("Finding optimal K for transformation...")

    mpaths = k_fit_folders(clusterprefix)
    kmeans_fits = get_kmean_fit_statistics(mpaths, data)

    plot_cluster(outpath, kmeans_fits)

    min_fit = min(list(enumerate(kmeans_fits)), key=lambda x:x[1]["BIC"])[1]

    return min_fit


def transform_cluster(datafolder, outpath, clusterprefix):
    data = read_parquet_data(datafolder)

    brst_model =  get_optimal_k(data, outpath, clusterprefix)
    logger.info("Using model: {}".format(brst_model))
    k = brst_model["K"]

    model = KMeansModel.load(brst_model["path"])
    ccf = cluster_center_file(outpath)
    logger.info("Writing cluster centers to: {}".format(ccf))

    with open(ccf, "w") as fh:
        fh.write("#Clustercenters\n")
        for center in model.clusterCenters():
            fh.write("\t".join(map(str, center)) + '\n')

    # transform data and select
    data = model.transform(data).select(
      "study", "pathogen", "library", "design", "replicate",
      "plate", "well", "gene", "sirna", "well_type",
      "image_idx", "object_idx", "prediction", "features")
    logger.info("Writing clustered data to parquet")

    opath = transform_path(outpath)
    write_parquet_data(opath, data)


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

    try:
        transform_cluster(datafolder, outpath, clusterprefix)
    except Exception as e:
        logger.error("Some error: {}".format(str(e)))

    logger.info("Stopping Spark context")
    spark.stop()


if __name__ == "__main__":
    run()
