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

import numpy
import pandas

from koios.globals import WITHIN_VAR_, EXPL_VAR_, TOTAL_VAR_, K_
from koios.plot.cluster_plot import plot_profile, plot_cluster_sizes

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GMMFitProfile:
    def __init__(self, max, models=None):
        self.__maximum = max
        self.__ks = []
        self.__bic_path = []
        self.__models = {} if models is None else models
        self.__loss = numpy.inf

    def __getitem__(self, key):
        return self.__models[key]

    @classmethod
    def as_profilefile(cls, fl):
        if fl.endswith(".tsv"):
            profilefile = fl.replace(".tsv", "-profile.tsv")
        else:
            profilefile = fl + "-profile.tsv"
        return profilefile

    def write_files(self, outpath):
        self._write_variance_path(outpath)
        self._write_cluster_quantiles(outpath)
        self._plot(outpath)

    def _write_variance_path(self, outpath):
        lrt_file = KMeansFitProfile.as_profilefile(outpath)
        logger.info("Writing kmeans fit profile to {}".format(lrt_file))
        with open(lrt_file, "w") as fh:
            fh.write(self._header())
            for el in self.__variance_path:
                fh.write(str(el))

    def _write_cluster_quantiles(self, outpath):
        from koios.io.io import write_tsv
        cs_file = outpath + "-cluster_stats.tsv"
        logger.info("Writing cluster quantiles to {}".format(cs_file))

        data, _ = self._cluster_sizes(outpath)
        data[K_] = data[K_].astype(int)
        data = data.groupby(K_).quantile([0, 0.25, 0.5, 0.75, 1])
        data = data.unstack(K_)["c"]
        data.columns = list(map(lambda x : "K{}".format(x), data.columns))
        data.insert(loc=0,
                    column="quantile",
                    value=list(map(lambda x: x, data.index)))

        write_tsv(data, cs_file, index=False)

    def as_pandas(self):
        df = [None] * len(self.__variance_path)
        for i, e in enumerate(self.__variance_path):
            df[i] = e.values
        return pandas.DataFrame(df)

    def _plot(self, outpath):
        data, labels = self._cluster_sizes(outpath)
        for suf in ["png", "pdf", "svg", "eps"]:
            plot_profile(outpath + "-profile." + suf, self.as_pandas())
            plot_cluster_sizes(
              outpath + "-cluster_sizes-histogram." + suf, data, labels)

    def _cluster_sizes(self, path):
        import glob
        import re

        fls = glob.glob(path + "*/*cluster_sizes.tsv")
        reg = re.compile(".*K(\d+)_cluster_sizes.tsv")
        ll = self.as_pandas()

        frames = [None] * len(fls)
        for i, fl in enumerate(fls):
            t = pandas.read_csv(fl, sep="\t", header=-1, names="c")
            idx = int(reg.match(fl).group(1))
            t[K_] = str(idx).zfill(9)
            frames[i] = [idx, t]

        frames = sorted(frames, key=lambda x: x[0])
        frames = list(filter(lambda x: x[0] in ll["k"].values, frames))

        labels = list(map(lambda x: "K = {}".format(x[0]), frames))
        data = pandas.concat(map(lambda x: x[1], frames))

        return data, labels

    @staticmethod
    def _header():
        return "left_bound\t" \
               "k\t" \
               "right_bound\t" \
               "{}\t".format(WITHIN_VAR_) + \
               "{}\t".format(EXPL_VAR_) + \
               "{}\t".format(TOTAL_VAR_) + \
               "percent_loss\n"

    @property
    def loss(self):
        return self.__loss

    @property
    def current_model(self):
        return self.__models[self.__ks[-1]]

    @property
    def max_model(self):
        if not self.has_max_model():
            return None
        return self.__models[self.__maximum]

    def has_max_model(self):
        return self.__maximum in self.__models.keys()

    def keys(self):
        return self.__models.keys()

    def _loss(self, model):
        if self.has_max_model():
            return 1 - model.explained_variance / self.max_model.explained_variance
        return 1

    def add(self, model, left, k, right):
        self.__ks.append(k)
        self.__models[k] = model
        self.__loss = self._loss(model)
        self.__variance_path.append(
          self.Element(left, k, right, model, self.loss))
        logger.info("Loss for K={} to {}".format(k, self.loss))
        return self

    class Element:
        def __init__(self, left, k, right, model, loss):
            self.__left_boundary = left
            self.__current = k
            self.__right_boundary = right
            self.__K = k
            self.__model = model
            self.__loss = loss

        @property
        def model(self):
            return self.__model

        @property
        def values(self):
            return {
                'left_bound': self.__left_boundary,
                K_: self.__current,
                'right_bound': self.__right_boundary,
                WITHIN_VAR_: self.__model.within_cluster_variance,
                EXPL_VAR_: self.__model.explained_variance,
                TOTAL_VAR_: self.__model.total_variance,
                'percent_loss': self.__loss
            }

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return "{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
              self.__left_boundary,
              self.__current,
              self.__right_boundary,
              self.__model.within_cluster_variance,
              self.__model.explained_variance,
              self.__model.total_variance,
              self.__loss)
