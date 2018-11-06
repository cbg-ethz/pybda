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
from abc import abstractmethod

from koios.globals import GMM__, FEATURES__
from koios.spark.features import n_features, split_vector
from koios.spark_model import SparkModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Clustering(SparkModel):
    def __init__(self, spark, clusters, findbest, threshold, max_iter, kind):
        super().__init__(spark)
        self.__kind = kind
        if kind == GMM__:
            self.__name_components = "components"
            self.__algorithm_type = "mixture"
        else:
            self.__name_components = "clusters"
            self.__algorithm_type = "clustering"
        if clusters is not None and isinstance(clusters, str):
            clusters = list(map(int, clusters.split(",")))
            if findbest and len(clusters) > 1:
                raise ValueError(
                  "Cannot find optimal {} with multiple {}."
                  "Use only a single K or set findbest=false.".format(
                    self.__algorithm_type, self.__name_components))
            if findbest:
                clusters = clusters[0]
        self.__threshold = threshold
        self.__max_iter = max_iter
        self.__clusters = clusters
        self.__findbest = findbest

    @abstractmethod
    def _get_fit_class(self):
        pass

    def load_precomputed_models(self, precomputed_models):
        mod = {}
        if precomputed_models:
            fls = glob.glob(precomputed_models + "/*_statistics.tsv")
        else:
            fls = []
        if fls:
            logger.info("Found precomputed ll-files...")
            for f in fls:
                m = self._get_fit_class.load_model(f)
                mod[m.k] = m
        else:
            logger.info("Starting from scratch...")
        return mod

    @property
    def clusters(self):
        return self.__clusters

    @property
    def findbest(self):
        return self.__findbest

    @property
    def max_iter(self):
        return self.__max_iter

    @property
    def threshold(self):
        return self.__threshold

    @abstractmethod
    def fit_transform(self):
        pass

    def fit(self, data, precomputed_models_path=None, outfolder=None):
        n, p = data.count(), n_features(data, FEATURES__)
        logger.info("Using data with n={} and p={}".format(n, p))
        data = data.select(FEATURES__)
        tots = self._totals(split_vector(data, FEATURES__), outfolder)

        if self.findbest:
            return self._fit_recursive(
              data, n, p, tots, precomputed_models_path, outfolder)
        return self._fit_single(data, n, p, tots, outfolder)

    @abstractmethod
    def _totals(self):
        pass

    def _find_or_fit(self, tots, prof, k, n, p, data, outfolder):
        if k in prof.keys():
            logger.info("Loading model k={}".format(k))
            model = prof[k]
        else:
            logger.info("Newly estimating model k={}".format(k))
            model = self._fit(tots, k, n, p, data, outfolder)
        return model

    @staticmethod
    def _check_transform(models, fit_folder):
        if fit_folder is None and models is None:
            raise ValueError("Provide either 'models' or a 'models_folder'")
