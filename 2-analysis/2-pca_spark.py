import argparse
import logging
import pathlib
import re
import sys
import pyspark

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pyspark.ml.feature import PCA
from pyspark.ml.linalg import Vector, Vectors

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
frmtr = logging.Formatter(
  '[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

spark = None


def read_args(args):
    parser = argparse.ArgumentParser(description='PCA on a clustered dataset.')

    subparsers = parser.add_subparsers(dest='subparser_name')
    subparsers.required = True
    parser_p = subparsers.add_parser(
      'plot', help='plot some single cells from a pca')
    parser_p.set_defaults(which="plot")
    parser_t = subparsers.add_parser(
      'transform', help='transform principal components')
    parser_t.set_defaults(which='transform')
    parser.add_argument('-f',
                        type=str,
                        help='the folder where the clustered/transformed data lie',
                        required=True,
                        metavar="input-folder")

    opts = parser.parse_args(args)

    return opts.f, opts.which, opts


def pca_transform_path(folder):
    return re.sub("^kmeans_transform",
                  "pca_transform", folder, 1)


def pca_plot_path(folder):
    return re.sub("^kmeans_transform",
                  "pca_plot", folder, 1)


def read_parquet_data(file_name):
    logger.info("Reading parquet: {}".format(file_name))
    return spark.read.parquet(file_name)


def write_parquet_data(file_name, data):
    logger.info("Writing parquet: {}".format(file_name))
    data.write.parquet(file_name, mode="overwrite")


def plot_pca(folder):
    logger.info("Plotting pcca for: {}".format(folder))
    pca_trans_path = pca_transform_path(folder)
    if not pathlib.Path(pca_trans_path).is_dir():
        logger.error("PCA transform directory doesnt exist: {}"
                     .format(pca_trans_path))
        return

    data = read_parquet_data(pca_trans_path)
    data.group_()


    ks = [x[0] for x in kmean_fits]
    mses = [x[2] for x in kmean_fits]
    plot(ks, mses, "RSS", outpath, file_name)
    aics = [x[3] for x in kmean_fits]
    plot(ks, aics, "AIC", outpath, file_name)
    bics = [x[4] for x in kmean_fits]
    plot(ks, bics, "BIC", outpath, file_name)


def plot(ks, score, axis_label, outpath, file_name):
    plotfile = k_performance_plot_path(outpath, file_name, axis_label)

    font = {'weight': 'normal',
            'family': 'sans-serif',
            'size': 14}
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
    logger.info("Saving plot to: {}".format(plotfile))
    plt.savefig(plotfile, bbox_inches="tight")


def transform_pca(folder):
    if not pathlib.Path(folder).is_dir():
        logger.error("Directory doesnt exist: {}".format(folder))
        return

    logger.info("Loading/clustering Kmeans clustering")
    data = read_parquet_data(folder)

    pca = PCA(k=2, inputCol="features", outputCol="pcs")
    model = pca.fit(data)
    model.transform(data)
    opath = pca_transform_path(folder)
    write_parquet_data(opath, data)


def loggername(which, outpath):
    name = {
        'transform': pca_transform_path(outpath),
        'plot': pca_plot_path(outpath)
    }[which]
    return name + ".log"


def run():
    # check files
    folder, which, opts = read_args(sys.argv[1:])
    if not pathlib.Path(folder).is_dir():
        logger.error("Folder does not exist: " + folder)
        return

    hdlr = logging.FileHandler(loggername(which, folder))
    hdlr.setFormatter(frmtr)
    logger.addHandler(hdlr)

    # spark settings
    pyspark.StorageLevel(True, True, False, False, 1)
    conf = pyspark.SparkConf()
    sc = pyspark.SparkContext(conf=conf)
    global spark
    spark = pyspark.sql.SparkSession(sc)

    # run analysis
    if which == "transform":
        transform_pca(folder)
    elif which == "plot":
        plot_pca(folder)
    else:
        logger.error("Wrong which chosen: " + which)

    spark.stop()


if __name__ == "__main__":
    run()
