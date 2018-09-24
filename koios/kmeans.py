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
import pathlib

import click
import pandas
import pyspark
import pyspark.ml.clustering

from koios.clustering import Clustering
from koios.globals import TOTAL_VAR_
from koios.io.as_filename import as_ssefile
from koios.io.io import write_line
from koios.kmeans_fit import KMeansFit
from koios.kmeans_fit_profile import KMeansFitProfile
from koios.kmeans_transformed import KMeansTransformed
from koios.util.features import n_features, split_vector
from koios.util.stats import sum_of_squared_errors

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class KMeans(Clustering):
    def __init__(self, spark, clusters, findbest=None,
                 threshold=.01, max_iter=25):
        clusters = list(map(int, clusters.split(",")))
        if findbest and len(clusters) > 1:
            raise ValueError(
              "Cannot find optimal clustering with multiple K."
              "Use only a single K or set findbest=false.")
        if findbest:
            clusters = clusters[0]
        super().__init__(spark, clusters, findbest, threshold, max_iter)

    def fit(self, data, precomputed_models_path=None, outfolder=None):
        if self.findbest:
            return self._fit_recursive(data, precomputed_models_path, outfolder)
        raise ValueError("Not implemented.")

    def transform(self, data, models=None, fit_folder=None):
        if fit_folder is None and models is None:
            raise ValueError("Provide either 'models' or a 'models_folder'")
        if fit_folder:
            fit = KMeansFit.find_best_fit(fit_folder)
        return KMeansTransformed(fit.transform(data))

    def fit_transform(self):
        raise NotImplementedError()

    def _fit_recursive(self, data, precomp_mod_path, outfolder):
        logger.info(
          "Recursively clustering with max K: {}".format(self.clusters))

        n, p = data.count(), n_features(data, "features")
        logger.info("Using data with n={} and p={}".format(n, p))

        data = data.select("features")

        tot_var = self._total_variance(split_vector(data, "features"),
                                       outfolder)

        kmeans_prof = KMeansFitProfile(
          self.clusters, self.load_precomputed_models(precomp_mod_path)) \
            .add(KMeansFit(None, None, 0, tot_var, tot_var, n, p), 0, 0, 0)

        lefts, mids, rights = [], [], []
        left, mid, right = 2, self.clusters, self.clusters

        itr = 0
        while True:
            mids.append(mid)
            lefts.append(left)
            rights.append(right)

            model = self._find_or_fit(
              tot_var, kmeans_prof, mid, n, p, data, outfolder)
            kmeans_prof.add(model, left, mid, right)

            if kmeans_prof.loss < self.threshold:
                mid, right = min(int((left + mid) / 2), self.clusters), mid + 1
            elif kmeans_prof.loss > self.threshold:
                mid, left = int((right + mid) / 2), mid
            if left == lefts[-1] and right == rights[-1]:
                break
            if itr >= self.max_iter:
                logger.info("Breaking")
                break
            itr += 1

        return kmeans_prof

    @staticmethod
    def _total_variance(data, outpath=None):
        if outpath:
            sse_file = as_ssefile(outpath)
        else:
            sse_file = None
        if sse_file and pathlib.Path(sse_file).exists():
            logger.info("Loading variance file")
            tab = pandas.read_csv(sse_file, sep="\t")
            sse = tab[TOTAL_VAR_][0]
        else:
            logger.info("Computing variance anew")
            sse = sum_of_squared_errors(data)
            if sse_file:
                write_line("{}\n{}\n".format(TOTAL_VAR_, sse), sse_file)
        logger.info("\t{}: {}".format(TOTAL_VAR_, sse))
        return sse

    @classmethod
    def load_precomputed_models(cls, precomputed_models):
        mod = {}
        if precomputed_models:
            fls = glob.glob(precomputed_models + "*_statistics.tsv")
        else:
            fls = []
        if fls:
            logger.info("Found precomputed ll-files...")
            for f in fls:
                m = KMeansFit.load_model(f)
                mod[m.K] = m
        else:
            logger.info("Starting from scratch...")
        return mod

    def _find_or_fit(self, total_var, kmeans_prof, k, n, p, data, outfolder):
        if k in kmeans_prof.keys():
            logger.info("Loading model k={}".format(k))
            model = kmeans_prof[k]
        else:
            logger.info("Newly estimating model k={}".format(k))
            model = self._fit(total_var, k, n, p, data, outfolder)
        return model

    @staticmethod
    def _fit(total_var, k, n, p, data, outfolder):
        logger.info("Clustering with K: {}".format(k))
        km = pyspark.ml.clustering.KMeans(k=k, seed=23)
        fit = km.fit(data)
        model = KMeansFit(data=None, fit=fit, k=k,
                          within_cluster_variance=fit.computeCost(data),
                          total_variance=total_var, n=n, p=p, path=None)
        if outfolder:
            model.write_files(outfolder)
        return model


@click.group()
def cli():
    pass


@cli.command()
@click.argument("infolder", type=str)
@click.argument("outfolder", type=str)
@click.argument("clusters", type=str)
@click.option(
  '--findbest',
  is_flag=True,
  help="Flag if clustering should be done recursively to find the best "
       "K for a given number of maximal clusters.")
def fit(infolder, outfolder, clusters, findbest):
    """
    Fit a kmeans-clustering to a data set.
    """

    from koios.io.io import read_parquet
    from koios.io.as_filename import as_logfile
    from koios.logger import set_logger
    from koios.spark_session import SparkSession
    from koios.util.string import drop_suffix

    outfolder = drop_suffix(outfolder, "/")
    set_logger(as_logfile(outfolder))

    with SparkSession() as spark:
        # try:
            km = KMeans(spark, clusters, findbest)
            fit = km.fit(read_parquet(spark, infolder),
                         precomputed_models_path=outfolder,
                         outfolder=outfolder)
            fit.write_variance_path(outfolder)
        # except Exception as e:
        #     logger.error("Some error: {}".format(1))
        #     logger.error(e)


@cli.command()
@click.argument("infolder", type=str)
@click.argument("outfolder", type=str)
@click.option(
  "--clusters",
  type=str,
  default=None,
  help="Comma separated list of number of clusters.")
def transform(infolder, outfolder, clusters):
    """
    Transform a dataset using a kmeans-clustering fit.
    """

    from koios.io.io import read_parquet
    from koios.io.as_filename import as_logfile
    from koios.logger import set_logger
    from koios.spark_session import SparkSession
    from koios.util.string import drop_suffix

    outfolder = drop_suffix(outfolder, "/")
    set_logger(as_logfile(outfolder))

    with SparkSession() as spark:
        try:
            km = KMeans(spark, clusters)
            tr = km.transform(read_parquet(spark, infolder),
                              fit_folder=infolder)
            tr = tr.select(
              "study", "pathogen", "library", "design", "replicate",
              "plate", "well", "gene", "sirna", "well_type",
              "image_idx", "object_idx", "prediction", "features")
            tr.write_files(outfolder)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    cli()
