# Copyright (C) 2018 Simon Dirmeier
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

import logging
from abc import ABC, abstractmethod
from collections import OrderedDict

import pandas
import joypy
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

    @abstractmethod
    def _cluster_sizes(self):
        pass

    def as_pandas(self):
        df = [None] * len(self.models)
        for i, e in enumerate(self.models.values()):
            df[i] = e.values
        return pandas.DataFrame(df)

    @abstractmethod
    def _plot_profile(self, outpath, data):
        pass

    def _plot_cluster_sizes(self, file_name, data, labels):
        logger.info("Plotting cluster sizes to: {}".format(file_name))
        _, ax = plt.subplots(figsize=(5, 3))
        _, axes = joypy.joyplot(
            data, by=K_, hist="True", ax=ax, bins=50, overlap=0, grid="y",
            color="grey", labels=labels, title="Cluster size distribution")
        for x in axes:
            x.spines['bottom'].set_color('grey')
            x.grid(color="grey", axis="y")
        plt.savefig(file_name, dpi=720)
        plt.close("all")
