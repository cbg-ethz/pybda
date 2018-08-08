
import time
import argparse
import logging
import sys
import pandas
import pathlib
import pyspark
import numpy
import re
import glob
import scipy
from scipy import spatial

from functools import partial
import multiprocessing as mp

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
frmtr = logging.Formatter(
  '[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

spark = None


def read_args(args):
    parser = argparse.ArgumentParser(
      description="Compute statistics of a clustered dataset."
      " The script computes some summary statistics about the number"
      " of cells (classified by gene/pathogen) and some silhouette scores.")
    parser.add_argument('-f',
                        type=str,
                        help="the folder where the  data lie,"
                             " i.e. 'kmeans-transformed'",
                        required=True, metavar="input-folder")

    opts = parser.parse_args(args)
    return opts.f, opts


def read_parquet_data(file_name):
    logger.info("Reading parquet: {}".format(file_name))
    return spark.read.parquet(file_name)


def write_parquet_data(file_name, data):
    logger.info("Writing parquet: {}".format(file_name))
    data.write.parquet(file_name, mode="overwrite")


def write_pandas_tsv(file_name, data):
    data.to_csv(file_name, sep="\t", index=False)


def count_statistics(data, folder, what):
    dnts = data.groupby(what).count()
    dnts = dnts.select(what + ["count"]).dropDuplicates()
    outfolder = folder + "-statistics-" + "_".join(what) + "_counts"
    logger.info("Writing sample table to: {}".format(outfolder))
    dnts.write.csv(path=outfolder, sep="\t", header=True, mode="overwrite")


def read_matrices(files):
    logger.info("Reading files into data frame")
    l = [None] * len(files)
    for i, fl in enumerate(files):
        df = pandas.read_csv(
            fl, sep="\t", nrows=1000,
            usecols=lambda x: x.startswith("f_") or x.startswith("pred"))
        l[i] = df
    df = pandas.concat(l)
    sh =  df.shape
    logger.info("Read data frame with dimension ({} x {})".format(sh[0], sh[1]))
    return df


def read_matrix(fl):
    return pandas.read_csv(fl, sep="\t", nrows=1000,
                           usecols=lambda x: x.startswith("f_"))


def compute_silhouettes(outfolder):
    start = time.clock()
    out_silhouette = outfolder + "-statistics-silhouette.tsv"
    logger.info("Writing silhouettes to: {}".format(out_silhouette))

    files = [x for x in glob.glob(outfolder + "-clusters/cluster*")  \
             if x.endswith(".tsv")]
    K = len(files)
    mat = read_matrices(files)
    with open(out_silhouette, "w") as ot:
        logger.info("Opening file IO")
        ot.write("#Cluster\tNeighbor\tSilhouette\n")
        for current_idx in range(K):
            logger.info("Doing file {}".format(current_idx))
            _compute_silhouette(current_idx, K, ot, mat)
    logger.info("TIme {}".format(time.clock() - start))


def _compute_silhouette(current_idx, K, ot, mat):
    #np_i = read_matrix(outfiles[i])
    min_cluster, min_distance = mp_min_distance(current_idx, K, mat)
    within_distance = _mean_distance(current_idx, current_idx, mat)
    silhouette = (min_distance - within_distance) / \
        numpy.maximum(min_distance, within_distance)
    for clust, sil in zip(min_cluster, silhouette):
        ot.write("{}\t{}\t{}".format(current_idx, clust, sil) + "\n")


def mp_min_distance(current_idx, K, mat):
    itr = numpy.array([j for j in range(K) if j != current_idx])
    distances = [_mean_distance(it, current_idx, mat) for it in itr]
    distances = numpy.vstack(distances).T
    argmins = numpy.argmin(distances, axis=1)
    min_distances = numpy.min(distances, axis=1)
    arg = itr[argmins]
    return arg, min_distances


def _mean_distance(it, current_idx, df):
    """Computes distances between np array and np_j"""
    #np_j = read_matrix(outfiles[j])
    distances = scipy.spatial.distance.cdist(
        df[df.prediction == current_idx].iloc[:, 1:],
        df[df.prediction == it].iloc[:, 1:])
    return numpy.mean(distances, axis=1)


def statistics(outfolder):

    logger.info("Loading Kmeans clustering")
    data = read_parquet_data(outfolder)

    # Group the data by some criteria dnd plot the statistics as parquet files
    #count_statistics(data, outfolder, ["gene", "prediction"])
    #count_statistics(data, outfolder, ["pathogen", "prediction"])
    #count_statistics(data, outfolder, ["gene", "pathogen", "prediction"])
    compute_silhouettes(outfolder)


def run():
    # check files
    folder, opts = read_args(sys.argv[1:])
    if not pathlib.Path(folder).is_dir():
        logger.error("Folder does not exist: " + folder)
        return

        # logging format
    hdlr = logging.FileHandler(folder + "-statistics.log")
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
        statistics(folder)
    except Exception as e:
        logger.error("Random exception: {}".format(str(e)))

    logger.info("Stopping Spark context")
    spark.stop()


if __name__ == "__main__":
    run()
