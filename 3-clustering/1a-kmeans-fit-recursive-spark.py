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
    return len(numpy.asarray(data.select("features").take(1)).flatten())

def split_features(data):
    def to_array(col):
        def to_array_(v):
            return v.toArray().tolist()

        return udf(to_array_, ArrayType(DoubleType()))(col)

    len_vec = len(data.select("features").take(1)[0][0])
    data = (data.withColumn("f", to_array(col("features")))
            .select(["prediction"]+  [col("f")[i] for i in range(len_vec)]))

    for i, x in enumerate(data.columns):
        if x.startswith("f["):
            data = data.withColumnRenamed(
                x, x.replace("[", "_").replace("]", ""))

    return data

def n_param_kmm(k, p):
    n_mean = k * p
    n_var = 1
    return n_mean + n_var


def compute_variance(K, data, model, p):
    total_var = 0
    ni = scipy.zeros(K)
    p = len(data.take(1)[0]) - 1

    for i in range(K):
        data_cluster = data.filter("prediction==" + str(i)).drop("prediction")
        ni[i] =  data_cluster.count()
        rdd = data_cluster.rdd.map(list)
        means = model.clusterCenters()[i]
        var = (RowMatrix(rdd).rows
                   .map(lambda x: (x - means).T.dot(x - means))
                   .reduce(lambda x, y: x + y))
        total_var += var
    total_var /= ((data.count() - K) * p)

    return total_var, ni


def loglik(data, K, model):
    n = data.count()
    p = len(data.take(1)[0]) - 1
    total_var, ni = compute_variance(K, data, model, p)
    ll = 0

    for i in range(K):
        l = ni[i] * scipy.log(ni[i])
        l -= ni[i] * scipy.log(n)
        l -= .5 * ni[i] * p * scipy.log(2 * scipy.pi * total_var)
        l -= .5 * (ni[i] - 1) * p
        ll += l
    bic = ll - .5 * scipy.log(n) * (p + 1) * K

    return ll, bic, total_var, ni


def lrt(max_loglik, loglik, max_params, params):
    t = 2 * (max_loglik - loglik)
    df = max_params - params
    if df == 0:
        return 1
    p_val = 1 - scipy.stats.chi2.cdf(t, df=df)
    return p_val

def get_model(k, data):
    mod = KMeans(k=k, seed=23).fit(data)
    transformed_data = split_features(mod.transform(data))
    ll, bic, var, ni = loglik(transformed_data, k, mod)
    n_params = n_param_kmm(k, p)
    return (ll, bic, var, ni, n_params)


def fit_cluster(file_name, K, outpath):
    data = get_frame(file_name)
    logger.info("Recursively clustering with a maximal K: {}".format(K))

    lefts, mids, rights = [], [], []
    left, right = 2, K
    mid = int((left + right) / 2)
    lrts = []

    K_model = get_model(right, df)
    mods = {}
    while True:
        mids.append(mid)
        lefts.append(left)
        rights.append(right)

        if mid in mods.keys():
            m_model = mods[mid]
        else:
            m_model = get_model(mid, df)
            mods[mid] = m_model

        l_rt = lrt(K_model[0], m_model[0], K_model[-1], m_model[-1])
        logger.info("{} {} {} {} {} {} {}".format(left, mid, right, K_model[0], m_model[0], K_model[-1], m_model[-1], l_rt))
        lrts.append(l_rt)

        if l_rt > p:
            mid, right = int((left + mid) / 2), mid + 1
        elif l_rt < p:
            mid, left = int((right + mid) / 2), mid - 1
        print(left, mid, right)
        if left == lefts[-1] and right == rights[-1]:
            break

    return mid, left, right







    km = KMeans().setK(K).setSeed(23)
    model = km.fit(data)

    clustout = k_fit_path(outpath, K)
    logger.info("Writing cluster fit to: {}".format(clustout))
    model.write().overwrite().save(clustout)
    sse = model.computeCost(data)

    comp_files = clustout + "_cluster_sizes.tsv"
    logger.info("Writing cluster size file to: {}".format(comp_files))
    with open(clustout + "_cluster_sizes.tsv", 'w') as fh:
        for c in model.summary.clusterSizes:
            fh.write("{}\n".format(c))

    ccf = clustout + "_cluster_centers.tsv"
    logger.info("Writing cluster centers to: {}".format(ccf))
    with open(ccf, "w") as fh:
        fh.write("#Clustercenters\n")
        for center in model.clusterCenters():
            fh.write("\t".join(map(str, center)) + '\n')

    sse_file = clustout + "_sse.tsv"
    logger.info("Writing sse to: {}".format(sse_file))
    P = P_(data)
    N = data.count()
    bic = sse + numpy.log(N) * K * P
    with open(sse_file, 'w') as fh:
        fh.write("{}\t{}\t{}\t{}\t{}\n".format("K", "SSE", "BIC",  "N", "P"))
        fh.write("{}\t{}\t{}\t{}\t{}\n".format(K, sse, bic, N, P))


def loggername(outpath, file_name, k=None):
    return k_fit_path(outpath, k) + ".log"


def run():
    # check files
    file_name, outpath, k, opts = read_args(sys.argv[1:])

    # logging format
    hdlr = logging.FileHandler(
      loggername(outpath, file_name, k))
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
