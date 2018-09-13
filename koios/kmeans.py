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
import matplotlib
import pandas
import scipy
import scipy.stats

from koios.clustering import Clustering
from koios.io.as_filename import as_ssefile
from koios.util.features import n_features, split_vector
from koios.util.stats import sum_of_squared_errors

matplotlib.use('Agg')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ExplainedVariance:
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


class KMeans(Clustering):
    def __init__(self, spark, clusters, recursive, threshold=.01, max_iter=25):
        super.__init__(spark, clusters, recursive, threshold, max_iter)

    def fit(self, data, precomputed_models_path=None):
        if self.do_recursive:
            self._fit_recursive(data, precomputed_models_path)

    def _fit_recursive(self, data, precomputed_models_path):
        logger.info(
          "Recursively clustering with a maximal K: {}".format(self.clusters))

        n, p = data.count(), n_features(data, "features")
        logger.info("Using data with n={} and p={}".format(n, p))

        lefts, mids, rights = [], [], []
        left, right = 2, self.clusters
        mid = int((left + right) / 2)

        mods = self.load_precomputed_models(precomputed_models_path)
        total_sse = self._sse(split_vector(data, "features"),
                              precomputed_models_path)

        lrts = []
        K_mod = self._estimate_model(total_sse, mods, right, n, p, data,
                                     precomputed_models_path)
        lrts.append(
          ExplainedVariance(
            left, K, K, K,
            K_mod['expl'], K_mod['expl'], K_mod["sse"], K_mod['sse'],
            total_sse, improved_variance))
        itr = 0

        while True:
            mids.append(mid)
            lefts.append(left)
            rights.append(right)

            m_mod = self.estimate_model(total_sse, mods, mid, n, p, data,
                                        outpath)

            improved_variance = 1 - m_mod['expl'] / K_mod['expl']
            lrts.append(
              ExplainedVariance(
                left, mid, right, K,
                K_mod['expl'], m_mod['expl'], K_mod["sse"], m_mod['sse'],
                total_sse, improved_variance))
            logger.info("\tVariance reduction for K={} to {}"
                        .format(mid, improved_variance))

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

    def k_fit_path(self, outpath, k):
        return outpath + "-K{}".format(k)

    @staticmethod
    def _sse(data, outpath=None):
        """
        Computes the sum of squared errors of the dataset
        """

        if outpath:
            sse_file = as_ssefile(outpath)
        else:
            sse_file = None
        if outpath and pathlib.Path(sse_file).exists():
            logger.info("Loading SSE file")
            tab = pandas.read_csv(sse_file, sep="\t")
            sse = tab["SSE"][0]
        else:
            sse = sum_of_squared_errors(data)
        logger.info("\tSSE: {}".format(sse))
        return sse

    def _estimate_model(self, total_sse, k, n, p, data, outpath):
        logger.info("\tclustering with K: {}".format(k))
        km = KMeans(k=k, seed=23)
        model = km.fit(data)

        clustout = self._k_fit_path(outpath, k)
        logger.info("\twriting cluster fit to: {}".format(clustout))
        model.write().overwrite().save(clustout)

        comp_files = clustout + "_cluster_sizes.tsv"
        logger.info("\twriting cluster size file to: {}".format(comp_files))
        with open(clustout + "_cluster_sizes.tsv", 'w') as fh:
            for c in model.summary.clusterSizes:
                fh.write("{}\n".format(c))

        ccf = clustout + "_cluster_centers.tsv"
        logger.info("\tWriting cluster centers to: {}".format(ccf))
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

    @classmethod
    def load_precomputed_models(cls, precomputed_models):

        mod = {}
        if precomputed_models is not None:
            fls = glob.glob(precomputed_models + "*_loglik.tsv")
        else:
            fls = []
        if fls:
            logger.info("Found precomputed ll-files.")
            for f in fls:
                tab = pandas.read_csv(f, sep="\t")
                sse, expl = tab["SSE"][0], tab["ExplainedVariance"][0]
                k, p = tab["K"][0], tab["P"][0]
                logger.info("\tusing k={}, p={}, sse={}, expl={} from {}"
                            .format(k, p, sse, expl, f))
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
    from koios.io.io import read_parquet, as_logfile

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
