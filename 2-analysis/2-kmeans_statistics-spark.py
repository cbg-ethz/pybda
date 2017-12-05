import argparse
import logging
import sys
import pandas
import pathlib
import pyspark
import numpy

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
    dnts = dnts.select(what + ["count"]).dropDuplicates().toPandas()

    outfile = folder + "_" + "_".join(what) + "_count.tsv"
    logger.info("Writing sample table to: {}".format(outfile))
    write_pandas_tsv(outfile, dnts)


def write_clusters(data, folder):
    file_names = []
    for i in range(5):
        data_i = data.filter("prediction={}".format(i))
        outfile = "{}_{}.tsv".format(folder, i)
        data_i.toPandas().to_csv(outfile, sep="\t", index=0)
    return file_names


def _from(el):
    return numpy.fromstring(el.replace("[", "").replace("]", ""),
                            dtype=numpy.float64, sep=",")


def compute_silhouettes(outfiles):
    K = len(outfiles)
    out_silhouette = outfiles + "silhouette.tsv"
    with open(out_silhouette, "w") as ot:
        ot.write("#Cluster\tSilhouette\n")
        for i in range(K):
            _compute_silhouette(outfiles, i, K, ot)


def _compute_silhouette(outfiles, i, K, ot):
    cnt = 0
    with open(outfiles[i], "r") as f1:
        for l1 in f1.readlines():
            if l1.startswith("study"):
                continue
            if cnt == 10000:
                return
            cnt += 1
            el1 = l1.split("\t")
            f1 = _from(el1[-1])
            min_distance = min(
              [_mean_distance(j, f1, outfiles) for j in range(K) if j != i])
            within_distance = _mean_distance(i, f1, outfiles)
            silhouette = (min_distance - within_distance) / max((min_distance, within_distance))
            ot.write("{}\t{}".format(i, silhouette))


def _mean_distance(j, f1, outfiles):
    distance = 0
    cnt = 0
    with open(outfiles[j], "r") as f2:
        for l2 in f2.readlines():
            if l2.startswith("study"):
                continue
            f2 = _from(l2.split("\t")[-1])
            distance += numpy.sqrt((f1 - f2) ** 2)
            cnt += 1
            if cnt == 10000:
                return distance / cnt
    return distance / cnt


def statistics(folder):
    if not pathlib.Path(folder).is_dir():
        logger.error("Directory doesnt exist: {}".format(folder))
        return

    logger.info("Loading PCA/Kmeans clustering")
    data = read_parquet_data(folder)

    count_statistics(data, folder, ["gene", "prediction"])
    count_statistics(data, folder, ["sirna", "prediction"])
    count_statistics(data, folder, ["pathogen", "prediction"])

    outfile_names = write_clusters(data, folder)
    compute_silhouettes(outfile_names, folder)


def run():
    # check files
    folder, opts = read_args(sys.argv[1:])
    if not pathlib.Path(folder).is_dir():
        logger.error("Folder does not exist: " + folder)
        return

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
    spark.stop()


if __name__ == "__main__":
    run()
