import argparse
import logging
import pathlib
import sys
import numpy
import scipy
import pyspark
import pandas
from scipy import linalg

from pyspark.rdd import reduce
import pyspark.sql.functions as func
import pyspark.mllib.linalg.distributed
from pyspark.mllib.linalg.distributed import RowMatrix, DenseMatrix
from pyspark.mllib.stat import Statistics

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
frmtr = logging.Formatter(
  '[%(levelname)-1s/%(processName)-1s/%(name)-1s]: %(message)s')

spark = None


def read_args(args):
    parser = argparse.ArgumentParser(description='Do a factor analysis.')
    parser.add_argument('-o',
                        type=str,
                        help='the output folder the results are written to',
                        required=True,
                        metavar="output-folder")
    parser.add_argument('-f',
                        type=str,
                        help='the file you want to do FA on'
                             'from rnai-query like '
                             'cells_sample_10_normalized_cut_100.tsv',
                        required=True,
                        metavar="input-file")
    opts = parser.parse_args(args)

    return opts.f, opts.o, opts


def get_feature_columns(data):
    return list(filter(
      lambda x: any(x.startswith(f) for f in ["cells", "perin", "nucle"]),
      data.columns))


def data_path(file_name):
    return file_name.replace(".tsv", "_parquet")


def read_parquet_data(file_name):
    logger.info("Reading parquet: {}".format(file_name))
    return spark.read.parquet(file_name)


def write_parquet_data(outpath, data):
    logger.info("Writing parquet: {}".format(outpath))
    data.write.parquet(outpath, mode="overwrite")


def get_frame(file_name):
    logger.info("Reading: {}".format(file_name))
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

    return df


def svd(X, comps):
    svd = X.computeSVD(X.numCols(), computeU=False)
    s = svd.s.toArray()
    V = svd.V.toArray().T
    var = numpy.dot(s[comps:], s[comps:])
    return s[:comps], V[:comps], var


def tilde(X, psi_sqrt, n_sqrt):
    norm = psi_sqrt * n_sqrt
    Xtilde = RowMatrix(X.rows.map(lambda x: x / norm))
    return Xtilde


def process_data(data):
    rdd = data.select(get_feature_columns(data)).rdd.map(list)
    summary = Statistics.colStats(rdd)
    return RowMatrix(rdd), summary.mean(), summary.variance()


def fit(X, var, n_components):
    iter, DELTA, MAX_ITER = 0, 1e-12, 100
    N, P = X.numRows(), X.numCols()

    ll = old_ll = -numpy.inf
    llconst = P * numpy.log(2. * numpy.pi) + n_components
    logliks = []

    psi = numpy.ones(P, dtype=numpy.float64)
    nsqrt = numpy.sqrt(N)

    for i in range(MAX_ITER):
        sqrt_psi = numpy.sqrt(psi) + DELTA
        s, V, unexp_var = svd(tilde(X, sqrt_psi, nsqrt), n_components)
        s = s ** 2
        # factor updated
        W = numpy.sqrt(numpy.maximum(s - 1., 0.))[:, numpy.newaxis] * V
        W *= sqrt_psi
        # loglik update
        ll = llconst + numpy.sum(numpy.log(s))
        ll += unexp_var + numpy.sum(numpy.log(psi))
        ll *= -N / 2.
        logliks.append(ll)

        # variance update
        psi = numpy.maximum(var - numpy.sum(W ** 2, axis=0), DELTA)
        if numpy.abs(ll - old_ll) < 0.001:
            break
        old_ll = ll

    return W, logliks, psi


def transform(X, W, psi):
    Ih = numpy.eye(len(W))
    Wpsi = W / psi
    cov_z = scipy.linalg.inv(Ih + numpy.dot(Wpsi, W.T))
    tmp = numpy.dot(Wpsi.T, cov_z)
    tmp_dense = DenseMatrix(
      numRows=tmp.shape[0], numCols=tmp.shape[1], values=tmp.flatten())

    X = X.multiply(tmp_dense)
    X = spark.createDataFrame(X.rows.map(lambda x: (x,)))
    X = X.withColumnRenamed("_1", "features")

    return X


def fa(file_name, outpath):
    if not pathlib.Path(file_name).is_file():
        logger.error("File doesnt exist: {}".format(file_name))
        return
    if pathlib.Path(outpath).is_file():
        logger.error("Not a path: {}".format(outpath))
        return

    data = get_frame(file_name)
    features = get_feature_columns(data)
    X, means, var = process_data(data)
    X = RowMatrix(X.rows.map(lambda x: x - means))
    W, ll, psi = fit(X, var, 10)
    X = transform(X, W, psi)

    X = X.withColumn('row_index', func.monotonically_increasing_id())
    data = data.withColumn('row_index', func.monotonically_increasing_id())
    data = data.join(X["row_index", "features"],
                     on=["row_index"]).drop("row_index")
    del X

    write_parquet_data(outpath, data)

    W = pandas.DataFrame(data=W)
    W.columns = features
    W.to_csv(outpath + "_factors.tsv", sep="\t", index=False)

    L = pandas.DataFrame(data=ll)
    L.to_csv(outpath + "_likelihood.tsv", sep="\t", index=False)


def run():
    # check files
    file_name, outpath, opts = read_args(sys.argv[1:])
    if not file_name.endswith(".tsv"):
        logger.error("Please provide a tsv file: " + file_name)
        return

    # spark settings
    pyspark.StorageLevel(True, True, False, False, 1)
    conf = pyspark.SparkConf()
    sc = pyspark.SparkContext(conf=conf)
    global spark
    spark = pyspark.sql.SparkSession(sc)

    try:
        fa(file_name, outpath)
    except Exception as e:
        logger.error("Some error: {}".format(str(e)))

    spark.stop()


if __name__ == "__main__":
    run()
