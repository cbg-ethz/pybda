#!/usr/bin/env python3

import argparse
import logging
import pathlib
import re
import sys
import glob
import pyspark
import pandas
import scipy
import scipy.stats
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pyspark.ml.clustering import KMeansModel, KMeans
from pyspark.ml.feature import VectorAssembler
from pyspark.rdd import reduce
from pyspark.sql.functions import udf, col, struct
from pyspark.sql.types import ArrayType, DoubleType, StringType
from pyspark.mllib.linalg.distributed import RowMatrix, DenseMatrix
from pyspark.mllib.stat import Statistics

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
frmtr = logging.Formatter(
  '[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

spark = None


class ExplainedVariance():
    def __init__(self, left_boundary, current, right_boundary, K,
                 K_explained_variance, curr_explained_variance,
                 K_sse, curr_sse, max_sse,
                 percent_explained_variance):
        self.__left_boundary = left_boundary
        self.__current = current
        self.__right_boundary = right_boundary
        self.__K = K
        self.__K_explained_variance = K_explained_variance
        self.__curr_explained_variance = curr_explained_variance
        self.__K_sse = K_sse
        self.__curr_sse = curr_sse
        self.__max_sse = max_sse
        self.__percent_explained_variance = percent_explained_variance

    def header(self):
        return "left_bound\tcurrent_model\tright_bound\t" \
               "K_max\tK_expl\tcurrent_expl\tmax_sse\tK_sse\tcurrent_sse\t" \
               "percent_improvement\n"

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
          self.__left_boundary, self.__current, self.__right_boundary,
          self.__K, self.__K_explained_variance, self.__curr_explained_variance,
          self.__max_sse, self.__K_sse, self.__curr_sse,
          self.__percent_explained_variance)


def read_args(args):
    parser = argparse.ArgumentParser(description='Cluster an RNAi dataset.')
    parser.add_argument('-o',
                        type=str,
                        help='the output folder the results are written to',
                        required=True,
                        metavar="output-folder")
    parser.add_argument('-f',
                        type=str,
                        help="the file or folder you want to cluster, This should be a parquet folder"
                             " like 'fa' or 'outlier-removal'",
                        required=True,
                        metavar="input")
    parser.add_argument('-k',
                        type=int,
                        help='maximum numbers of clusters',
                        required=True,
                        metavar="cluster-count")
    opts = parser.parse_args(args)

    return opts.f, opts.o, opts.k, opts


def k_fit_path(outpath, k):
    return outpath + "-K{}".format(k)


def data_path(file_name):
    return file_name.replace(".tsv", "_parquet")


def read_parquet_data(file_name):
    logger.info("Reading parquet: {}".format(file_name))
    return spark.read.parquet(file_name)


def write_parquet_data(file_name, data):
    logger.info("Writing parquet: {}".format(file_name))
    data.write.parquet(file_name, mode="overwrite")


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


def P_(data):
    return len(scipy.asarray(data.select("features").take(1)).flatten())


def split_features(data):
    def to_array(col):
        def to_array_(v):
            return v.toArray().tolist()

        return udf(to_array_, ArrayType(DoubleType()))(col)

    len_vec = len(data.select("features").take(1)[0][0])
    data = (data.withColumn("f", to_array(col("features")))
            .select([col("f")[i] for i in range(len_vec)]))

    for i, x in enumerate(data.columns):
        if x.startswith("f["):
            data = data.withColumnRenamed(
              x, x.replace("[", "_").replace("]", ""))

    return data


def sse(data, outpath):
    """
    Computes the sum of squared errors of the dataset
    """

    sse_file = outpath + "-total_sse.tsv"
    if pathlib.Path(sse_file).exists():
        logger.info("Loading SSE file")
        tab = pandas.read_csv(sse_file, sep="\t")
        sse = tab["SSE"][0]
    else:
        logger.info("Computing SSE of complete dataset")
        rdd = data.rdd.map(list)
        summary = Statistics.colStats(rdd)
        means = summary.mean()

        sse = (RowMatrix(rdd).rows
               .map(lambda x: (x - means).T.dot(x - means))
               .reduce(lambda x, y: x + y))

        with open(sse_file, 'w') as fh:
            fh.write("SSE\n{}\n".format(sse))

    logger.info("\tsse: {}".format(sse))
    return sse


def _estimate_model(total_sse, k, n, p, data, outpath):
    logger.info("\tclustering with K: {}".format(k))
    km = KMeans(k=k, seed=23)
    model = km.fit(data)

    clustout = k_fit_path(outpath, k)
    logger.info("\twriting cluster fit to: {}".format(clustout))
    model.write().overwrite().save(clustout)

    comp_files = clustout + "_cluster_sizes.tsv"
    logger.info("\twriting cluster size file to: {}".format(comp_files))
    with open(clustout + "_cluster_sizes.tsv", 'w') as fh:
        for c in model.summary.clusterSizes:
            fh.write("{}\n".format(c))

    ccf = clustout + "_cluster_centers.tsv"
    logger.info("\triting cluster centers to: {}".format(ccf))
    with open(ccf, "w") as fh:
        fh.write("#Clustercenters\n")
        for center in model.clusterCenters():
            fh.write("\t".join(map(str, center)) + '\n')

    sse_file = clustout + "_loglik.tsv"
    logger.info("\twriting SSE and BIC to: {}".format(sse_file))

    sse = model.computeCost(data)
    expl = 1 - sse / total_sse
    bic = sse + scipy.log(n) * (k * p + 1)
    with open(sse_file, 'w') as fh:
        fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
          "K", "SSE", "ExplainedVariance", "BIC", "N", "P"))
        fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
          k, sse, expl, bic, n, p))

    return {"sse": sse, "expl": expl}


def load_precomputed_models(lrt_file, K, outpath):
    mod = {}
    fls = glob.glob(outpath + "*_loglik.tsv")
    if fls:
        logger.info("Found precomputed ll-files. ")
        for f in fls:
            tab = pandas.read_csv(f, sep="\t")
            sse, expl = tab["SSE"][0], tab["ExplainedVariance"][0]
            k, p = tab["K"][0], tab["P"][0]
            logger.info("\tusing k={}, p={}, sse={}, expl={} from {}"
                        .format(k, p, sse,expl, f))
            mod[k] = {"sse": sse, "expl": expl}
    else:
        logger.info("Starting from scratch...")
    return mod


def estimate_model(total_sse, mods, k, n, p, data, outpath):
    if k in mods.keys():
        logger.info("Loading model k={}".format(k))
        model = mods[k]
    else:
        logger.info("Newly estimating model k={}".format(k))
        model = _estimate_model(total_sse, k, n, p, data, outpath)
        mods[k] = model
    return model


def recursive_clustering(file_name, K, outpath, lrt_file, threshold=.01, maxit=10):
    data = get_frame(file_name)
    logger.info("Recursively clustering with a maximal K: {}".format(K))

    n, p = data.count(), P_(data)
    logger.info("Using data with n={} and p={}".format(n, p))

    lefts, mids, rights = [], [], []
    left, right = 2, K
    mid = int((left + right) / 2)

    mods = load_precomputed_models(lrt_file, K, outpath)
    total_sse = sse(split_features(data), outpath)

    lrts = []
    K_mod = estimate_model(total_sse, mods, right, n, p, data, outpath)
    itr = 0
    while True:
        mids.append(mid)
        lefts.append(left)
        rights.append(right)

        m_mod = estimate_model(total_sse, mods, mid, n, p, data, outpath)

        improved_variance = 1 - m_mod['expl'] / K_mod['expl']
        lrts.append(
          ExplainedVariance(
            left, mid, right, K,
            K_mod['expl'], m_mod['expl'], K_mod["sse"], m_mod['sse'],
            total_sse, improved_variance))
        logger.info("\tVariance reduction for K={} to {}"
                    .format(mid, improved_variance))

        if improved_variance < threshold:
            mid, right = int((left + mid) / 2), mid + 1
        elif improved_variance > threshold:
            mid, left = int((right + mid) / 2), mid
        if left == lefts[-1] and right == rights[-1]:
            break
        if itr >= maxit:
            logger.info("Breaking")
            break
        itr += 1

    return lrts


def write_clustering(clustering, outpath, lrt_file):
    logger.info("Writing LRT file to {}".format(lrt_file))
    with open(lrt_file, "w") as fh:
        fh.write(clustering[0].header())
        for lrt in clustering:
            fh.write(str(lrt))


def fit_cluster(file_name, K, outpath):
    lrt_file = outpath + "-lrt_path.tsv"
    clustering = recursive_clustering(file_name, K, outpath, lrt_file)
    write_clustering(clustering, outpath, lrt_file)


def loggername(outpath):
    return outpath + ".log"


def run():
    # check files
    file_name, outpath, k, opts = read_args(sys.argv[1:])

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

    # run analysis
    fit_cluster(file_name, opts.k, outpath)

    logger.info("Stopping Spark context")
    spark.stop()


if __name__ == "__main__":
    run()
