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
import glob
import logging

import click
import scipy
import time

import numpy
import pandas

from koios.io.file import find_by_suffix
from koios.util.stats import sample

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

    @staticmethod
    def _read_matrices(files):
        logger.info("Reading files to data frame")
        tables = [None] * len(files)
        for i, fl in enumerate(files):
            tables[i] = pandas.read_csv(
              fl, sep="\t", nrows=1000,
              usecols=lambda x: x.startswith("f_") or x.startswith("pred"))
        frame = pandas.concat(tables)
        sh = frame.shape
        logger.info("Read data frame of dim ({} x {})".format(sh[0], sh[1]))

        return frame

    def compute_silhouettes(self, path, n=100):
        out_silhouette = path + "-statistics-silhouette.tsv"
        logger.info("Writing silhouette scores to: {}".format(out_silhouette))

        files = sample(find_by_suffix(path + "-clusters/cluster*", "tsv"), n)

        len_f = len(files)
        mat = self._read_matrices(files)
        for current_idx in range(len(files)):
            logger.info("Doing file {}".format(current_idx))
            self._compute_silhouette(current_idx, len_f, mat)

    def _compute_silhouette(self, current_idx, K, mat):
        min_cluster, min_distance = self._mp_min_distance(current_idx, K, mat)
        within_distance = self._mean_distance(current_idx, current_idx, mat)
        silhouette = (min_distance - within_distance) / \
                     numpy.maximum(min_distance, within_distance)
        return zip(min_cluster, silhouette)

    def _mp_min_distance(self, current_idx, K, mat):
        itr = numpy.array([j for j in range(K) if j != current_idx])
        distances = [self._mean_distance(it, current_idx, mat) for it in itr]
        distances = numpy.vstack(distances).T
        argmins = numpy.argmin(distances, axis=1)
        min_distances = numpy.min(distances, axis=1)
        arg = itr[argmins]
        return arg, min_distances

    @staticmethod
    def _mean_distance(it, current_idx, df):
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

    path = drop_suffix(path, "/")
    set_logger(as_logfile(path + "-statistics"))

    with SparkSession() as spark:
        try:
            data = read_parquet(spark, path)
            cs = ClusterStatistics(spark)
            gene_pred = cs.count_statistics(data, ["gene", "prediction"])
            path_pred = cs.count_statistics(data, ["pathogen", "prediction"])
            silhouettes = cs.compute_silhouettes(data)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
