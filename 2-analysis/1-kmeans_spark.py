import argparse
import logging
import pathlib
import re
import sys
import glob

import matplotlib.pyplot as plt
import pyspark
from pyspark.ml.clustering import KMeansModel, KMeans
from pyspark.ml.feature import VectorAssembler
from pyspark.rdd import reduce

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)


def read_args(args):
    parser = argparse.ArgumentParser(description='Cluster an RNAi dataset.')

    subparsers = parser.add_subparsers(dest='subparser_name')
    subparsers.required = True
    parser_p = subparsers.add_parser(
      'plot', help='plot some clustering results')
    parser_p.set_defaults(which="plot")
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
                        metavar="input-file")
    parser_t.add_argument('-k',
                          type=int,
                          help='numbers of clusters',
                          required=True,
                          metavar="cluster-count")
    parser_f.add_argument('-k',
                          type=int,
                          help='numbers of clusters',
                          required=True,
                          metavar="cluster-count")
    opts = parser.parse_args(args)

    return opts.f, opts.o, opts.which, opts


def model_path(outpath):
    return outpath + "/kmeans_fit_"


def k_model_path(outpath):
    return model_path(outpath) + str(k)


def data_path(file_name):
    return file_name.replace(".tsv", "_parquet")


def read_parquet_data(file_name):
    logger.info("Reading parquet: {}".format(file_name))
    return spark.read.parquet(file_name)


def write_parquet_data(file_name, data):
    logger.info("Writing parquet: {}".format(file_name))
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
    feature_columns = list(filter(
      lambda x: any(x.startswith(f) for f in ["cells", "perin", "nucle"]),
      df.columns))
    print(feature_columns)
    for x in feature_columns:
        df = df.withColumn(x, df[x].cast("double"))
    df = df.fillna(0)
    # add a DenseVector column to the frame
    assembler = VectorAssembler(inputCols=feature_columns, outputCol='features')
    data = assembler.transform(df)
    # save the frame
    write_parquet_data(parquet_file, data)

    return data


def plot_cluster(file_name, outpath):
    data = read_parquet_data(data_path(file_name))
    mpaths = glob.glob(model_path(outpath) + "*")
    plotfile = outpath + "/kmeans_performance.eps"

    kmean_fits = []
    for mpath in mpaths:
        K = re.match(".*_(\d+)$", mpath).group(1)
        logger.info("Loading model for K={}".format(K))
        model = KMeansModel.load(mpath)
        kmean_fits.append((K, model, model.computeCost(data)))

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


def fit_cluster(file_name, K, outpath):
    data = get_frame(file_name)
    if not pathlib.Path(outpath).is_dir():
        logger.error("Directory doesnt exist: {}".format(outpath))
        return
    logger.info("Clustering with K: {}".format(K))
    km = KMeans().setK(K).setSeed(23)
    model = km.fit(data)
    model.write().overwrite().save(k_model_path(outpath, K))


def transform_cluster(file_name, k, outpath):
    cpath = data_path(file_name)
    if not pathlib.Path(outpath).is_dir():
        logger.error("Directory doesnt exist: {}".format(cpath))
        return
    mpath = k_model_path(outpath, k)
    if not pathlib.Path(outpath).is_dir():
        logger.error("Directory doesnt exist: {}".format(mpath))
        return

    data = read_parquet_data(cpath)
    model = KMeansModel.load(mpath)
    data = model.transform(data)

    write_parquet_data(cpath, data)


if __name__ == "__main__":
    file_name, outpath, which, opts = read_args(sys.argv[1:])
    if not file_name.endswith(".tsv"):
        logger.error("Please provide a tsv file: " + file_name)
        exit(0)
    if not pathlib.Path(outpath).is_dir():
        logger.error("Please provide an existing path: " + outpath)
        exit(0)
    pyspark.StorageLevel(True, True, False, False, 1)
    conf = pyspark.SparkConf()
    sc = pyspark.SparkContext(conf=conf)
    spark = pyspark.sql.SparkSession(sc)

    if which == "transform":
        transform_cluster(file_name, opts.K, outpath)
    elif which == "fit":
        fit_cluster(file_name, opts.K,  outpath)
    elif which == "plot":
        plot_cluster(file_name, outpath)
    else:
        logger.error("Wrong which chosen: " + which)

    spark.stop()



