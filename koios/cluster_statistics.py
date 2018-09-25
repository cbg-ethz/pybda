# Copyright (C) 2018 Simon Dirmeier
#
# This file is part of koios.
#
# koios is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# koios is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with koios. If not, see <http://www.gnu.org/licenses/>.
#
# @author = 'Simon Dirmeier'
# @email = 'simon.dirmeier@bsse.ethz.ch'


import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ClusterStatistics:
    def __init__(self, spark):
        self.__spark = spark

    @staticmethod
    def count_statistics(data, what):
        return (data
                .groupby(what)
                .count()
                .select(what + ["count"])
                .dropDuplicates())


def read_matrices(files):
    logger.info("Reading files into data frame")
    l = [None] * len(files)
    for i, fl in enumerate(files):
        df = pandas.read_csv(
          fl, sep="\t", nrows=1000,
          usecols=lambda x: x.startswith("f_") or x.startswith("pred"))
        l[i] = df
    df = pandas.concat(l)
    sh = df.shape
    logger.info("Read data frame with dimension ({} x {})".format(sh[0], sh[1]))
    return df


def read_matrix(fl):
    return pandas.read_csv(fl, sep="\t", nrows=1000,
                           usecols=lambda x: x.startswith("f_"))


def compute_silhouettes(outfolder):
    start = time.clock()
    out_silhouette = outfolder + "-statistics-silhouette.tsv"
    logger.info("Writing silhouettes to: {}".format(out_silhouette))

    files = [x for x in glob.glob(outfolder + "-clusters/cluster*") \
             if x.endswith(".tsv")]
    K = len(files)
    mat = read_matrices(files)
    with open(out_silhouette, "w") as ot:
        logger.info("Opening file IO")
        ot.write("#Cluster\tNeighbor\tSilhouette\n")
        for current_idx in range(K):
            logger.info("Doing file {}".format(current_idx))
            _compute_silhouette(current_idx, K, ot, mat)
    logger.info("TIme {}".format(time.clock() - start))


def _compute_silhouette(current_idx, K, ot, mat):
    # np_i = read_matrix(outfiles[i])
    min_cluster, min_distance = mp_min_distance(current_idx, K, mat)
    within_distance = _mean_distance(current_idx, current_idx, mat)
    silhouette = (min_distance - within_distance) / \
                 numpy.maximum(min_distance, within_distance)
    for clust, sil in zip(min_cluster, silhouette):
        ot.write("{}\t{}\t{}".format(current_idx, clust, sil) + "\n")


def mp_min_distance(current_idx, K, mat):
    itr = numpy.array([j for j in range(K) if j != current_idx])
    distances = [_mean_distance(it, current_idx, mat) for it in itr]
    distances = numpy.vstack(distances).T
    argmins = numpy.argmin(distances, axis=1)
    min_distances = numpy.min(distances, axis=1)
    arg = itr[argmins]
    return arg, min_distances


def _mean_distance(it, current_idx, df):
    """Computes distances between np array and np_j"""
    # np_j = read_matrix(outfiles[j])
    distances = scipy.spatial.distance.cdist(
      df[df.prediction == current_idx].iloc[:, 1:],
      df[df.prediction == it].iloc[:, 1:])
    return numpy.mean(distances, axis=1)


@click.command()
@click.argument("path", type=int)
def run(path):
    from koios.util.string import drop_suffix
    from koios.logger import set_logger
    from koios.spark_session import SparkSession
    from koios.io.io import read_parquet
    from koios.io.as_filename import as_logfile

    outpath = drop_suffix(path, "/")
    set_logger(as_logfile(path + "-statistics"))

    with SparkSession() as spark:
        try:
            data = read_parquet(spark, path)
            cs = ClusterStatistics(spark)
            gene_pred = cs.count_statistics(data, ["gene", "prediction"])
            path_pred = cs.count_statistics(data, ["pathogen", "prediction"])
            statistics.write_files(outpath)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
