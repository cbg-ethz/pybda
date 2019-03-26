# Copyright (C) 2018, 2019 Simon Dirmeier
#
# This file is part of pybda.
#
# pybda is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pybda is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pybda. If not, see <http://www.gnu.org/licenses/>.
#
# @author = 'Simon Dirmeier'
# @email = 'simon.dirmeier@bsse.ethz.ch'

import glob
import logging
import re
from abc import ABC, abstractmethod
from collections import OrderedDict

import pandas
import joypy
import numpy
import matplotlib.pyplot as plt

from pybda.globals import K_

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FitProfile(ABC):
    def __init__(self):
        self.__models = OrderedDict()

    def __getitem__(self, key):
        return self.__models[key]

    def __setitem__(self, key, value):
        self.__models[key] = value

    def __iter__(self):
        for k, m in self.models.items():
            yield k, m

    @property
    def models(self):
        return self.__models

    def write(self, outpath):
        self._write_profile(outpath)
        self._plot(outpath)

    def _write_profile(self, outpath):
        lrt_file = FitProfile.as_profilefile(outpath)
        logger.info("Writing fit profile to {}".format(lrt_file))
        with open(lrt_file, "w") as fh:
            is_first = True
            for _, el in self.models.items():
                if is_first:
                    fh.write(el.header())
                    is_first = False
                fh.write(str(el))

    @classmethod
    def as_profilefile(cls, fl):
        if fl.endswith(".tsv"):
            profilefile = fl.replace(".tsv", "-profile.tsv")
        else:
            profilefile = fl + "-profile.tsv"
        return profilefile

    def _cluster_sizes(self, path):
        fls = glob.glob(path + "*/*cluster_sizes.tsv")
        reg = re.compile(r".*K(\d+)_cluster_sizes.tsv")
        ll = self.as_pandas()
        logger.info(len(fls))
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

    def as_pandas(self):
        df = [None] * len(self.models)
        for i, e in enumerate(self.models.values()):
            df[i] = e.values
        return pandas.DataFrame(df)

    @abstractmethod
    def _plot_profile(self, file_name, profile):
        pass

    @staticmethod
    def _plot_cluster_sizes(file_name, data, labels):
        logger.info("Plotting cluster sizes to: {}".format(file_name))
        _, ax = plt.subplots(figsize=(5, 3))
        _, axes = joypy.joyplot(
            data, by=K_, hist="True", ax=ax, bins=50, overlap=0, grid="y",
            color="grey", labels=labels, title="Cluster size distribution")
        for x in axes:
            x.spines['bottom'].set_color('grey')
            x.grid(color="grey", axis="y")
        locs, labels = plt.xticks()
        if any(locs < 0):
            idx = numpy.where(locs < 0)[0]
            for i in idx:
                labels[i].set_text(None)
            plt.xticks(locs, labels)
        plt.savefig(file_name, dpi=720)
        plt.close("all")
