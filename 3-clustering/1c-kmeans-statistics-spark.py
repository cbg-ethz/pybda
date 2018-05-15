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
      description='Compute statistics of a clustered PCA-dataset.')
    parser.add_argument('-f',
                        type=str,
                        help='the folder where the pca data lie,'
                             ' i.e. transform-*_K005',
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
    #dnts.write.csv(path=outfile, sep="\t", header=True)
    dnts.toPandas().to_csv(outfolder + ".tsv", sep="\t")


def compute_silhouettes(outfolder):
    out_silhouette = outfolder + "-statistics-silhouette.tsv"
    logger.info("Writing silhouettes to: {}".format(out_silhouette))

    files = [x for x in glob.glob(outfolder + "-clusters/*") if x.endswith(".tsv")]    
    K = len(files)
    with open(out_silhouette, "w") as ot:
        ot.write("#Cluster\tNeighbor\tSilhouette\n")
        for i in range(K):
            _compute_silhouette(files, i, K, ot)


def read_matrix(fl):
    matr = pandas.read_csv(fl, sep="\t", nrows=1000, usecols=["features"])
    return matr["features"].str.split(",", expand=True).as_matrix().astype(
        numpy.float64)


def _compute_silhouette(outfiles, i, K, ot):
    np_i = read_matrix(outfiles[i])
    min_cluster, min_distance = mp_min_distance(i, K, np_i, outfiles)
    within_distance = _mean_distance(i, np_i, outfiles)
    silhouette = (min_distance - within_distance) / numpy.maximum(min_distance,
                                                                  within_distance)
    for clust, sil in zip(min_cluster, silhouette):
        ot.write("{}\t{}\t{}".format(i, clust, sil) + "\n")


def mp_min_distance(i, K, np_i, outfiles):
    n_cores = mp.cpu_count()
    itr = numpy.array([j for j in range(K) if j != i])
    distances = [_mean_distance(i, np_i, outfiles) for i in itr]
    distances = numpy.vstack(distances).T
    argmins = numpy.argmin(distances, axis=1)
    min_distances = numpy.min(distances, axis=1)
    arg = itr[argmins]
    return arg, min_distances


def _mean_distance(j, np, outfiles):
    """Computes distances between np array and np_j"""
    distance = 0
    cnt = 0
    np_j = read_matrix(outfiles[j])
    distances = scipy.spatial.distance.cdist(np, np_j)
    return numpy.mean(distances, axis=1)


def statistics(outfolder):

    logger.info("Loading Kmeans clustering")
    data = read_parquet_data(outfolder)

    # Group the data by some criteria dnd plot the statistics as parquet files
    count_statistics(data, outfolder, ["gene", "prediction"])
    count_statistics(data, outfolder, ["pathogen", "prediction"])
    count_statistics(data, outfolder, ["gene", "pathogen", "prediction"])
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
