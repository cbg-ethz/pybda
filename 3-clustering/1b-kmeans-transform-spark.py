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
    opts = parser.parse_args(args)

    return opts.f, opts.o, opts


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
    kmean_fits = []
    for mpath in mpaths:
        try:
            # parameteres
            K = int(re.match(".*_K(\d+)$", mpath).group(1))
            logger.info("Loading model for K={}".format(K))
            model = KMeansModel.load(mpath)
            rss = model.computeCost(data)
            N = data.count()
            P = 10
            bic_3 = rss + numpy.log(N) * K * P
            bic_2 =  N + N * numpy.log(2 * numpy.pi) + N * numpy.log(rss/N) + numpy.log(N) * (K + 1)
            bic = N * numpy.log(rss / N) + K * numpy.log(N)

            kmean_fits.append((K, model, bic, bic_2, bic_3))

        except AttributeError as e:
            logger.error(
              "Could not load model {}, due to: {}".format(mpath, str(e)))
    kmean_fits.sort(key=lambda x: x[0])
    print(kmean_fits)
    return kmean_fits


def plot_cluster(file_name, outpath):
    logger.info("Plotting cluster for: {}".format(file_name))
    data = get_frame(file_name)
    mpaths = [x for x in
              glob.glob(model_path(outpath, file_name) + "*K*") if
              pathlib.Path(x).is_dir()]

    logger.info("Mpath: {}".format("\n".join(mpaths)))
    logger.info("Models path:  {}".format(model_path(outpath, file_name)))

    kmean_fits = get_kmean_fit_statistics(mpaths, data)

    ks = [x[0] for x in kmean_fits]
    bic = [x[2] for x in kmean_fits]
    plot(ks, mses, "BIC", outpath, file_name)
    bic2 = [x[3] for x in kmean_fits]
    plot(ks, aics, "BIC 2", outpath, file_name)
    bic3 = [x[4] for x in kmean_fits]
    plot(ks, bics, "BIC 3", outpath, file_name)


def plot(ks, score, axis_label, outpath, file_name):
    plotfile = k_performance_plot_path(outpath, file_name, axis_label)

    statistics_file = plotfile.replace("eps", "tsv")
    pandas.DataFrame(data={ "index": ks, "stat": score }).to_csv(statistics_file, sep="\t", index=0)

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





def transform_cluster(file_name, outpath):
    bic =  get_optimal_k()


    cpath = data_path(file_name)
    mpath = k_model_path(outpath, file_name, k)
    if not pathlib.Path(cpath).is_dir():
        logger.error("Directory doesnt exist: {}".format(cpath))
        return
    if not pathlib.Path(mpath).is_dir():
        logger.error("Directory doesnt exist: {}".format(mpath))
        return

    logger.info("Loading data: {}".format(cpath))
    logger.info("Loading model: {}".format(mpath))
    logger.info("Loading/clustering KMeansModel with k={}".format(k))
    data = read_parquet_data(cpath)
    model = KMeansModel.load(mpath)

    copath = k_transform_centers_path(outpath, file_name, k)
    logger.info("Writing cluster centers to: {}".format(copath))
    with open(copath, "w") as fh:
        fh.write("#Clustercenters\n")
        for center in model.clusterCenters():
            fh.write("\t".join(map(str, center)) + '\n')

    # transform data and select
    data = model.transform(data).select(
      "study", "pathogen", "library", "design", "replicate",
      "plate", "well", "gene", "sirna", "well_type",
      "image_idx", "object_idx", "prediction", "features")
    logger.info("Writing clustered data to parquet")

    opath = k_transform_path(outpath, file_name, k)
    write_parquet_data(opath, data)


def loggername(outpath, file_name):
    return outpath + ".log"


def run():
    # check files
    file_name, outpath, opts = read_args(sys.argv[1:])

    # logging format
    hdlr = logging.FileHandler(loggername(outpath))
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


    transform_cluster(file_name, outpath)

    logger.info("Stopping Spark context")
    spark.stop()


if __name__ == "__main__":
    run()
