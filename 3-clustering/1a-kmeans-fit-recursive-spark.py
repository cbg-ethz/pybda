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
            .select(["prediction"] + [col("f")[i] for i in range(len_vec)]))

    for i, x in enumerate(data.columns):
        if x.startswith("f["):
            data = data.withColumnRenamed(
              x, x.replace("[", "_").replace("]", ""))

    return data


def n_param_kmm(k, p):
    n_mean = k * p
    n_var = 1
    return n_mean + n_var


def cluster_stats(K, data, model, p):
    """
    Computes the variance of the clustering and the number of cells per cluster.
    """
    total_var = 0
    ni = scipy.zeros(K)

    for i in range(K):
        # get only the cells of a specific clustering
        data_cluster = data.filter("prediction==" + str(i)).drop("prediction")
        # number of clusters
        ni[i] = data_cluster.count()
        rdd = data_cluster.rdd.map(list)
        # get the current mean vector (i should need to test this again)
        means = model.clusterCenters()[i]
        # compute the variance
        var = (RowMatrix(rdd).rows
               .map(lambda x: (x - means).T.dot(x - means))
               .reduce(lambda x, y: x + y))
        total_var += var
    # sum the variances and compute the unbiased estimate
    total_var /= (data.count() - K) * p

    return total_var, ni


def loglik(variance, ni, K, n, p, model):
    ll = 0
    for i in range(K):
        l = ni[i] * scipy.log(ni[i])
        l -= ni[i] * scipy.log(n)
        l -= .5 * ni[i] * p * scipy.log(2 * scipy.pi * variance)
        l -= .5 * (ni[i] - 1) * p
        ll += l
    bic = ll - .5 * scipy.log(n) * (p + 1) * K

    return ll, bic


def get_model_likelihood(k, n, p, data, outpath):
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
    logger.info("\twriting likelihood and BIC to: {}".format(sse_file))
    transformed_data = split_features(model.transform(data))
    variance, cells_per_cluster = cluster_stats(k, transformed_data, model, p)
    ll, bic = loglik(variance, cells_per_cluster, k, n, p, model)
    n_params = n_param_kmm(k, p)
    with open(sse_file, 'w') as fh:
        fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
          "K", "LogLik", "BIC", "N", "P", "Var"))
        fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
          k, ll, bic, n, p, variance))

    return {"ll": ll, "n_params": n_params}


def lrt(max_loglik, loglik, max_params, params):
    t = 2 * (max_loglik - loglik)
    df = max_params - params
    if df <= 0:
        return (1, t, df)
    p_val = 1 - scipy.stats.chi2.cdf(t, df=df)
    return (p_val, t, df)


def load_models(lrt_file, k):
    mod = {}
    if pathlib.Path(lrt_file).exists():
        tab = pandas.read_csv(lrt_file, sep="\t", header=0)
        if tab["K_max"][0] != k:
            logger.info(
              "Need to start from scratch because file-K({}) =!= current-K({})".format(tab["K_max"][0], k))
        else:
            logger.info("\tusing precomputed likelihoods from {}".format(lrt_file))
            for x in range(tab.shape[0]):
                mod[tab["current_model"][x]] = {
                    "ll": tab["current_loglik"][x],
                    "n_params": tab["current_nparams"][x]
                }
    else:
        logger.info("\tstarting from scratch...")
    return mod


def get_model(mods, k, n, p, data, outpath):
    if k in mods.keys():
        logger.info("loading model k={}".format(k))
        model = mods[k]
    else:
        logger.info("newly estimating model k={}".format(k))
        model = get_model_likelihood(k, n, p, data, outpath)
        mods[k] = model
    return model


def fit_cluster(file_name, K, outpath):
    data = get_frame(file_name)
    logger.info("Recursively clustering with a maximal K: {}".format(K))

    n, p = data.count(), P_(data)
    logger.info("Using data with n={} and p={}".format(n, p))

    lefts, mids, rights = [], [], []
    left, right = 2, K
    mid = int((left + right) / 2)
    lrts = []

    lrt_file = outpath + "-lrt_path.tsv"
    mods = load_models(lrt_file, K)
    logger.info("Writing LRT file to {}".format(lrt_file))
    with open(lrt_file, "w") as fh:
        fh.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
          "left_bound", "current_model", "right_bound", "K_max", "Kmax_loglik", "current_loglik",
          "Kmax_nparams", "current_nparams", "LRT_pval", "LRT_t", "LRT_df"))

        K_model = get_model(mods, right, n, p, data, outpath)
        l_rt = lrt(K_model['ll'], K_model["ll"], K_model["n_params"], K_model["n_params"])
        fh.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
           left, mid, right, K, K_model['ll'], K_model["ll"],
           K_model["n_params"], K_model["n_params"], l_rt[0], l_rt[1], l_rt[2]))

        while True:
            mids.append(mid)
            lefts.append(left)
            rights.append(right)

            m_model = get_model(mods, mid, n, p, data, outpath)

            l_rt = lrt(K_model['ll'], m_model["ll"],  K_model["n_params"], m_model["n_params"])
            pval = l_rt[0]
            fh.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
              left, mid, right, K, K_model['ll'], m_model["ll"],
              K_model["n_params"], m_model["n_params"], l_rt[0], l_rt[1], l_rt[2]))
            logger.info("Creating model for K={} with LRT p-value {}".format(mid, pval))
            lrts.append(pval)

            if pval > p:
                mid, right = int((left + mid) / 2) , mid + 1
            elif pval < p:
                mid, left = int((right + mid) / 2) , mid - 1
            if left == lefts[-1] and right == rights[-1] and mid == mids[-1]:
                break


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
