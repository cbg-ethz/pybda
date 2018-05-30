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

from pyspark.ml.clustering import GaussianMixture, GaussianMixtureModel
from pyspark.ml.feature import VectorAssembler
from pyspark.rdd import reduce
from pyspark.sql.functions import udf, col
from pyspark.sql.types import ArrayType, DoubleType

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
                              "this is probablt a folder called 'gmm-transformed'",
                        required=True,
                        metavar="output-folder")
    parser.add_argument('-f',
                        type=str,
                        help="the folder originally used for clustering. "
                             "this is probably a folder called 'outlier-removal' or so",
                        required=True,
                        metavar="input")
    parser.add_argument('-c',
                        type=str,
                        help="the folder prefix used for clustering. "
                             "this is probaly a folder called 'gmm-fit'",
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


def k_fit_bics(clusterprefix):
    logger.info("\tloading Logliks")
    gmm_fits = []
    mreg =  re.compile(".*K\d+_loglik.tsv$")
    for x in glob.glob(clusterprefix + "*"):
        if mreg.match(x):
            tab = pandas.read_csv(x, sep='\t')
            logger.info("\tloading model for K={}".format(tab["K"][0]))
            gmm_fits.append({
                 "K":   tab["K"][0],
                 "N":   tab["N"][0],
                 "P":   tab["P"][0],
                 "Loglik": tab["Loglik"][0],
                 "BIC": tab["BIC"][0],
                 "path": clusterprefix + "-K" + str(tab["K"][0])
            })
    gmm_fits.sort(key=lambda x: x["K"])

    return gmm_fits


def cluster_center_file(outpath):
    return outpath + "-cluster_centers.tsv"


def get_feature_columns(data):
    return list(filter(
      lambda x: any(x.startswith(f) for f in ["cells", "perin", "nucle"]),
      data.columns))


def plot_cluster(outpath, gmm_fits):
    plotpath = outpath + "-bic"
    logger.info("Writing cluster BICs to: {}".format(plotpath))

    gmm_fits.sort(key=lambda x: x["K"])
    ks  = [ x["K"] for x in gmm_fits ]
    bic = [ x["BIC"] for x in gmm_fits ]

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

    gmm_fits = k_fit_bics(clusterprefix)
    plot_cluster(outpath, gmm_fits)

    min_fit = min(list(enumerate(gmm_fits)), key=lambda x:x[1]["BIC"])[1]

    return min_fit


def split_features(data):
    def to_array(col):
        def to_array_(v):
            return v.toArray().tolist()

        return udf(to_array_, ArrayType(DoubleType()))(col)

    logger.info("\tcomputing feature vectors")
    len_vec = len(data.select("features").take(1)[0][0])
    data = (data.withColumn("f", to_array(col("features")))
            .select(data.columns + [col("f")[i] for i in range(len_vec)])
            .drop("features"))

    for i, x in enumerate(data.columns):
        if x.startswith("f["):
            data = data.withColumnRenamed(
                x, x.replace("[", "_").replace("]", ""))

    return data


def write_clusters(data, outfolder):
    cluster_counts = numpy.array(
      data.select("prediction").dropDuplicates().collect()).flatten()

    outpath = outfolder + "-clusters"
    if not pathlib.Path(outpath).exists():
        pathlib.Path(outpath).mkdir()

    data = split_features(data)

    logger.info("Writing clusters to: {}".format(outpath))
    file_names = [""] * len(cluster_counts)
    for i in cluster_counts:
        outfile = "{}/cluster-{}.tsv".format(outpath, i)
        if pathlib.Path(outfile).is_file():
            continue
        data_i = data.filter("prediction={}".format(i))
        data_i.toPandas().sample(frac=1).to_csv(outfile, sep="\t", index=0)


def transform_cluster(datafolder, outpath, clusterprefix):
    data = read_parquet_data(datafolder)

    brst_model =  get_optimal_k(data, outpath, clusterprefix)
    logger.info("Using model: {}".format(brst_model))
    k = brst_model["K"]

    model = GaussianMixtureModel.load(brst_model["path"])

    # transform data and select
    data = model.transform(data).select(
      "study", "pathogen", "library", "design", "replicate",
      "plate", "well", "gene", "sirna", "well_type",
      "image_idx", "object_idx", "prediction", "features")
    logger.info("Writing clustered data to parquet")

    write_parquet_data(outpath, data)
    write_clusters(data, outpath)


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
