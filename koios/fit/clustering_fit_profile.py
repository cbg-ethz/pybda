
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
# @email = 'simon.dirmeier@bsse.ethz.ch'import glob

import glob
import logging
import re
from abc import ABC
from collections import OrderedDict

import pandas

from koios.globals import K_
from koios.plot.cluster_plot import plot_profile, plot_cluster_sizes

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class FitProfile(ABC):
    def __init__(self):
        self.__models = OrderedDict()

    def __getitem__(self, key):
        return self.__models[key]

    def __setitem__(self, key, value):
        self.__models[key] = value

    @property
    def models(self):
        return self.__models

    def write_files(self, outpath):
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

    def _plot(self, outpath):
        data, labels = self._cluster_sizes(outpath)
        pand = self.as_pandas()
        for suf in ["png", "pdf", "svg", "eps"]:
            plot_profile(outpath + "-profile." + suf, pand)
            plot_cluster_sizes(
              outpath + "-cluster_sizes-histogram." + suf, data, labels)

    def _cluster_sizes(self, path):
        fls = glob.glob(path + "*/*cluster_sizes.tsv")
        reg = re.compile(".*K(\d+)_cluster_sizes.tsv")
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

    def _write_path(self, outpath):
        lrt_file = FitProfile.as_profilefile(outpath)
        logger.info("Writing profile to {}".format(lrt_file))
        with open(lrt_file, "w") as fh:
            fh.write(self._header())
            for el in self.path:
                fh.write(str(el))

