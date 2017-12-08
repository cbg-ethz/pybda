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
    print("\n\n\n\n\n\n")
    print(dnts.count())
    print("\n\n\n\n\n\nn\n")
    #dnts = dnts.toPandas()
    outfile = folder + "_" + "_".join(what) + "_count"
    logger.info("Writing sample table to: {}".format(outfile))
    #write_pandas_tsv(outfile, dnts)
    dnts.write.csv(path=outfile, sep="\t", header=True)


def write_clusters(data, folder, cluster_counts):
    file_names = [""] * len(cluster_counts)
    for i in cluster_counts:
        data_i = data.filter("prediction={}".format(i))
        outfile = "{}_{}.tsv".format(folder, i)
        file_names[i] = outfile
        data_i.toPandas().sample(frac=1).to_csv(outfile, sep="\t", index=0)
    return file_names


def _from(el):
    return numpy.fromstring(el.replace("[", "").replace("]", ""),
                            dtype=numpy.float64, sep=",")


def compute_silhouettes(folder):

    reg = re.compile(".*K\d+\_\d+.tsv")
    files = [x for x in glob.glob(folder+"*") if x.endswith(".tsv")]
    files = [x for x in files if reg.match(x) is not None]
    out_silhouette = folder + "_silhouette.tsv"
    K = len(files)
    with open(out_silhouette, "w") as ot:
        ot.write("#Cluster\tNeighbor\tSilhouette\n")
        for i in range(K):
            _compute_silhouette(files, i, K, ot)


def _compute_silhouette(outfiles, i, K, ot):
    cnt = 0
    print("\n\n\nPURZO\n\n\n")
    with open(outfiles[i], "r") as f1:
        for l1 in f1.readlines():
            if l1.startswith("study"):
                continue
            if cnt == 10000:
                return
            cnt += 1
            el1 = l1.split("\t")
            f1 = _from(el1[-1])
            min_cluster, min_distance = mp_min_distance(i, K, f1, outfiles)
            within_distance = _mean_distance(i, f1, outfiles)
            silhouette = (min_distance - within_distance) / numpy.max(
              (min_distance, within_distance))
            ot.write("{}\t{}\t{}".format(i, min_cluster, silhouette) + "\n")


def mp_min_distance(i, K, f1, outfiles):
    n_cores = mp.cpu_count() - 1
    itr = [j for j in range(K) if j != i]
    p = mp.Pool(n_cores)
    distances = p.map(partial(_mean_distance, f1=f1, outfiles=outfiles), itr)
    p.close()
    p.join()
    arg = itr[numpy.argmin(distances)]
    return arg, distances[arg]


def _mean_distance(j, f1, outfiles):
    distance = 0
    cnt = 0
    with open(outfiles[j], "r") as f2:
        for l2 in f2.readlines():
            if l2.startswith("study"):
                continue
            f2 = _from(l2.split("\t")[-1])
            distance += scipy.spatial.distance.euclidean(f1, f2)
            cnt += 1
            if cnt == 1000:
                return numpy.mean(distance)
    return numpy.mean(distance)


def statistics(folder):
    if not pathlib.Path(folder).is_dir():
        logger.error("Directory doesnt exist: {}".format(folder))
        return

    logger.info("Loading PCA/Kmeans clustering")
    data = read_parquet_data(folder)
    #cluster_counts = numpy.array(
    #    data.select("prediction").dropDuplicates().collect()).flatten()
    
    #count_statistics(data, folder, ["gene", "prediction"])
    #count_statistics(data, folder, ["sirna", "prediction"])
    #count_statistics(data, folder, ["pathogen", "prediction"])
    #count_statistics(data, folder, ["gene", "pathogen", "prediction"])
    #count_statistics(data, folder, ["sirna", "pathogen", "prediction"])
    
    #write_clusters(data, folder, cluster_counts)
    compute_silhouettes(folder)


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
