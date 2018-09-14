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

from koios.clustering import Clustering
from koios.explained_variance import ExplainedVariance
from koios.io.as_filename import as_ssefile
from koios.io.io import write_line
from koios.kmeans_fit import KMeansFit
from koios.util.features import n_features, split_vector
from koios.util.stats import sum_of_squared_errors

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

WITHIN_CLUSTER_VARIANCE = "within_cluster_variance"
TOTAL_VARIANCE = "total_variance"
EXPLAINED_VARIANCE = "explained_variance"


class KMeans(Clustering):
    def __init__(self, spark, clusters, recursive, threshold=.01, max_iter=25):
        super.__init__(spark, clusters, recursive, threshold, max_iter)

    def fit(self, data, precomputed_models_path=None):
        if self.do_recursive:
            self._fit_recursive(data, precomputed_models_path)

    def _fit_recursive(self, data, precomp_mod_path):
        logger.info(
          "Recursively clustering with max K: {}".format(self.clusters))

        n, p = data.count(), n_features(data, "features")
        logger.info("Using data with n={} and p={}".format(n, p))

        models = self.load_precomputed_models(precomp_mod_path)
        tot_var = self._total_variance(
          split_vector(data, "features"), precomp_mod_path)

        lefts, mids, rights, lrts = [], [], [], []
        left, mid, right = 2, self.clusters, self.clusters
        mid = int((left + right) / 2)

        model_max = self._find_or_fit(
          tot_var, models, right, n, p, data, precomp_mod_path)
        lrts, _ = self._append_lrt(
          lrts, left, self.K, self.K, self.K, model_max, model_max, tot_var)

        itr = 0
        while True:
            mids.append(mid)
            lefts.append(left)
            rights.append(right)

            m_mod = self._find_or_fit(
              tot_var, models, mid, n, p, data, precomp_mod_path)
            lrts, improved_variance = self._append_lrt(
              lrts, left, mid, right, self.K, model_max, m_mod, tot_var)

            if improved_variance < self.threshold:
                mid, right = int((left + mid) / 2), mid + 1
            elif improved_variance > self.threshold:
                mid, left = int((right + mid) / 2), mid
            if left == lefts[-1] and right == rights[-1]:
                break
            if itr >= self.max_iter:
                logger.info("Breaking")
                break
            itr += 1

        return lrts

    def _append_lrt(self, lrts, left, mid, right, K_max, model_max, model, tot_var):
        improved_variance = 1 - model[EXPLAINED_VARIANCE] / model_max[EXPLAINED_VARIANCE]
        lrts.append(
          ExplainedVariance(
            left, mid, right, K_max,
            model_max[EXPLAINED_VARIANCE], model[EXPLAINED_VARIANCE],
            model_max[TOTAL_VARIANCE], model[TOTAL_VARIANCE],
            tot_var, improved_variance))
        logger.info("Variance reduction for K={} to {}"
                    .format(mid, improved_variance))
        return lrts, improved_variance

    @staticmethod
    def _total_variance(data, outpath=None):
        """
        Computes the sum of squared errors of the dataset
        """

        if outpath:
            sse_file = as_ssefile(outpath)
        else:
            sse_file = None
        if sse_file and pathlib.Path(sse_file).exists():
            logger.info("Loading variance file")
            tab = pandas.read_csv(sse_file, sep="\t")
            sse = tab[TOTAL_VARIANCE][0]
        else:
            sse = sum_of_squared_errors(data)
            if sse_file:
                write_line("{}\n{}\n".format(TOTAL_VARIANCE, sse), sse_file)
        logger.info("\t{}: {}".format(TOTAL_VARIANCE, sse))
        return sse

    @staticmethod
    def _cluster(data, k, sse, n, p):
        km = pyspark.ml.clustering.KMeans(k=k, seed=23)
        fit = km.fit(data)
        model = KMeansFit(data=None, fit=fit, k=k,
                          within_cluster_variance=fit.computeCost(data),
                          total_variance=sse, n=n, p=p)
        return model

    def _fit(self, total_sse, k, n, p, data, outpath):
        logger.info("Clustering with K: {}".format(k))

        model = self._cluster(data, k, total_sse, n, p)
        model.write_files(outpath)

        return {WITHIN_CLUSTER_VARIANCE: model.within_cluster_variance,
                EXPLAINED_VARIANCE: model.explained_variance}

    @classmethod
    def load_precomputed_models(cls, precomputed_models):
        mod = {}
        if precomputed_models:
            fls = glob.glob(precomputed_models + "*_loglik.tsv")
        else:
            fls = []
        if fls:
            logger.info("Found precomputed ll-files...")
            for f in fls:
                tab = pandas.read_csv(f, sep="\t")
                within_ss = tab[WITHIN_CLUSTER_VARIANCE][0]
                expl = tab[EXPLAINED_VARIANCE][0]
                k, p = tab["K"][0], tab["P"][0]
                logger.info("\tusing k={}, p={}, within_cluster_variance={}, "
                            "explained_variance={} from {}"
                            .format(k, p, within_ss, expl, f))
                mod[k] = {WITHIN_CLUSTER_VARIANCE: within_ss,
                          EXPLAINED_VARIANCE: expl}
        else:
            logger.info("Starting from scratch...")
        return mod

    def _find_or_fit(self, total_sse, mods, k, n, p, data, outpath):
        if k in mods.keys():
            logger.info("Loading model k={}".format(k))
            model = mods[k]
        else:
            logger.info("Newly estimating model k={}".format(k))
            model = self._fit(total_sse, k, n, p, data, outpath)
            mods[k] = model
        return model

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


@click.command()
@click.argument("infolder", type=str)
@click.argument("outfolder", type=str)
@click.argument("clusters", type=int)
@click.option(
  '--recursive',
  is_flag=True,
  help="Flag if clustering should be done recursively to find the best K.")
def run(infolder, outfolder, clusters, recursive):
    from koios.util.string import drop_suffix
    from koios.logger import set_logger
    from koios.spark_session import SparkSession
    from koios.io.io import read_parquet
    from koios.io.as_filename import as_logfile

    outfolder = drop_suffix(outfolder, "/")
    set_logger(as_logfile(outfolder))

    with SparkSession() as spark:
        try:
            km = KMeans(spark, clusters, recursive)
            fit = km.fit(read_parquet(spark, infolder),
                         precomputed_models_path=outfolder)
            fit.write_files(outfolder)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    run()
