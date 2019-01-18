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


class KMeansFitProfile:
    def __init__(self):
        self.__models = {}

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
        for model in self.__models.values():
            model.write_files(outpath)
        self._write_variance_path(outpath)
        self._plot(outpath)

    def _write_variance_path(self, outpath):
        lrt_file = KMeansFitProfile.as_profilefile(outpath)
        logger.info("Writing kmeans fit profile to {}".format(lrt_file))
        with open(lrt_file, "w") as fh:
            fh.write(self._header())
            for el in self.__variance_path:
                fh.write(str(el))

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
        return "k\t" \
               "{}\t".format(WITHIN_VAR_) + \
               "{}\t".format(EXPL_VAR_) + \
               "{}\t".format(TOTAL_VAR_) + \
               "percent_loss\n"

    def keys(self):
        return self.__models.keys()

    def add(self, k, model):
        self.__models[k] = model
        self.__variance_path.append(self.Element(k, model))
        return self

    class Element:
        def __init__(self, k, model, loss):
            self.__K = k
            self.__model = model

        @property
        def model(self):
            return self.__model

        @property
        def values(self):
            return {
                K_: self.__current,
                WITHIN_VAR_: self.__model.within_cluster_variance,
                EXPL_VAR_: self.__model.explained_variance,
                TOTAL_VAR_: self.__model.total_variance
            }

        def __repr__(self):
            return self.__str__()

        def __str__(self):
            return "\t{}\t{}\t{}\t{}\n".format(
              self.__K,
              self.__model.within_cluster_variance,
              self.__model.explained_variance,
              self.__model.total_variance)
