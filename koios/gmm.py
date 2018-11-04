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
import pathlib
import scipy

import click
import pandas
import pyspark
import pyspark.ml.clustering

from koios.clustering import Clustering
from koios.fit.gmm_fit import GMMFit
from koios.fit.gmm_fit_profile import GMMFitProfile
from koios.fit.gmm_transformed import GMMTransformed
from koios.globals import RESPONSIBILITIES__, LOGLIK_, GMM__
from koios.io.as_filename import as_loglikfile
from koios.io.io import write_line
from koios.stats.stats import loglik

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GMM(Clustering):
    def __init__(self, spark, clusters, findbest=None,
                 threshold=scipy.inf, max_iter=25):
        super().__init__(spark, clusters, findbest, threshold, max_iter, GMM__)

    def fit_transform(self):
        raise NotImplementedError()

    def transform(self, data, models=None, fit_folder=None):
        self._check_transform(models, fit_folder)
        fit = GMMFit.find_best_fit(fit_folder)
        return GMMTransformed(fit.transform(data))

    def _totals(self, data, outpath=None):
        if outpath:
            outf = as_loglikfile(outpath)
        else:
            outf = None
        if outf and pathlib.Path(outf).exists():
            logger.info("Loading totals file")
            tab = pandas.read_csv(outf, sep="\t")
            tot = tab[LOGLIK_][0]
        else:
            logger.info("Computing totals anew")
            tot = loglik(data)
            if outf:
                write_line("{}\n{}\n".format(LOGLIK_, tot), outf)
        logger.info("\t{}: {}".format(LOGLIK_, tot))
        return tot

    def _fit_recursive(self, data, n, p, tots, precomp_mod_path, outfolder):
        logger.info("Clustering with max K: {}".format(self.clusters))
        prof = GMMFitProfile(
          self.clusters, self.load_precomputed_models(precomp_mod_path))
        prof.add(GMMFit(None, None, 0, None, None, tots, tots, n, p), 0, 0, 0)
        lefts, mids, rights = [], [], []
        left, mid, right = 2, self.clusters, self.clusters

        itr = 0
        while True:
            mids.append(mid)
            lefts.append(left)
            rights.append(right)

            model = self._find_or_fit(tots, prof, mid, n, p, data, outfolder)
            prof.add(model, left, mid, right)

            # TODO: the clustering should return the maximal number
            # if the threshold is not passed and not the number 1 below
            # i.e. maybe it's better to take the ceil not the floor
            # change to LAST MODEL seen
            if prof.loss <= prof.last_loss:
                mid, left = int((right + mid) / 2), mid + 1
            elif prof.loss > prof.last_loss:
                mid, right = min(int((left + mid) / 2),
                                 self.clusters), mid + 1
            if left == lefts[-1] and right == rights[-1] and mid == mids[-1]:
                break
            if itr >= self.max_iter:
                logger.info("Breaking")
                break
            itr += 1

        return prof

    def _fit_single(self, data, n, p, tots, outfolder=None):
        logger.info("Clustering with max K: {}".format(self.clusters))

        prof = GMMFitProfile(scipy.max(self.clusters))
        prof.add(GMMFit(None, None, 0, None, None, tots, tots, n, p), 0, 0, 0)
        for cluster in self.clusters:
            model = self._fit(tots, cluster, n, p, data, outfolder)
            prof.add(model, cluster, cluster, cluster)
        return prof

    @property
    def _get_fit_class(self):
        return GMMFit

    @staticmethod
    def _fit(null_loglik, k, n, p, data, outfolder=None):
        logger.info("Clustering with K: {}".format(k))
        km = pyspark.ml.clustering.GaussianMixture(
          k=k, seed=23, probabilityCol=RESPONSIBILITIES__)
        fit = km.fit(data)
        model = GMMFit(data=None,
                       fit=fit,
                       k=k,
                       mixing_weights=fit.weights,
                       estimates=fit.gaussiansDF,
                       loglik=fit.summary.logLikelihood,
                       null_loglik=null_loglik,
                       n=n, p=p, path=None)
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
    Fit a gmm to a data set.
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
            km = GMM(spark, clusters, findbest)
            fit = km.fit(read_parquet(spark, infolder),
                         precomputed_models_path=outfolder,
                         outfolder=outfolder)
            fit.write_files(outfolder)
        except Exception as e:
            logger.error("Some error: {}".format(e))


@cli.command()
@click.argument("infolder", type=str)
@click.argument("fitfolder", type=str)
@click.argument("outfolder", type=str)
def transform(infolder, fitfolder, outfolder):
    """
    Transform a dataset using a gmm fit.
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
            km = GMM(spark, None)
            tr = km.transform(read_parquet(spark, infolder),
                              fit_folder=fitfolder)
            tr.data = tr.data.select(
              "study", "pathogen", "library", "design", "replicate",
              "plate", "well", "gene", "sirna", "well_type",
              "image_idx", "object_idx", "prediction", "features")
            tr.write_files(outfolder)
        except Exception as e:
            logger.error("Some error: {}".format(str(e)))


if __name__ == "__main__":
    cli()
