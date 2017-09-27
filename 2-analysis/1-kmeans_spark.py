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
logger.setLevel(logging.INFO)
frmtr = logging.Formatter(
  '[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

spark = None


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


def file_suffix(file_name):
    suff = re.match(".*/(.*).tsv", file_name).group(1)
    return suff


def path(outpath, mid, file_name):
    return outpath + "/" + mid + file_suffix(file_name)


def model_path(outpath, file_name):
    return path(outpath, "kmeans_fit-", file_name)


def transform_path(outpath, file_name):
    return path(outpath, "kmeans_transform-", file_name)


def plot_path(outpath, mid, file_name):
    return path(outpath, "kmeans_plot-{}-".format(mid), file_name)


def k_path(path, k):
    return path + "_K{:03d}".format(k)


def k_model_path(outpath, filename, k):
    return k_path(model_path(outpath, filename), k)


def k_transform_path(outpath, filename, k):
    return k_path(transform_path(outpath, filename), k)


def k_performance_plot_path(outpath, file_name):
    return plot_path(outpath, "performance", file_name) + ".eps"


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


def get_frame(file_name):
    parquet_file = data_path(file_name)

    # check if data has been loaded before
    if pathlib.Path(parquet_file).exists():
        logger.info("Parquet file exists already: {}".format(file_name))
        return read_parquet_data(parquet_file)

    logger.info("Reading: {} and writing parquet".format(file_name))
    # if not read the file and parse some oclumns
    df = spark.read.csv(path=file_name, sep="\t", header='true')
    old_cols = df.columns
    new_cols = list(map(lambda x: x.replace(".", "_"), old_cols))
    df = reduce(
      lambda data, idx: data.withColumnRenamed(old_cols[idx], new_cols[idx]),
      range(len(new_cols)), df)
    feature_columns = list(filter(
      lambda x: any(x.startswith(f) for f in ["cells", "perin", "nucle"]),
      df.columns))
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
    logger.info("Plotting cluster for: {}".format(file_name))
    data = read_parquet_data(data_path(file_name))
    mpaths = glob.glob(model_path(outpath, file_name) + "*[0-9]")
    plotfile = k_performance_plot_path(outpath, file_name)

    kmean_fits = []
    for mpath in mpaths:
        try:
            K = int(re.match(".*_K(\d+)$", mpath).group(1))
            logger.info("Loading model for K={}".format(K))
            model = KMeansModel.load(mpath)
            kmean_fits.append((K, model, model.computeCost(data)))
        except AttributeError as e:
            logger.error(
                "Could not load model {}, due to: {}".format(mpath, str(e)))
    kmean_fits.sort(key=lambda x: x[0])

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
    logger.info("Saving plot to: {}".format(plotfile))
    plt.savefig(plotfile, bbox_inches="tight")


def fit_cluster(file_name, K, outpath):
    data = get_frame(file_name)
    logger.info("Clustering with K: {}".format(K))
    km = KMeans().setK(K).setSeed(23)
    model = km.fit(data)
    clustout = k_model_path(outpath, file_name, K)
    logger.info("Writing cluster fit to: {}".format(clustout))
    model.write().overwrite().save(clustout)


def transform_cluster(file_name, k, outpath):
    cpath = data_path(file_name)
    mpath = k_model_path(outpath, file_name, k)
    if not pathlib.Path(cpath).is_dir():
        logger.error("Directory doesnt exist: {}".format(cpath))
        return
    if not pathlib.Path(mpath).is_dir():
        logger.error("Directory doesnt exist: {}".format(mpath))
        return

    logger.info("Loading/clustering KMeansModel with k={}".format(k))
    data = read_parquet_data(cpath)
    model = KMeansModel.load(mpath)
    # transform data and selecti
    data = model.transform(data).select(
      "study", "pathogen", "library", "design", "replicate",
      "plate", "well", "gene", "sirna", "well_type",
      "image_idx", "object_idx", "prediction")

    logger.info("Writing clustered data to parquet")
    opath = k_transform_path(outpath, file_name, k)
    write_tsv_data(opath, data)


def loggername(which, outpath, file_name, k=None):
    name = {
        'transform': k_transform_path(outpath, file_name, k),
        'fit': k_model_path(outpath, file_name, k),
        'plot': outpath + "/kmeans_plot-" + file_suffix(file_name)
    }[which]
    return name + ".log"


def run():
    # check files
    file_name, outpath, which, opts = read_args(sys.argv[1:])
    if not file_name.endswith(".tsv"):
        logger.error("Please provide a tsv file: " + file_name)
        return
    if not pathlib.Path(outpath).is_dir():
        logger.error("Outpath does not exist: " + outpath)
        return

    # logging format
    if "k" not in opts:
        opts.k = 0
    hdlr = logging.FileHandler(
      loggername(which, outpath, file_name, opts.k))
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
        transform_cluster(file_name, opts.k, outpath)
    elif which == "fit":
        fit_cluster(file_name, opts.k, outpath)
    elif which == "plot":
        plot_cluster(file_name, outpath)
    else:
        logger.error("Wrong which chosen: " + which)

    spark.stop()


if __name__ == "__main__":
    run()
